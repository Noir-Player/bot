import pomice
import json

from pomice import Track
from pomice.objects import Track
from pomice.queue import LoopMode

from utils.build import Build

build = Build()


class NoirQueue(pomice.Queue):
    def __init__(self, max_size: int | None = None, *, overflow: bool = True):
        super().__init__(max_size, overflow=overflow)

        """Первоначальная настройка очереди"""
        self._current_item: Track = None  # Текущий элемент

        """Дополнительно"""
        self._nonstop: bool = False  # Генерация потока
        self._loose: bool = False  # Сыпучая очередь

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Недо-инит

    def set_player(self, player):
        self.player = player

    def set_nonstop(self, value: bool):
        self._nonstop = value
        self.gen_nonstop()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Тулза для отображения очереди в redis

    async def update_state(self, action, value=None):
        await self.player.pub(action, value)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Поток для генерации треков

    async def nonstop(self) -> None:
        recs = await self.player.get_recommendations(
            track=self.player.current, ctx=self.player.current.ctx
        )

        if isinstance(recs, list):
            for rec in recs:
                await self.put(rec)

        elif isinstance(recs, pomice.Playlist):
            for rec in recs.tracks:
                await self.put(rec)

    def gen_nonstop(self):
        try:
            if self._nonstop and (
                    self.find_position(
                        self._current_item) +
                    1 >= self.count):
                self.player.bot.loop.create_task(self.nonstop())
        except BaseException:
            pass

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Мейн-коммуникация с вебом

    async def recieve(self):
        p = self.redis.pubsub()
        ch = await p.subscribe(f"app-{self.player.guild.id}")

        async for msg in p.listen():  # Прослушивание канала
            if (
                msg.get("type") == "message"
            ):  # Если тип - сообщение - десериализуем данные json
                data = json.loads(msg.get("data"))
            else:
                continue

            if data.get("type") == "queue":
                if data.get("action") == "loop":
                    if self.loop_mode == pomice.LoopMode.QUEUE:
                        await self.set_loop_mode(pomice.LoopMode.TRACK)
                    elif self.loop_mode == pomice.LoopMode.TRACK:
                        await self.disable_loop()
                    else:
                        await self.set_loop_mode(pomice.LoopMode.QUEUE)

                elif data.get("action") == "shuffle":
                    await self.shuffle()

                elif data.get("action") == "remove":
                    if self.player.current:
                        try:
                            await self.remove(self.player.current)
                            await self.player.play(self.next())
                        except BaseException:
                            pass

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Основные функции

    async def shuffle(self) -> None:
        super().shuffle()
        await self.update_state("shuffle")

    async def put(self, item: Track) -> None:
        if self.is_full:
            return
        super().put(item)
        await self.update_state(
            "put", build.track(item.info, item.track_type.value, item.thumbnail)
        )

    async def put_list(self, item: list) -> None:
        if self.is_full:
            return
        super().put_list(item)
        await self.update_state(
            "put_list", len(item)
        )

    async def put_at_index(self, index: int, item: Track) -> None:
        super().put_at_index(index, item)
        await self.update_state(
            "put",
            build.track(item.info, item.track_type.value, item.thumbnail),
            index=index,
        )

    async def set_loop_mode(self, mode: LoopMode) -> None:
        if self._queue:
            self._loop_mode = mode
            await self.player.update_bar_once()
            await self.update_state("loop", str(self.loop_mode.value))

    async def disable_loop(self) -> None:
        if self._queue:
            self._loop_mode = None
            await self.player.update_bar_once()
            await self.update_state("loop", None)

    async def remove(self, item_or_index: Track | int) -> None:
        await self.update_state(
            "remove", self.find_position(self._get_item(item_or_index))
        )
        super().remove(item_or_index)

    async def clear(self) -> None:
        await self.update_state("clear")
        return super().clear()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # GET-функции

    # def get(self) -> Track | None:
    #     """Следующий трек (исключая повтор) ИЛИ None"""
    #     if self.is_empty:
    #         return None # raise QueueEmpty("No items in the queue.")

    #     if self._loop_mode == LoopMode.TRACK: # вернуть текущий, если стоит повтор
    #         return self._current_item

    #     return self.next()

    # def next(self) -> Track | None:
    #     if self.is_empty:
    #         return None # raise QueueEmpty("No items in the queue.")

    #     if not self._current_item:
    #         self._current_item, self._last_index = self._queue[0], 0
    # return self._current_item if not self._loose else self._queue.pop(0)

    #     if self._last_index < self.count - 1: # последний индекс меньше индекса последнего элемента
    #         index = self._last_index + (1 if not self._loose else 0)
    #     else: # ласт индекс больше индекса последнего элемента
    #         if self.loop_mode == pomice.LoopMode.QUEUE: # если очередь повторяется, то возвращается первый элемент
    #             index = 0
    #         else:
    #             return None # в противном случае возвращается None

    #     self._current_item, self._last_index = self._queue[index], index # меняем текущий элемент и последний индекс
    #     self.gen_nonstop() # Генерация потока заранее
    # return self._current_item if not self._loose else self._queue.pop(index)
    # # возвращаем текущий элемент

    # def prev(self) -> Track | None:
    #     if self.is_empty:
    #         return None # raise QueueEmpty("No items in the queue.")

    #     if not self._current_item:
    #         self._current_item, self._last_index = self._queue[0], 0
    # return self._current_item if not self._loose else self._queue.pop(0)

    #     if self._last_index and self.count > self._last_index:
    #         index = self._last_index - 1 # предыдущий элемент
    #     else:
    #         return None # в противном случае нет предыдущего элемента

    #     self._current_item, self._last_index = self._queue[index], index # меняем текущий элемент и последний индекс
    #     self.gen_nonstop() # Генерация потока заранее
    # return self._current_item if not self._loose else self._queue.pop(index)
    # # возвращаем текущий элемент

    # def jump(self, position: int) -> Track:
    #     if self.is_empty:
    #         return None # raise QueueEmpty("No items in the queue.")

    #     if position < self.count and position >= 0: # индекс в пределах очереди
    #         self._current_item, self._last_index = self._queue[position], position # меняем текущий элемент и последний индекс
    #         self.gen_nonstop() # Генерация потока заранее
    #         return self._current_item if not self._loose else self._queue.pop(position) # возвращаем текущий элемент
    #     else:
    #         return None # невалидный индекс

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Переменные

    @property
    def is_nonstop(self) -> bool:
        """Режим потока"""
        return self._nonstop
