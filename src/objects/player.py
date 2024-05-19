import json
from typing import Any, Coroutine, Optional

import disnake
from disnake.ext import tasks

from components.ui.objects.player import Soundpad, state
from helpers.dump import Dump as Build
from objects.queue import NoirQueue
from services import persiktunes
from services.database.core import Database

build = Build()
db = Database()


class NoirPlayer(persiktunes.Player):
    """Кастомный плеер `persiktunes.Player`. Хранит в себе информацию об очереди, саундбаре и функции для их изменения."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Первоначальная настройка очереди
        self._queue = NoirQueue(self, 1000)

        # Настройки по умолчанию
        self._controller = None
        self._dj = None
        self._flux = False
        self._disable_eq = False
        self._volume_step = 25

        # Вебхук
        self._webhook: disnake.Webhook | None = None
        self._username: str = ...
        self._icon: str = ...

        # Кастом плеер
        self._color = int(self.bot.embedding.primary_light.replace("#", ""), base=16)

        # Брокер сокетов
        # self._broker = Broker(self.bot.redis, self)

        # NOTE: перенесено в очередь classes.Queue
        # """Генерация треков"""
        # self._nonstop = False

        self.bot.loop.create_task(self.refresh_init())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Таск для пада

    @tasks.loop()
    async def update_controller(self):
        """Таск для обновления бара через интервал времени."""
        if not self.is_connected or not self._controller:
            return

        await self.update_controller_once()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Функции

    async def update_controller_once(self, force=False, ctx=None) -> bool:
        """Обновляет бар один раз. Если `force = True`, удаляет и вызывает `edit_controller()`, также вам нужно передать `ctx`, чтобы бар корректно отправился."""
        try:
            if force:
                try:
                    await self._controller.delete()
                except BaseException:
                    pass

                return await self.edit_controller(ctx)

            await self._controller.edit(embed=await state(self))
        except Exception:
            return False

    async def edit_controller(self, ctx=None, embed=None, without_view=False):
        """Обновляет бар. Если нет, то посылает новый исходя из `def __init__()` или `ctx`"""
        if not embed:
            embed = await state(self)

        try:
            await self._controller.edit(
                embed=embed, view=None if without_view else Soundpad(player=self)
            )
        except BaseException:
            try:
                await self._controller.delete()
            except BaseException:
                pass
            try:
                self._controller = await self._webhook.send(
                    embed=embed,
                    username=self._username,
                    avatar_url=self._icon,
                    view=None if without_view else Soundpad(player=self),
                    wait=True,
                )
            except BaseException:
                try:
                    self._controller = await ctx.channel.send(
                        embed=embed,
                        view=None if without_view else Soundpad(player=self),
                    )
                except BaseException:
                    return

    async def pub(self, key: str, value: Any, **kwargs) -> None:
        """
        #### Отправитьсообщение в брокер

        #### `key: str`
        Ключ без гильдии

        #### `value: Any`
        Значение
        """

        kwargs["action"] = key
        kwargs["value"] = value

        await self.bot.redis.publish(f"player-{self.guild.id}", json.dumps(kwargs))

        # if not without_set:
        #     await self.redis.set(f"{key}-{self.guild.id}", json.dumps(value))

        # await self.redis.publish(
        #     f"noir-{self.guild.id}", json.dumps({"action": key, "value": value})
        # )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Переназначение play и stop

    async def play(
        self,
        track: persiktunes.Track,
        *,
        start: int = 0,
        end: Optional[int] = None,
        replace: bool = False,
        volume: int = None,
    ) -> None:
        await super().play(
            track, start=start, end=end, noReplace=not replace, volume=volume
        )

        await self.pub("play", track.model_dump_json(exclude=["ctx", "requester"]))

        if track.requester:
            db.metrics.add_last_track(
                track.model_dump_json(exclude=["ctx", "requester"]), track.requester.id
            )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Команды для js

    async def skip(self) -> None:
        if self.current:
            if self.queue.loop_mode.value != "track":
                track = self.queue.next()
                if track:
                    await self.play(track)

    async def prev(self) -> None:
        if self.current:
            if self.queue.loop_mode.value != "track":
                track = self.queue.prev()
                if track:
                    await self.play(track)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Стандартные команды, переписанные под пад и сокет

    async def set_pause(self, pause: Optional[bool] = None):
        if not self.current:
            return
        await super().set_pause(pause)
        await self.update_controller_once()
        await self.pub("pause", self._paused, position=self.position.__int__())

    # ==========================

    async def set_volume(self, volume: int) -> Coroutine[Any, Any, int]:
        value = await super().set_volume(volume)
        await self.update_controller_once()
        await self.pub("volume", value)

    async def volume_up(self) -> Coroutine[Any, Any, None]:
        if (self._volume + self._volume_step) >= 0 and (
            self._volume + self._volume_step
        ) <= 500:
            await self.set_volume(self._volume + self._volume_step)

    async def volume_down(self) -> Coroutine[Any, Any, None]:
        if (self._volume - self._volume_step) >= 0 and (
            self._volume - self._volume_step
        ) <= 500:
            await self.set_volume(self._volume - self._volume_step)

    # ==========================

    async def seek(self, position: int) -> Coroutine[Any, Any, int]:
        value = await super().seek(position)
        await self.update_controller_once()
        await self.pub("seek", value)

    async def destroy(self) -> Coroutine[Any, Any, None]:
        if self.update_controller.is_running():  # Stop if running
            self.update_controller.stop()

        try:
            await self.controller.delete()  # Delete text-controller
        except BaseException:
            pass

        await super().destroy()

        await self.pub("destroy", True)
        # await self.redis.delete(f"*{self.guild.id}")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Обновление плеера

    async def refresh_init(self, force=False):
        """Получает информацию с бд и переписывает `self`. В конце вызывается `update_controller_once(force=force)`"""
        params = self.bot.db.setup.get_setup(self.guild.id)

        if not params:
            return await self.update_controller_once(force=force)

        try:
            self._webhook = await self.bot.fetch_webhook(params["webhook"]["id"])
            self._username = params["webhook"].get("name", ...)
            self._icon = params["webhook"].get("icon", ...)

        except BaseException:
            self.bot.db.setup.webhook(self.guild.id)

        self.radio = params.get("24/7", False)

        self.dj = params.get("role")

        self._volume_step = params.get("volume_step", 25)

        self._disable_eq = params.get("disable_eq", False)

        try:
            self._color = int(params.get("color").replace("#", ""), base=16)
        except BaseException:
            pass

        await self.update_controller_once(force=force)

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
    # Переменные

    @property
    def is_radio(self) -> bool:
        """Стоит ли режим радио"""
        return self.radio

    @property
    def dj_role(self) -> int | None:
        """Возвращает массив с `roles` и `users`"""
        return self.dj

    @property
    def queue(self) -> NoirQueue:
        """Текущая очередь"""
        return self._queue

    # @property
    # def broker(self) -> Broker:
    #     """Брокер сокетов"""
    #     return self._broker

    @property
    def controller(self) -> disnake.WebhookMessage | disnake.Message:
        """Сообщение с саундбаром"""
        return self._controller

    @property
    def color(self) -> int:
        """Цвет плеера в `int`"""
        return self._color

    @property
    def webhook(self) -> disnake.Webhook | None:
        """Вебхук плеера (если есть)"""
        return self._webhook

    @property
    def disable_eq(self) -> bool:
        """Отключить эквалайзер"""
        return self._disable_eq

    @property
    def volume_step(self) -> int:
        """Шаг громкости"""
        return self._volume_step

    @property
    def current_build(self) -> dict | None:
        """Текущий билд трека"""
        return (
            build.track(
                self.current.info, self.current.track_type.value, self.current.thumbnail
            )
            if self.current
            else None
        )
