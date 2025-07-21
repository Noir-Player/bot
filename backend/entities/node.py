"""
Node entity `NoirNode`
"""

import traceback

from _logging import get_logger, logging
from services.persiktunes import Node
from spotipy import SpotifyClientCredentials

from .config import get_instance as get_config
from .pool import get_instance as get_pool

# from .redis import get_instance as get_redis

log = get_logger("node")


async def connect(bot) -> Node | None:
    """Connect to Lavalink Nodes."""

    log.info("Starting nodes")

    # TODO
    # resuming key if exists
    # key = await get_redis().get("resume_key")
    # if key:
    #     key = key.decode("utf-8")

    try:
        instance = await get_pool().create_node(
            bot=bot,
            host=get_config().lavalink_host,
            port=get_config().lavalink_port,
            password=get_config().lavalink_password,
            identifier="Noir_Main",
            log_level=logging._nameToLevel[get_config().loglevel],  # type: ignore
            spotify_credentials=SpotifyClientCredentials(
                client_id=get_config().spotify_client_id,
                client_secret=get_config().spotify_client_secret,
            ),
        )

    except Exception as e:
        return log.error(f"Node was not created: {e}\n{traceback.format_exc()}")

    log.info("Node created")

    return instance


# =============================================================================

instance = None


async def create_node(bot) -> bool:
    """
    If successful, returns `True`
    """
    global instance
    if instance is None:
        instance = await connect(bot)

    return bool(instance)


# =============================================================================


def get_instance():
    global instance
    if not instance:
        raise Exception("Node is not connected")

    return instance
