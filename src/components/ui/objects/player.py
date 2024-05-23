import datetime

import disnake
from disnake import Embed

import services.persiktunes as persik
from components.modals.multiple import AddMultiple
from components.ui.objects.context import EmbedContext
from components.ui.objects.queue import EmbedQueue
from objects.exceptions import *
from services.persiktunes import LoopMode, Player
from validators.player import check_player_btn_decorator

loop = {LoopMode.QUEUE: "очередь", LoopMode.TRACK: "трек"}


def progress_slider(start, end, length=24):
    bar, indicator = "", False

    for i in range(length):
        try:
            if start / end * length >= i + 1:
                if not indicator:
                    bar += "▬"
            else:
                if not indicator:
                    bar += "🟣"
                    indicator = True
                else:
                    bar += "▬"
        except BaseException:
            bar += "▬"

    return bar


async def state(player: Player):
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

    image = (
        player.current.info.artworkUrl
        if player.current.info.artworkUrl
        else f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif"
    )

    embed = Embed(
        color=player.current.color or player.color,
        description=f"<:alternate_email_primary:1239117898912497734> **{player.current.info.author}**",
    )

    embed.set_author(
        name=player.current.info.title,
        url=player.current.info.uri,
    )

    embed.set_image(image) if image else None

    prog = (
        progress_slider(player.adjusted_position, player.adjusted_length)
        if not player.current.info.isStream
        else ""
    )

    embed.set_footer(
        text=f"{prog}\n{times}\n {f'громкость: {player.volume}%' if player.volume != 100 else ''} {f' • повтор: {loop[player.queue.loop_mode]}' if player.queue.loop_mode else ''}",
    )

    return embed


class Soundpad(disnake.ui.View):
    def __init__(self, player, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

        self.player: persik.Player = player

    # async def on_error(self, error: Exception, item, interaction):
    #     if error is commands.CommandError or error is commands.CommandInvokeError:
    #         e = errors.get(error.__cause__.__class__.__name__, '*Something went wrong...*')
    #     else:
    #         e = errors.get(error.__class__.__name__, '*Something went wrong...*')

    #     await interaction.send(
    #         embed=type_embed("error", f"```diff\n- {e}```"),
    #         ephemeral=True,
    #         components=[disnake.ui.Button(style=disnake.ButtonStyle.url, label="report", url="https://discord.gg/ua4kpgzpWJ")]
    #         )

    #     logging.error(f'error in soundpad:')
    #     logging.error(traceback.format_exc())

    @disnake.ui.button(
        emoji="<:skip_previous_primary:1239113698623225908>",
        row=0,
    )
    @check_player_btn_decorator()
    async def prev(self, button, interaction):
        if self.player.current:
            if self.player.queue.loop_mode != persik.LoopMode.TRACK:
                track = self.player.queue.prev()
                if track:
                    await self.player.play(track)
            else:
                raise TrackIsLooping("Нельзя пропускать звук, когда он зациклен")

    @disnake.ui.button(
        emoji="<:play_pause_primary:1239113853137326220>",
        row=0,
    )
    @check_player_btn_decorator()
    async def play_pause(self, button, interaction):
        if self.player.current:
            await self.player.set_pause()

    @disnake.ui.button(
        emoji="<:skip_next_primary:1239113700594679838>",
        row=0,
    )
    @check_player_btn_decorator()
    async def next(self, button, interaction):
        if self.player.queue.loop_mode != persik.LoopMode.TRACK:
            track = self.player.queue.next()
            if track:
                await self.player.play(track)
        else:
            raise TrackIsLooping("Нельзя пропускать звук, когда он зациклен")

    @disnake.ui.button(
        emoji="<:queue_music_primary:1239113703824293979>",
        row=0,
    )
    @check_player_btn_decorator(with_message=True)
    async def queue(self, button, interaction: disnake.MessageInteraction):
        if self.player.current:
            await EmbedQueue(self.player.node).send(interaction)

    @disnake.ui.button(
        emoji="<:repeat_primary:1239113702129664082>",
        row=1,
    )
    @check_player_btn_decorator()
    async def loop(self, button, interaction):
        if self.player.queue.loop_mode == persik.LoopMode.QUEUE:
            await self.player.queue.set_loop_mode(persik.LoopMode.TRACK)
        elif self.player.queue.loop_mode == persik.LoopMode.TRACK:
            await self.player.queue.set_loop_mode()
        else:
            await self.player.queue.set_loop_mode(persik.LoopMode.QUEUE)

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=1,
    )
    @check_player_btn_decorator(with_defer=False)
    async def add(self, button, interaction):
        await interaction.response.send_modal(AddMultiple(self.player))

    @disnake.ui.button(
        emoji="<:delete_primary:1239113856027070514>",
        row=1,
    )
    @check_player_btn_decorator()
    async def remove(self, button, interaction):
        """"""
        # TODO

    @disnake.ui.button(
        emoji="<:apps_primary:1239113725714104441>",
        row=1,
    )
    @check_player_btn_decorator(with_message=True)
    async def action(self, button, interaction):
        await EmbedContext(self.player.node).send(interaction)
