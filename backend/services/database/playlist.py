import re
import uuid

from pymongo.collection import Collection


class PlaylistsDB:
    """DB["playlists"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def find(self, query: dict, without_id: bool = True) -> list[dict]:
        """Найти плейлисты"""
        result, playlists = (
            self.table.find({"title": {"$regex": re.compile(query)}}),
            [],
        )
        for playlist in result:
            if without_id:
                del playlist["_id"]
            playlists.append(playlist)
        return playlists

    def get_playlist(self, uuid: str, without_id: bool = True) -> dict | None:
        """Найти плейлист"""
        result = self.table.find_one({"uuid": uuid})
        if without_id and result:
            del result["_id"]
        return result

    def get_user_playlists(self, id: int, include_forked: bool = True) -> dict | None:
        """Получить плейлисты пользователя. `include_forked` определяет, включать ли плейлисты других пользователей."""
        return [
            playlist
            for playlist in self.table.find(
                {"$or": [{"author.id": id}, {"forked": {"$elemMatch": {"$eq": id}}}]}
                if include_forked
                else {"author.id": id}
            )
        ]

    def add_to_library(self, uuid: str, id: int):
        """Добавить плейлист в библиотеку"""
        return self.table.update_one(
            {"uuid": uuid}, {"$addToSet": {"forked": id}}
        ).modified_count.__bool__()

    def delete_playlist(self, uuid: str, id: int):
        """Удалить плейлист (из библиотеки или перманентно)"""
        playlist: dict = self.table.find_one({"uuid": uuid})
        if not playlist:
            return
        if playlist.get("author").get("id") == id and playlist.get("uuid") == uuid:
            return self.table.delete_one({"uuid": uuid}).deleted_count.__bool__()

        elif id in playlist.get("forked") and playlist.get("uuid") == uuid:
            return self.table.update_one(
                {"uuid": uuid}, {"$pull": {"forked": id}}
            ).modified_count.__bool__()

    def create_playlist(
        self,
        id: int,
        name: str,
        title: str,
        thumbnail: str,
        description: str,
        public: bool,
        tracks: list = [],
        **kwargs,
    ) -> str | None:
        """Создать плейлист"""
        _uuid = str(uuid.uuid4())

        if (
            not self.table.find_one({"title": title})
            and self.table.count_documents({"author.id": id}) <= 5
            and title
        ):
            self.table.insert_one(
                {
                    "uuid": _uuid,
                    "title": title,
                    "thumbnail": thumbnail,
                    "description": description,
                    "public": public,
                    "author": {"id": id, "name": name},
                    "tracks": tracks,
                }
            )
            return _uuid

    def edit_playlist(
        self,
        uuid: str,
        id: int,
        title: str = None,
        thumbnail: str = None,
        description: str = None,
        public: bool = False,
        **kwargs,
    ):
        """Изменить плейлист по uuid"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})
        if not playlist:
            return

        return self.table.update_one(
            {"uuid": playlist.get("uuid")},
            {
                "$set": {
                    "title": title or playlist.get("title"),
                    "thumbnail": thumbnail or playlist.get("thumbnail"),
                    "description": description or playlist.get("description"),
                    "public": public,
                }
            },
        ).modified_count.__bool__()

    def remove_from_playlist(self, uuid: str, id: int, url: str):
        """Удалить трек из плейлиста по uuid и url трека"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})
        if not playlist:
            return
        else:
            return self.table.update_one(
                {"uuid": uuid}, {"$pull": {f"tracks": {"url": url}}}
            ).modified_count.__bool__()

    def add_to_playlist(self, uuid: str, id: int, track: dict):
        """Добавить трек в плейлист"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})

        if not playlist or len(playlist.get("tracks", [])) >= 500:
            return

        return self.table.update_one(
            {"uuid": playlist.get("uuid")}, {"$push": {"tracks": track}}
        ).modified_count.__bool__()

    def merge_playlists(self, uuid1: str, uuid2: str, id: int):
        """Слить треки из плейлиста `uuid1` в `uuid2`"""
        playlist: dict = self.table.find_one({"uuid": uuid1})
        merge: dict = self.table.find_one({"uuid": uuid2, "author.id": id})

        if not playlist or not merge or len(merge.get("tracks", [])) > 500:
            return

        return self.table.update_one(
            {"uuid": merge.get("uuid")},
            {"$addToSet": {"tracks": {"$each": playlist.get("tracks", [])}}},
        ).modified_count.__bool__()

    def move_track(self, uuid: int, url: str, pos: int, id: int):
        """Переместить трек на новую позицию"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})
        if not playlist:
            return
        track = next(track for track in playlist["tracks"] if track.get("url") == url)
        self.table.update_one({"uuid": uuid}, {"$pull": {f"tracks": {"url": url}}})
        return self.table.update_one(
            {"uuid": uuid}, {"$push": {"tracks": {"$each": [track], "$position": pos}}}
        ).modified_count.__bool__()

    def clear_playlist(self, uuid: str, id: int):
        """Очистить плейлист от треков"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})
        if not playlist:
            return
        return self.table.update_one(
            {"uuid": playlist.get("uuid")}, {"$unset": {"tracks": 1}}
        ).modified_count.__bool__()

    def add_view(self, uuid: str):
        """Добавить просмотр плейлисту"""
        playlist: dict = self.table.find_one({"uuid": uuid})
        if not playlist:
            return
        return self.table.update_one(
            {"uuid": playlist.get("uuid")}, {"$inc": {"metric.views": 1}}
        ).modified_count.__bool__()
