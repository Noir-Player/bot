import datetime

import disnake
from disnake import Embed

import services.persiktunes as persik
from components.ui.views import *
from objects.exceptions import *
from services.persiktunes import LoopMode, Player
from validators.player import check_player_btn_decorator

loop = {LoopMode.QUEUE: "очередь", LoopMode.TRACK: "трек"}


def progress_slider(start, end):
    bar, indicator = "", False

    for i in range(24):
        try:
            if start / end * 24 >= i + 1:
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

    prog = (
        progress_slider(player.adjusted_position, player.adjusted_length)
        if not player.current.info.isStream
        else ""
    )

    embed = Embed(
        color=player.current.color or player.color,
        description=f"<:alternate_email_primary:1239117898912497734> **{player.current.info.author}**",
    )

    embed.set_author(
        name=player.current.info.title,
        url=player.current.info.uri,
        icon_url=player.current.info.artworkUrl,
    )

    embed.set_image(image) if image else None

    embed.set_footer(
        text=f"{prog}\n{times}\n {f'громкость: {player.volume}%' if player.volume != 100 else ''} {f' • повтор: {loop[player.queue.loop_mode]}' if player.queue.loop_mode else ''}",
        icon_url=(
            player.current.ctx.author.display_avatar.url
            if player.current.ctx
            else (
                player.current.requester.display_avatar.url
                if player.current.requester
                else None
            )
        ),
    )

    if player.current.playlist:
        embed.set_author(
            name=player.current.playlist.info.name,
            icon_url=player.current.playlist.pluginInfo.get(
                "artworkUrl", player.current.playlist.tracks[0].info.artworkUrl
            ),
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
        style=disnake.ButtonStyle.gray,
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
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator()
    async def play_pause(self, button, interaction):
        if self.player.current:
            await self.player.set_pause()

    @disnake.ui.button(
        emoji="<:skip_next_primary:1239113700594679838>",
        row=0,
        style=disnake.ButtonStyle.gray,
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
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator(with_message=True)
    async def queue(self, button, interaction: disnake.MessageInteraction):
        if self.player.current:
            view = QueueView(self.player)
            await view.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:repeat_primary:1239113702129664082>",
        row=1,
        style=disnake.ButtonStyle.gray,
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
        emoji="<:volume_down_primary:1239113694856876076>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator()
    async def vol_down(self, button, interaction):
        await self.player.volume_down()

    @disnake.ui.button(
        emoji="<:volume_up_primary:1239113696337199165>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator()
    async def vol_up(self, button, interaction):
        await self.player.volume_up()

    @disnake.ui.button(
        emoji="<:apps_primary:1239113725714104441>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn_decorator()
    async def action(self, button, interaction):
        await interaction.send(ephemeral=True, view=ActionsView(self.player))
