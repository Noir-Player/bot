from typing import Any
from disnake.ext.commands import AutoShardedInteractionBot
from quart.blueprints import Blueprint
from quart import Quart

import asyncio


class Router(Blueprint):
    """Router for Noir Player"""

    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: str | None = None,
        static_url_path: str | None = None,
        template_folder: str | None = None,
        url_prefix: str | None = None,
        subdomain: str | None = None,
        url_defaults: dict | None = None,
        root_path: str | None = None,
        cli_group: str | None = ...,
    ) -> None:
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )

        self._bot: AutoShardedInteractionBot | None = None

    @property
    def bot(self) -> AutoShardedInteractionBot | None:
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

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


class App(Quart):
    """App for Noir Player"""

    def __init__(
        self,
        import_name: str,
        static_url_path: str | None = None,
        static_folder: str | None = "static",
        static_host: str | None = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str | None = "templates",
        instance_path: str | None = None,
        instance_relative_config: bool = False,
        root_path: str | None = None,
        bot: AutoShardedInteractionBot | None = None
    ) -> None:
        super().__init__(
            import_name,
            static_url_path,
            static_folder,
            static_host,
            host_matching,
            subdomain_matching,
            template_folder,
            instance_path,
            instance_relative_config,
            root_path,
        )

        self._bot: AutoShardedInteractionBot | None = bot

    @property
    def bot(self) -> AutoShardedInteractionBot | None:
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    def register_blueprint(self, blueprint: Router, **options: Any) -> None:
        blueprint.bot = self.bot
        return super().register_blueprint(blueprint, **options)
