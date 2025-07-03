from pymongo.collection import Collection


class MetricsDB:
    """DB["metrics"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def get_metric(self, id: int, without_id: bool = True):
        """Получить метрику"""
        result = self.table.find_one({"id": id})
        if without_id and result:
            del result["_id"]
        return result

    def add_last_track(self, track: dict, id: int):
        """Добавить последний прослушанный трек"""
        self.table.update_one(
            {"id": id},
            {"$push": {"last_tracks": {"$each": [track], "$slice": -5}}},
            upsert=True,
        ).modified_count.__bool__()
