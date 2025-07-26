import traceback
from typing import Any

import disnake
from _logging import get_logger
from components.embeds import ErrorEmbed
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

log = get_logger("exceptions")


class NoInVoice(commands.CommandError):
    pass


class NoInVoiceWithMe(commands.CommandError):
    pass


class TrackIsLooping(commands.CommandError):
    pass


class NoCurrent(commands.CommandError):
    pass


class InvalidSource(commands.CommandError):
    pass


class InvalidIndex(commands.CommandError):
    pass


class NoSubscribe(commands.CommandError):
    pass


async def on_error(
    inter: ApplicationCommandInteraction | Any,
    error: commands.CommandError,
):

    log.debug(
        f"Error in {inter.guild_id}: {error.__class__.__name__} - {error}\n{traceback.format_exc()}"
    )

    embed = ErrorEmbed(
        title="Something went wrong",
        description=f"`{error.__class__.__name__}`: {error}",
    )

    # if inter.response.is_done():
    #     await inter.edit_original_response(embed=embed)

    # else:
    await inter.send(embed=embed, ephemeral=True)


async def on_view_error(
    error: commands.CommandError,
    component: disnake.ui.Item,
    inter: ApplicationCommandInteraction | Any,
):

    log.debug(
        f"Error in {inter.guild_id}: {error.__class__.__name__} - {error}\n{traceback.format_exc()}"
    )

    embed = ErrorEmbed(
        title="Something went wrong",
        description=f"`{error.__class__.__name__}`: {error}",
    )

    # if inter.response.is_done():
    #     await inter.edit_original_response(embed=embed)

    # else:
    await inter.send(embed=embed, ephemeral=True)
