import asyncio
import configparser
import logging
import random
import traceback
from typing import Any

# import sdc_api_py
import disnake
import hypercorn
import quart
from disnake.ext import commands
from hypercorn.asyncio import serve
from redis.asyncio import Redis
from spotipy.oauth2 import SpotifyClientCredentials

import _logging
import services.api as api
import services.persiktunes as persiktunes
from config import *
from helpers.ex_load import cogsLoad, cogsReload
from objects.exceptions import errors

# from services.app import setup
from services.database.core import Database
from services.ui.embed import EmbedBuilder

# import api


class NoirBot(commands.AutoShardedInteractionBot):
    """Кастомный класс Noir с включенными в него table, node и т.д."""

    def __init__(self, *, config: str = "noir.properties", debug: bool = False) -> None:
        # Debug or not
        self._debug = debug

        # Config
        self._config = configparser.ConfigParser()
        self._config.read(config)

        # Intents
        intents = disnake.Intents.default()
        intents.members = True

        # Sync flags
        sync = (
            commands.CommandSyncFlags.all()
            if (
                self._config.getboolean("launch", "sync_commands")
                if not self._debug
                else self._config.getboolean("altlaunch", "sync_commands")
            )
            else commands.CommandSyncFlags.none()
        )

        super().__init__(
            # sync_commands=True,
            command_sync_flags=sync,
            shard_count=(
                self._config.getint("launch", "shard_count")
                if not self._debug
                else self._config.getint("altlaunch", "shard_count")
            ),
            chunk_guilds_at_startup=False,
            status=disnake.Status.idle,
            activity=disnake.Activity(
                name="noirplayer.su", type=disnake.ActivityType.listening
            ),
            intents=intents,
        )

        # Pool
        self._pool = persiktunes.NodePool()

        # MongoDB
        self._db = Database()

        # Redis
        self._redis = Redis(host=HOST, port=PORT, password=PASS)

        # App server
        # self._app = setup(bot=self)

        # Set logging
        self._log = _logging.get_logger("bot")

        # Embedding
        self._embedding = EmbedBuilder()

        # Setup
        self.setup()

        # Connect lavalink
        self.loop.create_task(self.connect_nodes())

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Setup

    def setup(self):
        self._log.info("Loading cogs")

        cogsLoad(self)

        if self._config.getboolean("launch", "sdc_api_enabled"):
            self._log.info("Sending data to SD.C")
            try:
                data = sdc_api_py.Bots(self, self._config.get("tokens", "sdc_token"))
                data.create_loop()
            except BaseException:
                pass
            else:
                self._log.debug("Loop created")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Api

    def serve_api(self):

        self._log.info("Loading FastAPI")

        self._app = api.__init__(bot=self)

        if not self._debug:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5000"]
            config.use_reloader = True

            self._log.info("Run in prodaction")

            asyncio.run(serve(self._app, config))

        else:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5001"]
            config.use_reloader = True
            config.debug = True

            self._log.info("Run in debug")

            asyncio.run(serve(self._app, config))

    # -------------------------------------------------------------------------------------------------------------------------------------
    # App

    def serve_app(self):

        self._log.info("Loading Quart")

        if not self._debug:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5000"]
            config.use_reloader = True

            self._log.info("Run in prodaction")

            asyncio.run(serve(self.app, config))

        else:
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:5001"]
            config.use_reloader = True
            config.debug = True

            self._log.info("Run in debug")

            asyncio.run(serve(self.app, config))

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Lavalink connection

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        self._log.debug("Waiting for ready...")

        await self.wait_until_ready()

        self._log.info("Starting nodes")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        async def _set_resume_key(key: str | None = None):
            self.log.debug(f"Setting resume key: {key} (expiring in 60 seconds)")
            if key:
                await self.redis.set("resume_key", key)
            else:
                await self.redis.delete("resume_key")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        key = await self.redis.get("resume_key")
        if key:
            key = key.decode("utf-8")

        async def _get_resume_key():
            self.log.debug(f"Getting resume key")
            key = await self.redis.get("resume_key")
            if key:
                return key.decode("utf-8")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        async def _get_player_channel(guild_id: int):
            channel_id = await self.redis.get(f"player_guild-{guild_id}")
            if channel_id:
                return await self.fetch_channel(channel_id.decode("utf-8"))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        async def _set_player_channel(player, channel_id: int | None = None):
            if channel_id:
                await self.redis.set(f"player_guild-{player.guild.id}", channel_id)
            else:
                await self.redis.delete(f"player_guild-{player.guild.id}")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        try:
            self._node = await self._pool.create_node(
                bot=self,
                host=self._config.get("lavapass", "host"),
                port=self._config.getint("lavapass", "port"),
                password=self._config.get("lavapass", "pass"),
                identifier="Noir",
                log_level=logging.DEBUG,
                set_resume_key=_set_resume_key,
                get_resume_key=_get_resume_key,
                get_player_channel=_get_player_channel,
                set_player_channel=_set_player_channel,
                spotify_credentials=SpotifyClientCredentials(
                    client_id=self._config.get("spotify", "client_id"),
                    client_secret=self._config.get("spotify", "client_secret"),
                ),
            )

        except Exception as e:
            return self._log.error(
                f"Node was not created: {e}\n{traceback.format_exc()}"
            )

        self._log.info("Node created")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Events

    async def on_ready(self):
        self._log.info(f"Starting as {self.user} (ID: {self.user.id})")

        self._log.info("Player is ready")

    async def on_shard_connect(self, id):
        self._log.debug(f"Player connected | {id}")

    async def _on_slash_command_error(self, inter: disnake.Interaction, error):
        if error is commands.CommandError or error is commands.CommandInvokeError:
            e = errors.get(error.__cause__.__class__.__name__, "Ошибка")
        else:
            e = errors.get(error.__class__.__name__, "Ошибка")
        await inter.send(
            embed=self.embedding.get(
                {
                    "name": "`исходные данные:`",
                    "value": f"||```diff\n+ {e}\n- {error.__cause__}```||",
                },
                title=f"🟠 | {e}",
                description=random.choice(errors["ShortResponses"]),
                color="warning",
            ),
            ephemeral=True,
            components=[
                disnake.ui.Button(
                    style=disnake.ButtonStyle.url,
                    label="Support server",
                    url="https://discord.gg/ua4kpgzpWJ",
                )
            ],
        )

        self._log.error(f"Slash command error: {error}\n{traceback.format_exc()}")

    async def _on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        self._log.error(
            f"Exception in event_method {event_method}\n{traceback.format_exc()}"
        )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Run & Stop

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass  # TODO: add graceful shutdown
            # self.loop.run_until_complete(self.stop())
            # cancel all tasks lingering

    def start(self):
        if self._debug:
            return super().start(self._config.get("altsecrets", "token"))
        return super().start(self._config.get("secrets", "token"))

    async def stop(self) -> None:
        await self.node.disconnect()
        await self.close()
        self.loop.close()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Extensions

    def exload(self, path: None | str = None) -> None:
        """Load extensions in `/cogs`"""
        cogsLoad(self) if not path else self.load_extension(path)

    def exreload(self, path: None | str = None) -> None:
        """Reload extensions in `/cogs`"""
        cogsReload(self) if not path else self.reload_extension(path)

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Properties

    @property
    def pool(self) -> persiktunes.NodePool:
        """persiktunes.NodePool"""
        return self._pool

    @property
    def node(self) -> persiktunes.Node:
        """persiktunes.Node"""
        return self._pool.get_node()

    @property
    def db(self) -> Database:
        """Database class"""
        return self._db

    @property
    def redis(self) -> Redis:
        """Redis class"""
        return self._redis

    @property
    def app(self) -> quart.Quart:
        """App class"""
        return self._app

    @property
    def log(self) -> logging.Logger:
        """Logger class"""
        return self._log

    @property
    def embedding(self) -> EmbedBuilder:
        """EmbedBuilder class"""
        return self._embedding
