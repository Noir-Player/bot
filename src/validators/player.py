from disnake.ext import commands
from classes.Exceptions import *

# from classes.Player import NoirPlayer

# -------------------------------------------------------------------------------------------------------------------------------------
# Декораторы для slash-команд


def check_player_decorator(with_connection=False):
    """
    ### Проверить, находится ли юзер в канале с Noir и имеет нужные права.

    ---
    Параметр `with_connection` определяет, нужно ли подключиться в случае неудачи.
    """

    async def wrapper(inter, *args, **kwargs):
        await inter.response.defer(ephemeral=True)

        node = inter.bot.node

        if not inter.author.voice:  # Автор не в войсе
            raise NoInVoice("Вам нужно быть в войсе")

        if not inter.guild.voice_client:  # бот не в войсе
            if node.get_player(
                inter.guild_id
            ):  # если бот каким то образом хранит плеер
                try:
                    await node.get_player(inter.guild_id).destroy()
                except BaseException:
                    pass

            if not inter.author.voice.channel.permissions_for(
                inter.me
            ).connect:  # нет доступа к войсу
                raise commands.BotMissingPermissions(["connect to voice"])

            if with_connection:  # если указано подключиться
                params = inter.bot.db.setup.get_setup(
                    inter.guild.id)  # поиск прав в бд

                if params:  # если есть требования к правам
                    if (
                        params.get("role")
                        and not (
                            params.get("role")
                            in [role.id for role in inter.author.roles]
                        )
                        and not inter.permissions.administrator
                    ):
                        raise commands.MissingPermissions(
                            ["setup or manage player"])

                from classes.Player import (
                    NoirPlayer,
                )  # предотвращает циркулярный импорт

                player = await inter.author.voice.channel.connect(
                    cls=NoirPlayer
                )  # подключение
                await inter.guild.change_voice_state(
                    channel=inter.author.voice.channel, self_deaf=True
                )
                return True
            else:
                raise NoInVoiceWithMe("Вам нужно быть в войсе")

        else:  # Нуар уже в войсе
            if inter.guild.voice_client.channel.id != inter.author.voice.channel.id:
                raise NoInVoiceWithMe("Вам нужно быть в войсе вместе со мной")

            player = node.get_player(inter.guild_id)  # получаем плеер

            if player.dj_role:
                if (
                    not player.dj_role in [role.id for role in inter.author.roles]
                    and not inter.permissions.administrator
                ):
                    raise commands.MissingPermissions(
                        ["setup or manage player"])

            return True

    return commands.check(wrapper)


# -------------------------------------------------------------------------------------------------------------------------------------
# Декораторы для кнопок


def check_player_btn_decorator(with_message=False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            inter = args[2]

            await inter.response.defer(
                ephemeral=True, with_message=True
            ) if with_message else await inter.response.defer(ephemeral=True)

            node = inter.bot.node

            if not inter.author.voice:  # Автор не в войсе
                raise NoInVoice("Вам нужно быть в войсе")

            if not inter.guild.voice_client:  # бот не в войсе
                if node.get_player(
                    inter.guild_id
                ):  # если бот каким то образом хранит плеер
                    try:
                        await node.get_player(inter.guild_id).destroy()
                    except BaseException:
                        pass

                raise NoInVoiceWithMe("Вам нужно быть в войсе")

            else:  # Нуар уже в войсе
                if inter.guild.voice_client.channel.id != inter.author.voice.channel.id:
                    raise NoInVoiceWithMe(
                        "Вам нужно быть в войсе вместе со мной")

                player = node.get_player(inter.guild_id)  # получаем плеер

                if player.dj_role:
                    if (
                        not player.dj_role in [role.id for role in inter.author.roles]
                        and not inter.permissions.administrator
                    ):
                        raise commands.MissingPermissions(
                            ["setup or manage player"])

                return await func(*args, **kwargs)

        return wrapper

    return decorator
