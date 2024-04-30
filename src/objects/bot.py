import asyncio
import configparser
import logging
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
from helpers.dump import Dump as Build
from helpers.embeds import type_embed
from helpers.ex_load import cogsLoad, cogsReload
from services.app import setup
from services.database.core import Database
from src.config import *

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

        # Build util
        self._build = Build()

        # App server
        self._app = setup(bot=self)

        # Jsons
        # self._errors = json.load(open("data/errors.json", "r", encoding="utf-8"))
        # self._hello = json.load(open("data/embeds/hello.json", "r", encoding="utf-8"))
        # self._help = json.load(open("data/embeds/help.json", "r", encoding="utf-8"))

        # Set logging
        self._log = _logging.get_logger("bot")

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
    # App

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

        try:
            self._node = await self._pool.create_node(
                bot=self,
                host=self._config.get("lavapass", "host"),
                port=self._config.getint("lavapass", "port"),
                password=self._config.get("lavapass", "pass"),
                identifier="Noir",
                log_level=logging.INFO,
                spotify_credentials=SpotifyClientCredentials(
                    client_id=self._config.get("spotify", "client_id"),
                    client_secret=self._config.get("spotify", "client_secret"),
                ),
            )

        except Exception as e:
            traceback.print_exc()
            return self._log.error(f"Node was not created: {e}")

        self._log.info("Node created")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Events

    async def on_ready(self):
        self._log.info(f"Starting as {self.user} (ID: {self.user.id})")

        self._log.info("Player is ready")

        if not self.pool.node_count:
            return

        self._log.debug("Checking for dead players...")

        for player in list(self.node.players.values()):
            if player.is_dead or not player.is_connected:
                try:
                    await player.destroy()
                except BaseException:
                    self._log.debug(f"Player {player} is not cleaned")

        self._log.debug("Cleanup done")

    async def on_shard_connect(self, id):
        self._log.debug(f"Player connected | {id}")

    async def on_slash_command_error(self, inter: disnake.Interaction, error):
        if error is commands.CommandError or error is commands.CommandInvokeError:
            e = self._errors.get(
                error.__cause__.__class__.__name__, "Неизвестная ошибка. Простите..."
            )
        else:
            e = self._errors.get(
                error.__class__.__name__, "Неизвестная ошибка. Простите..."
            )
        await inter.send(
            embed=type_embed(
                "error", f"```diff\n- {e}```\n||```diff\n- {error}```||"
            ),  # \n*Исходное сообщение об ошибке*: ||```Текст: {error.__cause__}\nИмя ошибки: {error.__cause__.__class__.__name__}```||"),
            ephemeral=True,
            components=[
                disnake.ui.Button(
                    style=disnake.ButtonStyle.url,
                    label="report",
                    url="https://discord.gg/ua4kpgzpWJ",
                )
            ],
        )

        self._log.error(f"Slash command error: {error}")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        self._log.error(f"Exception in event_method {event_method}")

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Run & Stop

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            self.stop()
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
    def build(self) -> Build:
        """Build class"""
        return self._build
