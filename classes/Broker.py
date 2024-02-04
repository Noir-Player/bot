import json
import traceback
import asyncio
from typing import AsyncGenerator, AnyStr


class Broker:
    """Broker for manage connections"""

    def __init__(self, redis, channel) -> None:
        self.redis = redis
        self.channel: str = f'player-{channel}'
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    async def publish(self, message: AnyStr) -> None:
        """send message to all connections"""
        await self.redis.publish(self.channel, json.dumps(message))

    async def subscribe(self, event: asyncio.Event | None = None) -> AsyncGenerator[str, None]:
        """Subscribe for msgs"""
        await self.pubsub.subscribe(self.channel)

        if event:
            event.set()

        try:
            async for msg in self.pubsub.listen():
                yield json.loads(msg.get('data'))

        finally:
            await self.pubsub.close()
            print('closed [inside]')

    async def close(self):
        """Close pubsub"""
        await self.pubsub.close()
