import json

from clients.redis import redis

class Sessions:
    """Класс для работы с сессиями"""


    def __init__(self, prefix="session_") -> None:
        self.redis = redis
        self.prefix = prefix

    async def get(self, id: int) -> dict:
        return json.loads(
            await self.redis.get(f"{self.prefix}{id}")
            )
    
    async def push(self, id: int, data: dict) -> None:
        session = await self.get(id)
        if not session:
            return
        
        session.update(data)

        await redis.set(f"{self.prefix}{id}", json.dumps(session))
    
    async def pop(self, id: int) -> dict:
        return json.loads(
            await self.redis.getdel(f"{self.prefix}{id}")
            )

    async def set(self, id: int, data: dict, expireAt: int = None) -> None:
        if not expireAt:
            return await self.redis.set(f"{self.prefix}{id}", json.dumps(data))

        await self.redis.setex(f"{self.prefix}{id}", expireAt, json.dumps(data))