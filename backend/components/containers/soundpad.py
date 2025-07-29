# TODO

import datetime
from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from entities.player import NoirPlayer

import disnake
from assets.colors import *
from assets.emojis import *
from assets.fallbacks import NO_COVER_URL
from components.buttons.soundpad import *
from components.modals.multiple import AddMultipleModal
from disnake import ui
from disnake.ui.item import UIComponent
from exceptions import *
from services.persiktunes import LoopMode
from validators.player import check_player_btn

from ..views.context import EmbedContext
from ..views.queue import EmbedQueue

loop = {LoopMode.QUEUE: "queue", LoopMode.TRACK: "track"}


def progress_slider(
    pos: int, end: int, length: int = 17, lowscreen_optimazed: bool = False
) -> str:
    slider: str = ""

    flag: bool = False
    flag_index = -1

    if lowscreen_optimazed:
        length = 10

    for i in range(length):
        check: bool = pos / end * length >= i + 1  # while True, indicator placed after

        if flag_index == -1 and not check:
            flag_index = i

        flag = i == flag_index

        if i == 0:
            slider += (
                PROGRESS_START
                if check
                else (INDICATOR_START if flag else BACKGROUND_START)
            )
        elif i == length - 1:
            slider += (
                PROGRESS_END if check else (INDICATOR_END if flag else BACKGROUND_END)
            )
        else:
            slider += (
                PROGRESS_MID if check else (INDICATOR_MID if flag else BACKGROUND_MID)
            )

    return slider


def progress_timer(
    current, total, length: int = 28, lowscreen_optimazed: bool = False
) -> str:

    total = (total / 1000) % (24 * 3600)
    curr = (current / 1000) % (24 * 3600)

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

    middle_width = length - len(curr) - len(total)
    filler_padding = "ㅤ" * middle_width

    if lowscreen_optimazed:
        filler_padding = " / "

    formatted_string = f"`{curr}`{filler_padding}`{total}`"

    return formatted_string


class MoreMenu(disnake.ui.View):
    def __init__(self, player, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

        self.player: Any = player

        self.on_error = on_view_error  # type: ignore

    @disnake.ui.button(
        emoji=ADD,
    )
    @check_player_btn(with_defer=False)
    async def add(self, button, interaction):
        await interaction.response.send_modal(AddMultipleModal(self.player))

    @disnake.ui.button(
        emoji=STOP,
    )
    @check_player_btn()
    async def _stop(self, button, interaction):
        await self.player.destroy()

    @disnake.ui.button(
        emoji=QUEUE,
    )
    @check_player_btn(with_message=True)
    async def queue(self, button, interaction: disnake.MessageInteraction):
        await EmbedQueue(self.player.node).send(interaction)

    @disnake.ui.button(
        emoji=ACTION,
    )
    @check_player_btn(with_message=True)
    async def action(self, button, interaction):
        await EmbedContext(self.player.node).send(interaction)


def not_current_fallback(fallback_track=None) -> Sequence[UIComponent]:
    components = []

    components.append(ui.TextDisplay(f"## Waiting for tracks 👾"))

    components.append(ui.TextDisplay(f"-# Nothing to play from queue..."))

    components.append(ui.Separator())

    components.append(
        ui.TextDisplay(
            "You can add tracks to the queue by using the `/play` command ✨"
        )
    )

    if fallback_track:
        components.append(
            ui.Section(
                ui.TextDisplay(
                    f"If you want, you can start autoplay from last track {fallback_track.info.title} by clicking the button in right ✨"
                ),
                accessory=START_AUTOPLAY_BUTTON,
            ),
        )

    container = ui.Container(
        *components,
        accent_colour=disnake.Colour(int(PRIMARY.replace("#", ""), base=16)),
    )

    return [container]


def state(player, fallback_track=None) -> Sequence[UIComponent]:  # player: NoirPlayer

    if not player.current:
        return not_current_fallback(fallback_track)

    components = []

    # Album
    if player.current.album:
        components.append(
            ui.TextDisplay(
                f"-# <:album:1399428474296340530> {player.current.album.name}"
            )
        )

    # Artwork
    components.append(
        ui.MediaGallery(
            disnake.MediaGalleryItem(
                {
                    "media": {"url": player.current.info.artworkUrl or NO_COVER_URL},
                },
            )
        )
    )

    # Section with titile and add button

    title = "# " + (
        player.current.info.title[:24] + "..."
        if len(player.current.info.title) > 25
        else player.current.info.title
    )

    components.append(
        ui.Section(
            ui.TextDisplay(
                f"# {player.current.info.title}\n{ARTIST} {player.current.info.author}"
            ),
            accessory=LIKE_BUTTON,
        ),
    )

    lowscreen_optimazed = (
        player.current.requester.is_on_mobile()
        if isinstance(player.current.requester, disnake.Member)
        else False
    )

    progress = (
        progress_slider(
            player.adjusted_position,
            player.adjusted_length,
            lowscreen_optimazed=lowscreen_optimazed,
        )
        if not player.current.info.isStream
        else progress_slider(1, 1, 10) + " **LIVE**"
    )

    timer = (
        progress_timer(
            player.adjusted_position,
            player.adjusted_length,
            lowscreen_optimazed=lowscreen_optimazed,
        )
        if not player.current.info.isStream
        else ""
    )

    info_string = []

    if player.volume != 100:
        info_string.append(f"volume: {player.volume}%")

    if player.queue.loop_mode:
        info_string.append(f"loop: {loop[player.queue.loop_mode]}")

    components.append(ui.TextDisplay(f"{progress}\n{timer}\n{' • '.join(info_string)}"))

    components.append(ui.Separator(divider=False))

    components.append(ui.ActionRow(*SOUNDPAD_BUTTONS))

    container = ui.Container(
        *components,
        accent_colour=disnake.Colour(int(PRIMARY.replace("#", ""), base=16)),
    )

    return [container]
