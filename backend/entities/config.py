"""Config entity `BaseSettings`"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):

    version: str = "0.1.0"
    """Version (for database)"""

    mode: Literal["dev", "prod"] = "dev"
    """dev or prod"""

    token: str
    """Bot token"""

    sync_commands: bool = True
    """Syncing commands parameters"""

    shard_count: int = 1
    """Shard count"""

    activity_name: str = "noirplayer.su"
    """Activity name"""
    activity_status: Literal[-1, 0, 1, 2, 3, 4, 5] = 2
    """Activity status"""

    redis_host: str = "redis"
    """Redis host"""
    redis_port: int = 6379
    """Redis port"""

    mongodb_host: str = "database"
    """MongoDB host"""
    mongodb_port: int = 27017
    """MongoDB port"""

    lavalink_host: str = "lavalink"
    """Lavalink host"""
    lavalink_port: int = 2333
    """Lavalink port"""
    lavalink_password: str = "youshallnotpass"
    """Lavalink password"""

    loglevel: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    """Log level. Default: info"""

    spotify_client_id: str | None = None
    """Spotify client id"""
    spotify_client_secret: str | None = None
    """Spotify client secret"""

    support_server_id: int | None = None
    """Support server id"""
    support_server_invite: str | None = None
    """Support server invite url"""
    logs_channel_id: int | None = None
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
