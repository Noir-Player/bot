from pymongo.collection import Collection


class UsersDB:
    """DB["users"]"""

    def __init__(self, table: Collection):
        self.table = table

    def col(self) -> Collection:
        return self.table

    def add_user(self, user: dict):
        """Добавить юзера"""
        return self.table.update_one(
            {"id": int(user.get("id"))}, {"$set": user}, upsert=True
        ).modified_count.__bool__()

    def get_user(self, id: int, without_id: bool = True):
        """Получить юзера"""
        result = self.table.find_one({"id": id})
        if without_id and result:
            del result["_id"]
        return result

    def edit_user(self, id: int, name: str, description: str, theme: str):
        """Изменить юзера"""
        return self.table.update_one(
            {"id": id},
            {"$set": {"name": name, "description": description, "theme": theme}},
        ).modified_count.__bool__()

    def set_name(self, name: str, id: int):
        """Установить имя"""
        return self.table.update_one(
            {"id": id}, {"$set": {"name": name}}, upsert=True
        ).modified_count.__bool__()

    def set_icon(self, icon: str, id: int):
        """Установить иконку"""
        return self.table.update_one(
            {"id": id}, {"$set": {"icon": icon}}, upsert=True
        ).modified_count.__bool__()

    def set_description(self, description: str, id: int):
        """Установить описание"""
        return self.table.update_one(
            {"id": id}, {"$set": {"description": description}}, upsert=True
        ).modified_count.__bool__()

    def set_role(self, role: str, id: int):
        """Добавить роль"""
        return self.table.update_one(
            {"id": id}, {"$set": {"role": role}}, upsert=True
        ).modified_count.__bool__()

    def set_permissions(self, permissions: int, id: int):
        """Настроить уровень разрешений"""
        return self.table.update_one(
            {"id": id}, {"$set": {"permissions": permissions}}, upsert=True
        ).modified_count.__bool__()

    def set_playlist_limit(self, playlist_limit: int, id: int):
        """Установить лимит плейлистов"""
        return self.table.update_one(
            {"id": id}, {"$set": {"playlist_limit": playlist_limit}}, upsert=True
        ).modified_count.__bool__()

    def set_theme(self, theme: int, id: int):
        """Установить тему сайта"""
        return self.table.update_one(
            {"id": id}, {"$set": {"theme": theme}}, upsert=True
        ).modified_count.__bool__()

    def ban(self, reason: str, timestamp: int, id: int):
        """Заблокировать"""
        return self.table.update_one(
            {"id": id},
            {"$set": {"ban.reason": reason, "ban.timestamp": timestamp}},
            upsert=True,
        ).modified_count.__bool__()
