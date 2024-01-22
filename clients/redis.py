from redis.asyncio import Redis
from config import *

redis = Redis(host=HOST, port=PORT, password=PASS)