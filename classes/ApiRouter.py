from enum import Enum
from typing import List, Sequence
from disnake.ext.commands import AutoShardedInteractionBot
from fastapi import APIRouter

import asyncio

from fastapi.params import Depends

from clients.database import Database
from clients.session  import Sessions


class NOIRouter(APIRouter):
    """Router for Noir Player, include bot instanse"""

    def __init__(self,
                 *,
                 prefix: str = "",
                 tags: List[str | Enum] | None = None,
                 dependencies: Sequence[Depends] | None = None) -> None:
        super().__init__(prefix=prefix, tags=tags, dependencies=dependencies)

        self._bot: AutoShardedInteractionBot | None = None
        self._db = Database()
        self._salt = "wtfwheremysaltidiot"

        self._session: Sessions | None = None # if salt has not been set

    @property
    def bot(self) -> AutoShardedInteractionBot | None:
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    @property
    def salt(self) -> str:
        return self._salt

    @salt.setter
    def salt(self, value):
        self._salt = value
        self._session = Sessions(salt=value)

    @property
    def session(self):
        return self._session

    @property
    def db(self) -> Database:
        return self._db

    def execute(self, func, timeout=None):
        try:
            return asyncio.run_coroutine_threadsafe(
                func, self.bot.loop).result(timeout)
        except asyncio.TimeoutError:
            pass

    async def coroexecute(self, func):
        try:
            return asyncio.run_coroutine_threadsafe(func, self.bot.loop)
        except asyncio.TimeoutError:
            pass

    async def run_independent(self, func, *args, **kwargs):
        if asyncio.coroutines.iscoroutinefunction(func):
            return await self.coroexecute(func(*args, **kwargs))

        return await asyncio.to_thread(func, *args, **kwargs)
