from services.persiktunes import LoopMode, Player, Queue, Track
from services.persiktunes.models import *


class NoirQueue(Queue):
    def __init__(
        self,
        player: Player,
        max_size: int | None = None,
        *,
        overflow: bool = True,
        return_exceptions: bool = False,
        loose_mode: bool = False,
    ):
        super().__init__(
            max_size,
            overflow=overflow,
            return_exceptions=return_exceptions,
            loose_mode=loose_mode,
        )

        self.player = player

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Тулза для отображения очереди в redis

    async def update_state(self, action, value=None):
        await self.player.pub(action, value)

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
            "put", item.model_dump_json(exclude=["ctx", "requester"])
        )

    async def put_list(self, item: list) -> None:
        if self.is_full:
            return
        super().put_list(item)
        await self.update_state("put_list", len(item))

    async def put_at_index(self, index: int, item: Track) -> None:
        super().put_at_index(index, item)
        await self.update_state(
            "put",
            item.model_dump_json(exclude=["ctx", "requester"]),
        )

    async def put_next(self, item: Track) -> None:
        super().put_next(item)
        await self.update_state(
            "put_next",
            item.model_dump_json(exclude=["ctx", "requester"]),
        )

    async def put_auto(
        self,
        item: (
            LavalinkTrackLoadingResponse | LavaSearchLoadingResponse | Track | Playlist
        ),
        put_type: Literal["once", "tracks", "playlists", "mixes"] = "once",
    ) -> None:
        pass

    async def set_loop_mode(self, mode: LoopMode | None) -> None:
        if self._queue:
            self._loop_mode = mode
            await self.player.update_controller_once()
            await self.update_state("loop", str(self.loop_mode.value))

    async def remove(self, item_or_index: Track | int) -> None:
        await self.update_state(
            "remove", self.find_position(self._get_item(item_or_index))
        )
        super().remove(item_or_index)

    async def clear(self) -> None:
        await self.update_state("clear")
        return super().clear()
