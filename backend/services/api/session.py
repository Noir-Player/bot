import json
import uuid

from redis.asyncio import Redis

from config import *


class Sessions:
    """Класс для работы с сессиями"""

    def __init__(self, salt: str, prefix: str = "session_") -> None:
        """
        Initializes the class with the given salt and an optional prefix.

        Parameters:
            salt (str): The salt to be used for initialization.
            prefix (str, optional): The prefix for the session keys. Defaults to "session_".

        Returns:
            None
        """
        self.redis = Redis(host=HOST, port=PORT, password=PASS)
        self.prefix = prefix
        self.salt = salt

    def _get_key(self, token: str) -> str:
        return uuid.uuid5(uuid.NAMESPACE_X500, f"{token}{self.salt}").__str__()

    async def _id(self, token: str) -> int | None:
        """
        An asynchronous function that takes an string token as input and returns an integer ID or None.
        Retrieves a user from redis cache based on the token, and returns the user's id if found, otherwise returns None.
        """
        user = await self.redis.get(f"{self.prefix}{self._get_key(token)}")

        if not user:
            return None

        return json.loads(user)["user"]["id"]

    async def get(self, token: str) -> dict:
        """
        Asynchronously retrieves a dictionary using the provided token.

        Args:
            token (str): The token used to retrieve the dictionary.

        Returns:
            dict: The dictionary retrieved using the token.
        """
        return json.loads(await self.redis.get(f"{self.prefix}{self._get_key(token)}"))

    async def verify(self, token: str) -> int:
        """
        Verify the token and return the corresponding ID.

        Parameters:
            token (str): The token to be verified.

        Returns:
            int: The ID associated with the token.

        Raises:
            ValueError: If the token is invalid.
        """
        id = await self._id(token)

        if not id:
            raise ValueError("Invalid token")

        return id

    async def push(self, token: str, data: dict) -> None:
        """
        Asynchronously updates a session with the given id using the provided data.

        Args:
            id (int): The id of the session to be updated.
            data (dict): The data to update the session with.

        Returns:
            None
        """
        session = await self.get(token)
        if not session:
            return

        session.update(data)

        await self.redis.set(
            f"{self.prefix}{self._get_key(token)}", json.dumps(session)
        )

    async def delete(self, token: str) -> None:
        """
        Asynchronous function to delete a token from the specified Redis key.

        Args:
            token (str): The token to be deleted.

        Returns:
            None
        """
        await self.redis.delete(f"{self.prefix}{self._get_key(token)}")

    async def set(self, token: str, data: dict, expireAt: int = None) -> None:
        """
        Asynchronously sets a value in the cache with the given token and data. Optionally, it can set an expiration time as seconds for the data.

        Args:
            token (str): The token used to identify the data.
            data (dict): The data to be stored in the cache.
            expireAt (int, optional): The expiration time for the data in seconds. Defaults to None.

        Returns:
            None
        """
        if not expireAt:
            return await self.redis.set(
                f"{self.prefix}{self._get_key(token)}", json.dumps(data)
            )

        await self.redis.setex(
            f"{self.prefix}{self._get_key(token)}", expireAt, json.dumps(data)
        )
