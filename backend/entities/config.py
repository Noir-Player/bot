"""Config entity `BaseSettings`"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):

    mode: Literal["dev", "prod"]
    """dev or prod"""

    token: str
    """Bot token"""

    sync_commands: bool
    """Syncing commands parameters"""

    shard_count: int
    """Shard count"""

    activity_name: str = "noirplayer.su"
    """Activity name"""
    activity_status: Literal[-1, 0, 1, 2, 3, 4, 5] = 2
    """Activity status"""

    redis_host: str
    """Redis host"""
    redis_port: int
    """Redis port"""

    mongodb_host: str
    """MongoDB host"""
    mongodb_port: int
    """MongoDB port"""

    lavalink_host: str
    """Lavalink host"""
    lavalink_port: int
    """Lavalink port"""
    lavalink_password: str
    """Lavalink password"""

    loglevel: Literal["debug", "info", "warning", "error"] = "info"
    """Log level. Default: info"""

    spotify_client_id: str
    """Spotify client id"""
    spotify_client_secret: str
    """Spotify client secret"""

    support_server_id: int
    """Support server id"""
    support_server_invite: str
    """Support server invite url"""
    logs_channel_id: int
    """Logs channel id"""

    model_config = SettingsConfigDict(env_file=".env")


# =============================================================================

instance = None


def get_instance():
    """Singleton getter"""
    global instance
    if instance is None:
        instance = BotConfig()
    return instance
