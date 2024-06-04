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

        self.api = player.node.rest.abstract_search

        self.player = player

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Тулза для отображения очереди в redis

    async def update_state(self, action, value=None):
        await self.player.pub(action, value)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Основные функции

    async def put_relayted(self, item: Track, limit: int = 10) -> None:
        async for track in self.api.default.ongoing(item, limit):  # type: ignore
            await self.put(track)

    def _get(self) -> Track | None:
        if self.loose_mode and self.count <= 1:
            self.player.bot.loop.create_task(self.put_relayted(self._current_item))
        if not self.count:
            return
        return super()._get()

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

    async def put_list(self, item: List[Track]) -> None:
        if self.is_full:
            return
        super().put_list(item)
        await self.update_state(
            "put_list", [i.model_dump_json(exclude=["ctx", "requester"]) for i in item]
        )

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
        put_type: Literal["auto", "once", "tracks", "playlists", "mixes"] = "auto",
    ) -> None:
        if put_type == "auto":
            if isinstance(item, LavalinkTrackLoadingResponse):
                if item.loadType == "track":
                    await self.put(item.data)
                elif item.loadType == "playlist":
                    await self.put_list(item.data.tracks)
                elif item.loadType == "search":
                    await self.put(item.data[0])
                else:
                    return False
            elif isinstance(item, LavaSearchLoadingResponse):
                await self.put(item.tracks[0])
            elif isinstance(item, (Playlist, Album)):
                await self.put_list(item.tracks)
            elif isinstance(item, Track):
                await self.put(item)
            elif isinstance(item, list):
                return await self.put_auto(item[0])
            else:
                return False

    async def start_autoplay(self, item: Track) -> None:
        if item.info.sourceName != "youtube":
            return
        if item != self.player.current:
            await self.player.play(item, noReplace=False)
        self._loose_mode = True
        await self.clear()
        await self.put_relayted(item)

    async def stop_autoplay(self) -> None:
        self._loose_mode = False

    async def set_loop_mode(self, mode: LoopMode | None = None) -> None:
        if self._queue:
            self._loop_mode = mode
            await self.player.update_controller_once()
            await self.update_state(
                "loop", str(self.loop_mode.value if self.loop_mode else None)
            )

    async def remove(self, item_or_index: Track | int) -> None:
        await self.update_state(
            "remove", self.find_position(self._get_item(item_or_index))
        )
        super().remove(item_or_index)

    async def clear(self) -> None:
        await self.update_state("clear")
        return super().clear()
