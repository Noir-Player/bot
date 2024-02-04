import pymongo
import uuid
import datetime

from pymongo import ASCENDING
from pymongo.collection import Collection

mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongoclient["Noir"]


def table(name: str) -> Collection:
    return db[name]


class Database:
    """Основной класс базы"""

    def __init__(self) -> None:
        self.mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = mongoclient["Noir"]

        self._setup = SetupDB(self.db["guilds"])
        self._playlists = PlaylistsDB(self.db["playlists"])
        self._stars = StarsDB(self.db["stars"])
        self._users = UsersDB(self.db["users"])
        self._metrics = MetricsDB(self.db["metrics"])
        self._cache = CacheDB(self.db["cache"])
        self._sessions = SessionsDB(self.db["sessions"])

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
    
    @property
    def sessions(self):
        """Таблица с сессиями"""
        return self._sessions

    def table(self, name: str) -> Collection:
        return self.db[name]


class SetupDB:
    """DB["guilds"]"""

    def __init__(self, table: Collection):
        self.table = table

    def get_setup(self, guild_id: int, without_id: bool = True):
        """Получить запись"""
        result = self.table.find_one({"id": guild_id})
        if without_id and result:
            del result['_id']
        return result

    def col(self) -> Collection:
        return self.table
    
    def force_set(self, guild_id, obj: dict, upsert=True):
        """Собрать настройки из словаря"""
        return self.table.update_one(
                {"id": guild_id}, {"$set": obj}, upsert=upsert).modified_count.__bool__()

    def set(self, guild_id, key: str, value=None, upsert=True):
        """Изменяет ключ или удаляет его"""
        if value:
            return self.table.update_one(
                {"id": guild_id}, {"$set": {key: value}}, upsert=upsert
            ).modified_count.__bool__()
        else:
            return self.table.update_one(
                {"id": guild_id}, {"$unset": {key: 1}}, upsert=upsert).modified_count.__bool__()

    def role(self, guild_id, role: int = None):
        """Настроить / удалить роль"""
        if role:
            self.table.update_one({"id": guild_id}, {"$set": {"role": role}}).modified_count.__bool__()
        else:
            self.table.update_one({"id": guild_id}, {"$unset": {"role": 1}}).modified_count.__bool__()

    def color(self, guild_id, color: str = None):
        """Настроить / удалить цвет эмбеда"""
        if color:
            self.table.update_one({"id": guild_id}, {"$set": {"color": color}}).modified_count.__bool__()
        else:
            self.table.update_one({"id": guild_id}, {"$unset": {"color": 1}}).modified_count.__bool__()

    def channel(self, guild_id, channel: int = None):
        """Настроить / удалить канал с плеером"""
        if channel:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"channel": channel}}).modified_count.__bool__()
        else:
            self.table.update_one({"id": guild_id}, {"$unset": {"channel": 1}}).modified_count.__bool__()

    def volume_step(self, guild_id, volume_step: int = None):
        """Настроить / удалить шаг громкости"""
        if volume_step:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"volume_step": volume_step}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"volume_step": 1}}).modified_count.__bool__()

    def disable_eq(self, guild_id, disable_eq: bool = None):
        """Переключить эквалайзер"""
        if disable_eq:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"disable_eq": disable_eq}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"disable_eq": 1}}).modified_count.__bool__()

    def webhook(
        self,
        guild_id,
        webhook_id: int = None,
        webhook_name: str = "Noir Player",
        webhook_icon: str = None,
    ):
        """Настроить вебхук"""
        if webhook_id:
            return self.table.update_one(
                {"id": guild_id},
                {
                    "$set": {
                        "webhook.id": webhook_id,
                        "webhook.name": webhook_name,
                        "webhook.icon": webhook_icon,
                    }
                }, upsert=True
            ).modified_count.__bool__()
        else:
            return self.table.update_one({"id": guild_id}, {"$unset": {"webhook": 1}}).modified_count.__bool__()

    def clear_guild(self, guild_id):
        """Удалить настройки"""
        return self.table.delete_one({"id": guild_id}).deleted_count.__bool__()


class PlaylistsDB:
    """DB["playlists"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def get_playlist(self, uuid: str, without_id: bool = True) -> dict | None:
        """Найти плейлист"""
        result = self.table.find_one({"uuid": uuid})
        if without_id and result:
            del result['_id']
        return result

    def get_user_playlists(
            self,
            id: int,
            include_forked: bool = True) -> dict | None:
        """Получить плейлисты пользователя. `include_forked` определяет, включать ли плейлисты других пользователей."""
        return [
            playlist
            for playlist in table("playlists").find(
                {"$or": [{"author.id": id}, {"forked": {"$elemMatch": {"$eq": id}}}]} if include_forked else {"author.id": id}
            )
        ]

    def add_to_library(self, uuid: str, id: int):
        """Добавить плейлист в библиотеку"""
        return self.table.update_one({"uuid": uuid}, {"$addToSet": {"forked": id}}).modified_count.__bool__()

    def delete_playlist(self, uuid: str, id: int):
        """Удалить плейлист (из библиотеки или перманентно)"""
        playlist: dict = self.table.find_one({"uuid": uuid})
        if not playlist:
            return
        if playlist.get("author").get(
                "id") == id and playlist.get("uuid") == uuid:
            return self.table.delete_one({"uuid": uuid}).deleted_count.__bool__()

        elif id in playlist.get("forked") and playlist.get("uuid") == uuid:
            return self.table.update_one(
                {"uuid": uuid}, {"$pull": {"forked": id}}).modified_count.__bool__()

    def create_playlist(
        self,
        id: int,
        name: str,
        title: str,
        thumbnail: str,
        description: str,
        public: bool,
        tracks: list = [],
        **kwargs
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
                    "tracks": tracks
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
        **kwargs
    ):
        """Изменить плейлист по uuid"""
        playlist: dict = self.table.find_one({"uuid": uuid, "author.id": id})
        if not playlist:
            return
        
        return self.table.update_one(
            {"uuid": playlist.get("uuid")},
            {
                "$set": {
                    "title": title or playlist.get('title'),
                    "thumbnail": thumbnail or playlist.get('thumbnail'),
                    "description": description or playlist.get('description'),
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
        track = next(
            track for track in playlist["tracks"] if track.get("url") == url)
        self.table.update_one({"uuid": uuid},
                              {"$pull": {f"tracks": {"url": url}}})
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
            del result['_id']
        return result

    def add_to_stars(self, id: int, track_or_list: dict | list):
        """Добавить в звездочки"""
        stars = self.table.find_one({"user_id": id})
        if stars and len(stars.get("tracks", [])) + (1 if type(track_or_list) == dict else len(track_or_list)) <= 1000:
            track = track_or_list if type(track_or_list) == dict else {"$each": track_or_list}
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
        track = next(
            track for track in stars["tracks"] if track.get("url") == url)
        self.table.update_one({"user_id": id},
                              {"$pull": {f"tracks": {"url": url}}})
        return self.table.update_one(
            {"user_id": id}, {"$push": {"tracks": {"$each": [track], "$position": pos}}}
        ).modified_count.__bool__()


class UsersDB:
    """DB["users"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def get_user(self, id: int, without_id: bool = True):
        """Получить юзера"""
        result = self.table.find_one({"id": id})
        if without_id and result:
            del result['_id']
        return result
    
    def edit_user(self, id: int, name: str, description: str, theme: str):
        """Изменить юзера"""
        return self.table.update_one(
            {"id": id}, {"$set": {"name": name, "description": description, "theme": theme}}).modified_count.__bool__()

    def set_name(self, name: str, id: int):
        """Установить имя"""
        return self.table.update_one(
            {"id": id}, {"$set": {"name": name}}, upsert=True).modified_count.__bool__()

    def set_description(self, description: str, id: int):
        """Установить описание"""
        return self.table.update_one(
            {"id": id}, {"$set": {"description": description}}, upsert=True).modified_count.__bool__()

    def set_role(self, role: str, id: int):
        """Добавить роль"""
        return self.table.update_one(
            {"id": id}, {"$set": {"role": role}}, upsert=True).modified_count.__bool__()

    def set_permissions(self, permissions: int, id: int):
        """Настроить уровень разрешений"""
        return self.table.update_one(
            {"id": id}, {"$set": {"permissions": permissions}}, upsert=True).modified_count.__bool__()

    def set_playlist_limit(self, playlist_limit: int, id: int):
        """Установить лимит плейлистов"""
        return self.table.update_one(
            {"id": id}, {"$set": {"playlist_limit": playlist_limit}}, upsert=True
        ).modified_count.__bool__()

    def set_theme(self, theme: int, id: int):
        """Установить тему сайта"""
        return self.table.update_one(
            {"id": id}, {"$set": {"theme": theme}}, upsert=True).modified_count.__bool__()

    def ban(self, reason: str, timestamp: int, id: int):
        """Заблокировать"""
        return self.table.update_one(
            {"id": id}, {"$set": {"ban.reason": reason, "ban.timestamp": timestamp}}, upsert=True
        ).modified_count.__bool__()


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
            del result['_id']
        return result

    def add_last_track(self, track: dict, id: int):
        """Добавить последний прослушанный трек"""
        self.table.update_one(
            {"id": id},
            {"$push": {"last_tracks": {"$each": [track], "$slice": -5}}},
            upsert=True,
        ).modified_count.__bool__()


class CacheDB:
    """DB["cache"]"""

    def __init__(self, table: Collection):
        self.table = table

        self.table.create_index(
            [("expireAt", ASCENDING)], expireAfterSeconds=0)

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
        info["expireAt"] = datetime.datetime.utcnow() + (expireAt or datetime.timedelta(days=7))

        return self.table.update_one(
            {"id": int(id)},
            {"$set": info},
            upsert=True,
        ).modified_count.__bool__()

    def push(
        self,
        info: dict,
        id: int
        ):
        """Добавить к списку"""
        return self.table.update_one(
            {"id": int(id)},
            {"$addToSet": info},
            upsert=True,
        ).modified_count.__bool__()

    def clear(self, id: int):
        """Очистить кэш"""
        return self.table.delete_one({"id": int(id)})


class SessionsDB:
    """DB["sessions"]"""

    def __init__(self, table: Collection):
        self.table = table

        self.table.create_index([("expireAt", ASCENDING)], expireAfterSeconds=0)

    def col(self) -> Collection:
        return self.table

    def get(self, token: str):
        """Получить сессию"""
        return self.table.find_one({"token": token})

    def set(
        self,
        info: dict,
        token: str,
        expireAt: datetime.timedelta = None,
    ) -> dict | None:
        """Установить / обновить сессию"""
        info["expireAt"] = datetime.datetime.utcnow() + (expireAt or datetime.timedelta(days=7))

        return self.table.update_one(
            {"token": token},
            {"$set": info},
            upsert=True,
        ).modified_count.__bool__()
    

    def set_oauth_token(
        self,
        oauth_token: str,
        token: str,
    ):
        """Установить токен для авторизации"""

        return self.table.update_one(
            {"token": token},
            {"$set": {"oauth_token": oauth_token}},
            upsert=True,
        ).modified_count.__bool__()
    

    def get_oauth_token(
        self,
        token: str,
    ):
        """Получить токен авторизации. После авторизации токен удаляется"""

        return (
            self.table.find_one_and_update({"token": token}, {"$unset": {"oauth_token": 1}}) or {"oauth_token": None}
            ).get('oauth_token')
    

    def set_oauth_state(
        self,
        oauth_state: str,
        token: str,
    ):
        """Установить токен для авторизации"""

        return self.table.update_one(
            {"token": token},
            {"$set": {"oauth_state": oauth_state}},
            upsert=True,
        ).modified_count.__bool__()
    

    def get_oauth_state(
        self,
        token: str,
    ):
        """Получить токен авторизации. После авторизации токен удаляется"""

        return (
            self.table.find_one_and_update({"token": token}, {"$unset": {"oauth_state": 1}}) or {"oauth_state": None}
            ).get('oauth_state')


    def push(
        self,
        info: dict,
        token: str
        ):
        """Добавить к списку"""
        return self.table.update_one(
            {"token": token},
            {"$addToSet": info},
            upsert=True,
        ).modified_count.__bool__()

    def clear(self, token: str):
        """Удалить сессию"""
        return self.table.delete_one({"token": token})
