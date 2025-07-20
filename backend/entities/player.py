from typing import Any, List, Optional

import disnake
from disnake.ext import tasks

from services.database.models.setup import SetupDocument

from components.views import Soundpad, state
from components.embeds import *
from components.colors import PRIMARY
from entities.queue import NoirQueue
from services import persiktunes


class NoirPlayer(persiktunes.Player):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._queue = NoirQueue(self, 1000)

        # Default settings
        self._controller: disnake.Message | None = None
        self._dj: int | None = None
        self._flux: bool = False
        self._disable_eq: bool = False
        self._volume_step: int = 25

        # Webhook
        self._webhook: disnake.Webhook | None = None
        self._username: str = "Noir"
        self._icon: str | None = None

        # Custom color
        self._color = int(PRIMARY.replace("#", ""), base=16)

        # Broker
        # self._broker = Broker(self.bot.redis, self)

        self._search_cls = persiktunes.YoutubeMusicSearch(self.node)

        self.bot.loop.create_task(self.refresh_init())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Controller update task

    @tasks.loop()
    async def update_controller(self):
        """
        Start task to updating controller (if exist)
        """
        if not self.is_connected or not self._controller:
            return

        await self.update_controller_once()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Функции

    async def update_controller_once(
        self, force: bool = False, ctx: disnake.Interaction | Any | None = None
    ) -> bool | None:
        """
        ### Update controller once. \n
        If `force = True`, controller will be deleted and called `edit_controller()`. \n
        You need to provide `ctx`, if you providing `force`."""
        try:
            if force and ctx and self._controller:
                await self._controller.delete()
                await self.edit_controller(ctx)

            if self._controller:
                await self._controller.edit(embed=state(self))

        except Exception:
            return False

    async def edit_controller(
        self,
        ctx: disnake.Interaction | Any | None = None,
        embed: Embed | None = None,
        without_view: bool = False,
    ):
        """
        ### Update controller \n
        If not exist, creating new from `def __init__()` or `ctx`
        """
        if not embed:
            embed = state(self)

        try:
            await self._controller.edit(  # type: ignore
                embed=embed, view=None if without_view else Soundpad(self)
            )
        except BaseException:
            try:
                await self._controller.delete()  # type: ignore
            except BaseException:
                pass
            try:
                self._controller = await self._webhook.send(  # type: ignore
                    embed=embed,
                    username=self._username,
                    avatar_url=self._icon,
                    view=None if without_view else Soundpad(player=self),  # type: ignore
                    wait=True,
                )
            except BaseException:
                try:
                    self._controller = await ctx.channel.send(  # type: ignore
                        embed=embed,
                        view=None if without_view else Soundpad(player=self),  # type: ignore
                    )
                except BaseException:
                    return

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Play & stop

    # async def play(
    #     self,
    #     track: persiktunes.Track,
    #     *,
    #     start: int = 0,
    #     end: Optional[int] = None,
    #     noReplace: bool = False,
    #     volume: int | None = None,
    # ) -> None:
    #     await super().play(
    #         track, start=start, end=end, noReplace=noReplace, volume=volume
    #     )

    # TODO add some metrics

    # await self.pub("play", track.model_dump_json(exclude=["ctx", "requester"]))

    # if track.requester:
    #     db.metrics.add_last_track(
    #         track.model_dump_json(exclude=["ctx", "requester"]), track.requester.id
    #     )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Queue attrs to player attrs

    async def skip(self) -> None:
        if self.current and self.queue.loop_mode:
            if self.queue.loop_mode.value != "track":
                if track := self.queue.next():
                    await self.play(track)

    async def prev(self) -> None:
        if self.current and self.queue.loop_mode:
            if self.queue.loop_mode.value != "track":
                if track := self.queue.prev():
                    await self.play(track)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Search

    async def search(
        self,
        query: str,
        *args,
        **kwargs,
    ) -> Optional[List[persiktunes.Track]]:

        return await self._search_cls.search_songs(query, *args, **kwargs)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Стандартные команды, переписанные под пад и сокет

    async def set_pause(self, pause: Optional[bool] = None):  # type: ignore
        if not self.current:
            return
        value = await super().set_pause(pause)
        await self.update_controller_once()

        return value
        # await self.pub("pause", self._paused, position=self.position.__int__())

    # ==========================

    async def set_volume(self, volume: int):
        value = await super().set_volume(volume)
        await self.update_controller_once()

        return value
        # await self.pub("volume", value)

    async def volume_up(self):
        if (self._volume + self._volume_step) >= 0 and (
            self._volume + self._volume_step
        ) <= 500:
            await self.set_volume(self._volume + self._volume_step)

    async def volume_down(self):
        if (self._volume - self._volume_step) >= 0 and (
            self._volume - self._volume_step
        ) <= 500:
            await self.set_volume(self._volume - self._volume_step)

    # ==========================

    async def seek(self, position: int):  # type: ignore
        await super().seek(position)
        await self.update_controller_once()
        # await self.pub("seek", value)

    async def destroy(self):  # type: ignore
        if self.update_controller.is_running():  # Stop if running
            self.update_controller.stop()

        try:
            await self.controller.delete()  # Delete text-controller # type: ignore
        except BaseException:
            pass

        await super().destroy()

        # await self.pub("destroy", True)
        # await self.redis.delete(f"*{self.guild.id}")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Player update

    async def refresh_init(self, force=False):
        """
        ### Get info from database and update info inside entity  \n
        In last call `update_controller_once(force=force)`
        """

        document = await SetupDocument.find_one(
            SetupDocument.guild_id == self._guild_id
        )

        if not document:
            return await self.update_controller_once(force=force)

        try:
            if document.webhook:
                self._webhook = await self.bot.fetch_webhook(document.webhook.id)
                self._username = document.webhook.name or self._username
                self._icon = document.webhook.image_url

        except BaseException:
            document.webhook = None

        self._radio = document.radio

        self._dj = document.dj_role_id

        self._volume_step = document.volume_step

        self._disable_eq = not document.avaible_equalizer

        await self.update_controller_once(force=force)

        await document.save()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Listener

    # async def on_voice_state_update(
    #     self,
    #     member: disnake.Member,
    #     before: disnake.VoiceState,
    #     after: disnake.VoiceState,
    # ):

    #     await self.bot.redis.publish(
    #         f'player-{member.guild.id}',
    #         json.dumps(
    #             {
    #                 "members": [user.id for user in (before.channel.members if before.channel else after.channel.members)]
    #             }
    #         )
    #     )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Properties

    @property
    def is_radio(self) -> bool:
        return self._radio

    @property
    def dj_role(self) -> int | None:
        return self._dj

    @property
    def queue(self) -> NoirQueue:
        return self._queue

    # @property
    # def broker(self) -> Broker:
    #     return self._broker

    @property
    def controller(self) -> disnake.WebhookMessage | disnake.Message | None:
        return self._controller

    @property
    def color(self) -> int:
        return self._color

    @property
    def webhook(self) -> disnake.Webhook | None:
        return self._webhook

    @property
    def disable_eq(self) -> bool:
        return self._disable_eq

    @property
    def volume_step(self) -> int:
        return self._volume_step
