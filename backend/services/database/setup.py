from pymongo.collection import Collection


class SetupDB:
    """DB["guilds"]"""

    def __init__(self, table: Collection):
        self.table = table

    def get_setup(self, guild_id: int, without_id: bool = True):
        """Получить запись"""
        result = self.table.find_one({"id": guild_id})
        if without_id and result:
            del result["_id"]
        return result

    def col(self) -> Collection:
        return self.table

    def force_set(self, guild_id, obj: dict, upsert=True):
        """Собрать настройки из словаря"""
        return self.table.update_one(
            {"id": guild_id}, {"$set": obj}, upsert=upsert
        ).modified_count.__bool__()

    def set(self, guild_id, key: str, value=None, upsert=True):
        """Изменяет ключ или удаляет его"""
        if value:
            return self.table.update_one(
                {"id": guild_id}, {"$set": {key: value}}, upsert=upsert
            ).modified_count.__bool__()
        else:
            return self.table.update_one(
                {"id": guild_id}, {"$unset": {key: 1}}, upsert=upsert
            ).modified_count.__bool__()

    def role(self, guild_id, role: int = None):
        """Настроить / удалить роль"""
        if role:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"role": role}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"role": 1}}
            ).modified_count.__bool__()

    def color(self, guild_id, color: str = None):
        """Настроить / удалить цвет эмбеда"""
        if color:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"color": color}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"color": 1}}
            ).modified_count.__bool__()

    def channel(self, guild_id, channel: int = None):
        """Настроить / удалить канал с плеером"""
        if channel:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"channel": channel}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"channel": 1}}
            ).modified_count.__bool__()

    def volume_step(self, guild_id, volume_step: int = None):
        """Настроить / удалить шаг громкости"""
        if volume_step:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"volume_step": volume_step}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"volume_step": 1}}
            ).modified_count.__bool__()

    def disable_eq(self, guild_id, disable_eq: bool = None):
        """Переключить эквалайзер"""
        if disable_eq:
            self.table.update_one(
                {"id": guild_id}, {"$set": {"disable_eq": disable_eq}}
            ).modified_count.__bool__()
        else:
            self.table.update_one(
                {"id": guild_id}, {"$unset": {"disable_eq": 1}}
            ).modified_count.__bool__()

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
                },
                upsert=True,
            ).modified_count.__bool__()
        else:
            return self.table.update_one(
                {"id": guild_id}, {"$unset": {"webhook": 1}}
            ).modified_count.__bool__()

    def clear_guild(self, guild_id):
        """Удалить настройки"""
        return self.table.delete_one({"id": guild_id}).deleted_count.__bool__()
