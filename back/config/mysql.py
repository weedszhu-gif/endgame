from common.get_config_from_yaml import get_config
import pymysql
import os
import time
import threading
from pymysql import MySQLError
from pymysql.cursors import DictCursor
from queue import Queue, Empty


class PooledConnection:
    """A proxy connection that returns the real connection back to the pool on close."""

    def __init__(self, real_connection, pool):
        self._real_connection = real_connection
        self._pool = pool
        self._returned = False

    def close(self):
        if self._returned:
            return
        try:
            # Ensure the connection is still valid before returning to pool
            try:
                self._real_connection.ping(reconnect=True)
            except Exception:
                # If ping fails, drop this connection
                try:
                    self._real_connection.close()
                except Exception:
                    pass
                self._pool._decrease_connection_count()
                self._returned = True
                return

            # Return to pool (may be closed by pool if over maxcached)
            self._pool._return_connection(self._real_connection)
        finally:
            self._returned = True

    # Delegate all other attributes/methods to the real connection
    def __getattr__(self, name):
        return getattr(self._real_connection, name)


class SimpleConnectionPool:

    def __init__(
        self,
        creator,
        maxconnections=15,
        mincached=2,
        maxcached=5,
        maxshared=3,  # kept for compatibility, not used
        blocking=True,
        maxusage=None,  # kept for compatibility, not used
        setsession=None,
        ping=1,
        **conn_kwargs,
    ):
        self._creator = creator
        self._conn_kwargs = conn_kwargs
        self._blocking = blocking
        self._ping = ping
        self._mincached = max(0, int(mincached or 0))
        self._maxcached = max(1, int(maxcached or 1))
        self._maxconnections = max(1, int(maxconnections or 1))

        self._pool = Queue(maxsize=self._maxcached)
        self._current_connection_count = 0
        self._count_lock = threading.Lock()

        if setsession:
            self._conn_kwargs.setdefault("init_command", "; ".join(setsession))

        # Pre-create initial cached connections
        for _ in range(min(self._mincached, self._maxconnections)):
            conn = self._create_new_connection()
            if conn is not None:
                self._pool.put(conn)

    def _create_new_connection(self):
        with self._count_lock:
            if self._current_connection_count >= self._maxconnections:
                return None
            try:
                conn = self._creator.connect(**self._conn_kwargs)
                self._current_connection_count += 1
                return conn
            except Exception:
                raise

    def _decrease_connection_count(self):
        with self._count_lock:
            if self._current_connection_count > 0:
                self._current_connection_count -= 1

    def _return_connection(self, conn):
        # If pool is full beyond maxcached, close and drop this connection
        if self._pool.full():
            try:
                conn.close()
            finally:
                self._decrease_connection_count()
        else:
            try:
                self._pool.put_nowait(conn)
            except Exception:
                try:
                    conn.close()
                finally:
                    self._decrease_connection_count()

    def connection(self):
        """Get a pooled connection. Caller should call .close() to return it to the pool."""
        # Try to take one from the pool
        try:
            conn = self._pool.get_nowait()
        except Empty:
            # Try to create a new one if we are under maxconnections
            conn = self._create_new_connection()
            if conn is None:
                if not self._blocking:
                    raise MySQLError("No available connections and blocking is False")
                # Block until a connection is returned
                conn = self._pool.get()

        # Validate connection if ping policy requires
        try:
            if self._ping:
                conn.ping(reconnect=True)
        except Exception:
            # Drop and create a new one if possible, otherwise block/wait
            try:
                conn.close()
            except Exception:
                pass
            self._decrease_connection_count()
            conn = self._create_new_connection()
            if conn is None:
                if not self._blocking:
                    raise MySQLError(
                        "Failed to create a new connection after ping failure"
                    )
                conn = self._pool.get()

        return PooledConnection(conn, self)


class MYSQL:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MYSQL, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db=None):
        if self._initialized:
            return

        config = get_config()
        self.__mysql_ip = os.getenv("EXTERNAL_HOST_IP", config["mysql"]["host"])
        self.__mysql_port = config["mysql"]["port"]
        self.__mysql_username = config["mysql"]["username"]
        self.__mysql_password = config["mysql"]["password"]
        if db is None:
            self.__mysql_database = config["mysql"]["db"]
        else:
            self.__mysql_database = db

        # 连接池配置
        self.pool_config = {
            "creator": pymysql,
            "host": self.__mysql_ip,
            "port": self.__mysql_port,
            "user": self.__mysql_username,
            "password": self.__mysql_password,
            "database": self.__mysql_database,
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.Cursor,
            "maxconnections": 15,  # 最大连接数
            "mincached": 2,  # 初始化时，链接池中至少创建的空闲的链接
            "maxcached": 5,  # 链接池中最多闲置的链接
            "maxshared": 3,  # 链接池中最多共享的链接数量
            "blocking": True,  # 连接池中如果没有可用连接后，是否阻塞等待
            "maxusage": None,  # 一个链接最多被重复使用的次数，None表示无限制
            "setsession": [],  # 开始会话前执行的命令列表
            "ping": 1,  # ping MySQL服务器检查连接是否有效，1表示每次请求前都ping
        }

        # 创建连接池（自实现）
        self.pool = SimpleConnectionPool(**self.pool_config)

        # 连接有效期设置（秒）
        self.connection_lifetime = 3600  # 1小时

        # 记录连接创建时间
        self.connection_time = None

        # 初始化标志
        self._initialized = True

    @property
    def host(self):
        return self.__mysql_ip

    @property
    def port(self):
        return self.__mysql_port

    @property
    def username(self):
        return self.__mysql_username

    @property
    def password(self):
        return self.__mysql_password

    def _get_connection(self):
        """从连接池获取连接"""
        try:
            conn = self.pool.connection()
            # 记录连接获取时间
            self.connection_time = time.time()
            return conn
        except MySQLError as e:
            # 记录错误
            print(f"获取数据库连接失败: {e}")
            raise

    def _check_connection(self, conn):
        """检查连接是否有效，如果无效则重新获取"""
        try:
            # 检查连接是否已过期
            if self.connection_time and (
                time.time() - self.connection_time > self.connection_lifetime
            ):
                conn.close()
                conn = self._get_connection()
                return conn

            # 检查连接是否仍然活跃
            conn.ping(reconnect=True)
            return conn
        except MySQLError:
            # 如果ping失败，关闭旧连接并获取新连接
            try:
                conn.close()
            except:
                pass
            return self._get_connection()

    def connect(self, cursorclass=pymysql.cursors.Cursor):
        """获取数据库连接"""
        try:
            self.conn = self._get_connection()
            self.cursor = self.conn.cursor(cursorclass)
            return True
        except MySQLError as e:
            print(f"连接数据库失败: {e}")
            return False

    def insert_sql(self, sql):
        """写入数据库"""
        try:
            # 检查连接是否有效
            self.conn = self._check_connection(self.conn)
            self.cursor = self.conn.cursor()

            # 执行SQL
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.lastrowid
        except MySQLError as e:
            # 发生错误时回滚
            try:
                self.conn.rollback()
            except:
                pass
            print(f"执行SQL失败: {e}")
            raise

    def insert_sql_many(self, sql, data):
        """批量写入数据库"""
        try:
            # 检查连接是否有效
            self.conn = self._check_connection(self.conn)
            self.cursor = self.conn.cursor()

            # 执行SQL
            self.cursor.executemany(sql, data)
            self.conn.commit()
            return self.cursor.lastrowid
        except MySQLError as e:
            # 发生错误时回滚
            try:
                self.conn.rollback()
            except:
                pass
            print(f"批量执行SQL失败: {e}")
            raise

    def return_sql_result(self, sql):
        """查询数据库"""
        try:
            # 检查连接是否有效
            self.conn = self._check_connection(self.conn)
            self.cursor = self.conn.cursor()

            # 执行查询
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except MySQLError as e:
            print(f"查询SQL失败: {e}")
            raise

    def close_conn(self):
        """关闭连接（实际上是将连接返回给连接池）"""
        try:
            if hasattr(self, "cursor") and self.cursor:
                self.cursor.close()
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
        except MySQLError as e:
            print(f"关闭连接失败: {e}")
