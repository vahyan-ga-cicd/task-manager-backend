import redis
from app.config.settings import REDIS_HOST, REDIS_PORT

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)