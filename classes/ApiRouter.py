from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union
from disnake.ext.commands import AutoShardedInteractionBot
from fastapi import APIRouter

import asyncio

from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp, Lifespan


class NOIRouter(APIRouter):
    """Router for Noir Player, include bot instanse"""
    def __init__(self, *, prefix: str = "", tags: List[str | Enum] | None = None, dependencies: Sequence[Depends] | None = None) -> None:
        super().__init__(prefix=prefix, tags=tags, dependencies=dependencies)

        self._bot: AutoShardedInteractionBot | None = None


    @property
    def bot(self) -> AutoShardedInteractionBot | None:
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    def execute(self, func, timeout = None):
        try:
            return asyncio.run_coroutine_threadsafe(func, self.bot.loop).result(timeout)
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