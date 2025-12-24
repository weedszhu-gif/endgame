from config._redis import REDIS
from config.mysql import MYSQL


class Config:

    def __init__(self):
        self.__redis = REDIS()
        self.__mysql = MYSQL()

    @property
    def redis(self):
        return self.__redis

    @property
    def mysql(self):
        return self.__mysql
