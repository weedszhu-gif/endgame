from common.get_config_from_yaml import get_config
import redis
import os

# db 0: celery
# db 1: yach stream massage
# db 2: api middleware
# db 3: sw config record


class REDIS:

    def __init__(self):
        self.redis_config = get_config()["redis"]
        self.redis_config["host"] = os.getenv(
            "EXTERNAL_HOST_IP", self.redis_config["host"]
        )

    @property
    def redis_url(self):
        return (
            "redis://default:"
            + self.redis_config["password"]
            + "@"
            + self.redis_config["host"]
            + ":"
            + self.redis_config["port"]
            + "/"
            + self.redis_config["db"]
        )

    def client(self, db=None):
        if db is None:
            db = 0
        return redis.Redis(
            host=self.redis_config["host"],
            port=self.redis_config["port"],
            db=db,
            password=self.redis_config["password"],
        )

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)
