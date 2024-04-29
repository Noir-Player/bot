from redis.asyncio import Redis

from src.config import *

redis = Redis(host=HOST, port=PORT, password=PASS)
