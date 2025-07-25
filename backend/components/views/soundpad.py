# TODO

import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from entities.player import NoirPlayer

import disnake
from assets.emojis import *
from assets.fallbacks import NO_COVER_URL
from components.modals.multiple import AddMultipleModal
from disnake import Embed
from exceptions import *
from exceptions import on_view_error
from services.persiktunes import LoopMode
from validators.player import check_player_btn

from .context import EmbedContext
from .queue import EmbedQueue

loop = {LoopMode.QUEUE: "queue", LoopMode.TRACK: "track"}


def progress_slider(start, end, length=24):
    bar, indicator = "", False

    for i in range(length):
        try:
            if start / end * length >= i + 1:
                if not indicator:
                    bar += "▬"
            else:
                if not indicator:
                    bar += "⭕"
                    indicator = True
                else:
                    bar += "▬"
        except BaseException:
            bar += "▬"

    return bar


def state(player):  # player: NoirPlayer
    times = ""

    if not player.current.info.isStream:

        total = (player.adjusted_length / 1000) % (24 * 3600)
        curr = (player.adjusted_position / 1000) % (24 * 3600)

        total = datetime.time(
            second=int(total % 60),
            minute=int((total % 3600) // 60),
            hour=int(total // 3600),
        ).strftime("%H:%M:%S" if total // 3600 else "%M:%S")
        curr = datetime.time(
            second=int(curr % 60),
            minute=int((curr % 3600) // 60),
            hour=int(curr // 3600),
        ).strftime("%H:%M:%S" if curr // 3600 else "%M:%S")

        times = f"{curr} / {total}"

    image = player.current.info.artworkUrl or NO_COVER_URL

    embed = Embed(
        color=player.current.color or player.color,
        description=f"{ARTIST} **{player.current.info.author}**",
    )

    embed.set_author(
        name=player.current.info.title,
        url=player.current.info.uri,
        icon_url=player.current.info.artworkUrl,
    )

    embed.set_image(image)

    progress = (
        progress_slider(player.adjusted_position, player.adjusted_length)
        if not player.current.info.isStream
        else ""
    )

    infos = []

    infos.append(times)

    if player.volume != 100:
        infos.append(f"volume: {player.volume}%")

    if player.queue.loop_mode:
        infos.append(f"loop: {loop[player.queue.loop_mode]}")

    embed.set_footer(
        text=f"{progress}\n {' • '.join(infos)}",
    )

    return embed


class Soundpad(disnake.ui.View):
    def __init__(self, player, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

        self.player: Any = player

        self.on_error = on_view_error  # type: ignore

    @disnake.ui.button(
        emoji=PREVIOUS,
        row=0,
    )
    @check_player_btn()
    async def prev(self, button, interaction):
        if self.player.current:
            if self.player.queue.loop_mode != LoopMode.TRACK:
                track = self.player.queue.prev()
                if track:
                    await self.player.play(track)
            else:
                raise TrackIsLooping("You can't skip track, when it's looping")

    @disnake.ui.button(
        emoji=PLAYPAUSE,
        row=0,
    )
    @check_player_btn()
    async def play_pause(self, button, interaction):
        if self.player.current:
            await self.player.set_pause()

    @disnake.ui.button(
        emoji=NEXT,
        row=0,
    )
    @check_player_btn()
    async def next(self, button, interaction):
        if self.player.queue.loop_mode != LoopMode.TRACK:
            try:
                await self.player.play(self.player.queue.next())
            except:
                pass
        else:
            raise TrackIsLooping("You can't skip track, when it's looping")

    @disnake.ui.button(
        emoji=QUEUE,
        row=0,
    )
    @check_player_btn(with_message=True)
    async def queue(self, button, interaction: disnake.MessageInteraction):
        await EmbedQueue(self.player.node).send(interaction)

    @disnake.ui.button(
        emoji=LOOP,
        row=1,
    )
    @check_player_btn()
    async def loop(self, button, interaction):
        if self.player.queue.loop_mode == LoopMode.QUEUE:
            await self.player.queue.set_loop_mode(LoopMode.TRACK)
        elif self.player.queue.loop_mode == LoopMode.TRACK:
            await self.player.queue.set_loop_mode()
        else:
            await self.player.queue.set_loop_mode(LoopMode.QUEUE)

    @disnake.ui.button(
        emoji=ADD,
        row=1,
    )
    @check_player_btn(with_defer=False)
    async def add(self, button, interaction):
        await interaction.response.send_modal(AddMultipleModal(self.player))

    @disnake.ui.button(
        emoji=STOP,
        row=1,
    )
    @check_player_btn()
    async def _stop(self, button, interaction):
        await self.player.destroy()

    @disnake.ui.button(
        emoji=ACTION,
        row=1,
    )
    @check_player_btn(with_message=True)
    async def action(self, button, interaction):
        await EmbedContext(self.player.node).send(interaction)
