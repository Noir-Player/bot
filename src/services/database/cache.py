import datetime

from pymongo import ASCENDING
from pymongo.collection import Collection


class CacheDB:
    """DB["cache"]"""

    def __init__(self, table: Collection):
        self.table = table

        self.table.create_index([("expireAt", ASCENDING)], expireAfterSeconds=0)

    def col(self) -> Collection:
        return self.table

    def get(self, id: int):
        """Получить запись с кэшем"""
        return self.table.find_one({"id": int(id)})

    def set(
        self,
        info: dict,
        id: int,
        expireAt: datetime.timedelta = None,
    ):
        """Установить / обновить кэш"""
        info["expireAt"] = datetime.datetime.utcnow() + (
            expireAt or datetime.timedelta(days=7)
        )

        return self.table.update_one(
            {"id": int(id)},
            {"$set": info},
            upsert=True,
        ).modified_count.__bool__()

    def push(self, info: dict, id: int):
        """Добавить к списку"""
        return self.table.update_one(
            {"id": int(id)},
            {"$addToSet": info},
            upsert=True,
        ).modified_count.__bool__()

    def clear(self, id: int):
        """Очистить кэш"""
        return self.table.delete_one({"id": int(id)})
