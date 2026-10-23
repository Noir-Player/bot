from typing import TYPE_CHECKING

import disnake
from disnake.ext import commands
from entities.node import Node
from entities.node import get_instance as get_node
from exceptions import *

if TYPE_CHECKING:
    from entities.player import NoirPlayer

# -------------------------------------------------------------------------------------------------------------------------------------
# Декораторы для slash-команд


def check_player(with_connection=False, with_defer=True):
    """
    ### Проверить, находится ли юзер в канале с Noir и имеет нужные права.

    ---
    Параметр `with_connection` определяет, нужно ли подключиться в случае неудачи.
    Параметр `with_defer` определяет, нужно ли делать defer() перед вызовом функции.
    """

    async def wrapper(inter: disnake.ApplicationCommandInteraction, *args, **kwargs):
        if with_defer:
            await inter.response.defer(ephemeral=True)

        node: Node = get_node()

        if not inter.author.voice:  # Автор не в войсе
            raise NoInVoice("You need to be in a voice channel")

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
                # TODO database check
                # params = inter.bot.db.setup.get_setup(inter.guild.id)  # поиск прав в бд

                # if params:  # если есть требования к правам
                #     if (
                #         params.get("role")
                #         and not (
                #             params.get("role")
                #             in [role.id for role in inter.author.roles]
                #         )
                #         and not inter.permissions.administrator
                #     ):
                #         raise commands.MissingPermissions(["Setup or manage player"])

                from entities.player import (  # предотвращает циркулярный импорт
                    NoirPlayer,
                )

                player = await inter.author.voice.channel.connect(
                    cls=NoirPlayer
                )  # подключение
                await inter.guild.change_voice_state(
                    channel=inter.author.voice.channel, self_deaf=True
                )
                return True
            else:
                raise NoInVoiceWithMe("You need to be in a voice channel")

        else:  # Нуар уже в войсе
            if inter.guild.voice_client.channel.id != inter.author.voice.channel.id:
                raise NoInVoiceWithMe("You need to be in a voice channel **with me**")

            player = node.get_player(inter.guild_id)  # получаем плеер

            if player.dj_role:
                if (
                    not player.dj_role in [role.id for role in inter.author.roles]
                    and not inter.permissions.administrator
                ):
                    raise commands.MissingPermissions(["Setup or manage player"])

            return True

    return commands.check(wrapper)


# -------------------------------------------------------------------------------------------------------------------------------------
# Декораторы для кнопок


def check_player_btn(with_message=False, with_connection=False, with_defer=True):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            inter: disnake.CommandInteraction = args[2]

            if with_defer:
                await inter.response.defer(ephemeral=True, with_message=with_message)

            node: Node = get_node()

            if not inter.author.voice:  # Автор не в войсе
                raise NoInVoice("You need to be in a voice channel")

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
                    # TODO database check
                    # params = inter.bot.db.setup.get_setup(
                    #     inter.guild.id
                    # )  # поиск прав в бд

                    # if params:  # если есть требования к правам
                    #     if (
                    #         params.get("role")
                    #         and not (
                    #             params.get("role")
                    #             in [role.id for role in inter.author.roles]
                    #         )
                    #         and not inter.permissions.administrator
                    #     ):
                    #         raise commands.MissingPermissions(
                    #             ["Setup or manage player"]
                    #         )

                    from entities.player import (  # предотвращает циркулярный импорт
                        NoirPlayer,
                    )

                    player = await inter.author.voice.channel.connect(
                        cls=NoirPlayer
                    )  # подключение
                    await inter.guild.change_voice_state(
                        channel=inter.author.voice.channel, self_deaf=True
                    )
                    return True
                else:
                    raise NoInVoiceWithMe("You need to be in a voice channel")

            else:  # Нуар уже в войсе
                if inter.guild.voice_client.channel.id != inter.author.voice.channel.id:
                    raise NoInVoiceWithMe(
                        "You need to be in a voice channel **with me**"
                    )

                player: NoirPlayer = node.get_player(inter.guild_id)  # получаем плеер

                if player.dj_role:
                    if (
                        not player.dj_role in [role.id for role in inter.author.roles]
                        and not inter.permissions.administrator
                    ):
                        raise commands.MissingPermissions(["Setup or manage player"])

                return await func(*args, **kwargs)

        return wrapper

    return decorator
