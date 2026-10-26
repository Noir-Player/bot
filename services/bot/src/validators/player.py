from typing import TYPE_CHECKING

import disnake
from disnake.ext import commands
from entities.node import Node
from entities.node import get_instance as get_node
from exceptions import *

if TYPE_CHECKING:
    from entities.player import NoirPlayer


async def _check_player(inter: disnake.Interaction, with_connection: bool):

    
    node: Node = get_node()
    
    assert isinstance(inter.author, disnake.Member)
    assert isinstance(inter.guild, disnake.Guild)
    assert isinstance(inter.me, disnake.Member)

    if not inter.author.voice or not inter.author.voice.channel:
        raise NoInVoice("You need to be in a voice channel")

    if not inter.guild.voice_client:  # Bot is not in the voice
        if node.get_player(inter.guild.id):  # if bot somehow handle a player
            try: # quietly destroy
                await node.get_player(inter.guild.id).destroy() # type: ignore
            except BaseException:
                pass

        if not inter.author.voice.channel.permissions_for(inter.me).connect:
            raise commands.BotMissingPermissions(["connect to voice"])

        if with_connection:
            # TODO database check
            # params = inter.bot.db.setup.get_setup(inter.guild.id)  # searching permissions in db 

            # if params:  # if exist
            #     if (
            #         params.get("role")
            #         and not (
            #             params.get("role")
            #             in [role.id for role in inter.author.roles]
            #         )
            #         and not inter.permissions.administrator
            #     ):
            #         raise commands.MissingPermissions(["Setup or manage player"])


            from entities.player import NoirPlayer  # circular import                

            player: NoirPlayer = await inter.author.voice.channel.connect(cls=NoirPlayer)  # type: ignore
            await inter.guild.change_voice_state(channel=inter.author.voice.channel, self_deaf=True)
            return True
        
        else:
            raise NoInVoiceWithMe("You need to be in a voice channel")

    else:  # bot is already in voice
        if inter.guild.voice_client.channel.id != inter.author.voice.channel.id:
            raise NoInVoiceWithMe("You need to be in a voice channel **with me**")

        player = node.get_player(inter.guild.id) # type: ignore

        if player.dj_role:
            if (
                not player.dj_role in [role.id for role in inter.author.roles]
                and not inter.permissions.administrator
            ):
                raise commands.MissingPermissions(["Setup or manage player"])

        return True


# -------------------------------------------------------------------------------------------------------------------------------------
# Slash-command



def check_player(with_connection=False, with_defer=True):
    """
    ### Check the match of author's voice and permission to play

    ---
    `with_connection` is connecting bot to vc if not connected to the same yet
    `with_defer` does defer before check
    """

    async def wrapper(inter: disnake.ApplicationCommandInteraction, *args, **kwargs):
        if with_defer:
            await inter.response.defer(ephemeral=True)

        return await _check_player(inter, with_connection)

    return commands.check(wrapper) # type: ignore


# -------------------------------------------------------------------------------------------------------------------------------------
# Button decorators


def check_player_btn(with_message=False, with_connection=False, with_defer=True):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            inter: disnake.CommandInteraction = args[2]

            if with_defer:
                await inter.response.defer(ephemeral=True, with_message=with_message)

            await _check_player(inter, with_connection)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
