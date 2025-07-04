import pymongo
from pymongo.collection import Collection

from .cache import CacheDB
from .metric import MetricsDB
from .playlist import PlaylistsDB
from .setup import SetupDB
from .star import StarsDB
from .user import UsersDB

mongoclient = pymongo.MongoClient("mongodb://database:27017/")
db = mongoclient["debug"]


class Database:
    """Основной класс базы"""

    def __init__(self) -> None:
        self.db = db

        self._setup = SetupDB(self.db["guilds"])
        self._playlists = PlaylistsDB(self.db["playlists"])
        self._stars = StarsDB(self.db["stars"])
        self._users = UsersDB(self.db["users"])
        self._metrics = MetricsDB(self.db["metrics"])
        self._cache = CacheDB(self.db["cache"])

    @property
    def setup(self):
        """Таблица с настройками"""
        return self._setup

    @property
    def playlists(self):
        """Таблица с плейлистами"""
        return self._playlists

    @property
    def stars(self):
        """Таблица с избранным"""
        return self._stars

    @property
    def users(self):
        """Таблица с юзерами"""
        return self._users

    @property
    def metrics(self):
        """Таблица с метриками"""
        return self._metrics

    @property
    def cache(self):
        """Таблица с кэшем"""
        return self._cache

    def table(self, name: str) -> Collection:
        return self.db[name]
