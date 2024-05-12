import json

import disnake

import services.persiktunes as persik
from components.ui.views import *
from objects.exceptions import *
from validators.player import check_player_btn_decorator

errors = json.load(open("data/resources/errors.json", "r", encoding="utf-8"))


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
