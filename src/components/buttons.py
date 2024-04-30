import json

import disnake
import pomice

from components.ui.views import *
from helpers.embeds import *
from objects.exceptions import *
from validators.player import check_player_btn_decorator

errors = json.load(open("json-obj/errors.json", "r", encoding="utf-8"))


class Soundpad(disnake.ui.View):
    def __init__(self, player, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

        self.player: pomice.Player = player

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
        emoji="<:prev:1110211620052942911>", row=0, style=disnake.ButtonStyle.blurple
    )
    @check_player_btn_decorator()
    async def prev(self, button, interaction):
        # await check_voice(self.player, interaction)
        if self.player.current:
            if self.player.queue.loop_mode != pomice.LoopMode.TRACK:
                track = self.player.queue.prev()
                if track:
                    await self.player.play(track)
            else:
                raise TrackIsLooping("Нельзя пропускать звук, когда он зациклен")

    @disnake.ui.button(
        emoji="<:skipendcircle:1107270817932378162>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def play_pause(self, button, interaction):
        # await check_voice(self.player, interaction)
        if self.player.current:
            await self.player.set_pause(not self.player.is_paused)

    @disnake.ui.button(
        emoji="<:skipforward:1107250322801442877>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def next(self, button, interaction):
        # await check_voice(self.player, interaction)
        if self.player.queue.loop_mode != pomice.LoopMode.TRACK:
            track = self.player.queue.next()
            if track:
                await self.player.play(track)
        else:
            raise TrackIsLooping("Нельзя пропускать звук, когда он зациклен")

    @disnake.ui.button(
        emoji="<:musicnotelist:1107250545523183616>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator(with_message=True)
    async def queue(self, button, interaction: disnake.MessageInteraction):
        # await check_voice(self.player, interaction, with_message=True)
        if self.player.current:
            view = QueueView(self.player)
            await view.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:repeat1:1107250320301629460>", row=1, style=disnake.ButtonStyle.blurple
    )
    @check_player_btn_decorator()
    async def loop(self, button, interaction):
        # await check_voice(self.player, interaction)

        if self.player.queue.loop_mode == pomice.LoopMode.QUEUE:
            await self.player.queue.set_loop_mode(pomice.LoopMode.TRACK)
        elif self.player.queue.loop_mode == pomice.LoopMode.TRACK:
            await self.player.queue.disable_loop()
        else:
            await self.player.queue.set_loop_mode(pomice.LoopMode.QUEUE)

    @disnake.ui.button(
        emoji="<:volumedown:1107250325578063953>",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def vol_down(self, button, interaction):
        # await check_voice(self.player, interaction)
        await self.player.volume_down()

    @disnake.ui.button(
        emoji="<:volumeup:1107250326974771241>",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def vol_up(self, button, interaction):
        # await check_voice(self.player, interaction)
        await self.player.volume_up()

    @disnake.ui.button(
        emoji="<:threedots:1117080320261500940>", row=1, style=disnake.ButtonStyle.gray
    )
    @check_player_btn_decorator()
    async def action(self, button, interaction):
        # await check_voice(self.player, interaction)

        await interaction.send(ephemeral=True, view=ActionsView(self.player))
