from pymongo.collection import Collection


class StarsDB:
    """DB["stars"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def get_stars(self, id: int, without_id: bool = True):
        """Запись со звездочками"""
        result = self.table.find_one({"user_id": id})
        if without_id and result:
            del result["_id"]
        return result

    def add_to_stars(self, id: int, track_or_list: dict | list):
        """Добавить в звездочки"""
        stars = self.table.find_one({"user_id": id})
        if (
            stars
            and len(stars.get("tracks", []))
            + (1 if type(track_or_list) == dict else len(track_or_list))
            <= 1000
        ):
            track = (
                track_or_list
                if type(track_or_list) == dict
                else {"$each": track_or_list}
            )
            return self.table.update_one(
                {"user_id": id}, {"$addToSet": {"tracks": track}}, upsert=True
            ).modified_count.__bool__()

    def remove_from_stars(self, track_url: str, id: int):
        """Удалить из звездочек"""
        return self.table.update_one(
            {"user_id": id}, {"$pull": {f"tracks": {"url": track_url}}}
        ).modified_count.__bool__()

    def move_track(self, url: str, pos: int, id: int):
        """Переместить трек на новую позицию"""
        stars: dict = self.table.find_one({"user_id": id})
        if not stars or not stars.get("tracks"):
            return
        track = next(track for track in stars["tracks"] if track.get("url") == url)
        self.table.update_one({"user_id": id}, {"$pull": {f"tracks": {"url": url}}})
        return self.table.update_one(
            {"user_id": id}, {"$push": {"tracks": {"$each": [track], "$position": pos}}}
        ).modified_count.__bool__()
