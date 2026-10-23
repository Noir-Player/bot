from redis.asyncio import Redis

from .config import get_instance as get_config

instance = None


def get_instance():
    """Singleton getter"""
    global instance

    if instance is None:
        instance = Redis(host=get_config().redis_host, port=get_config().redis_port)

    return instance
