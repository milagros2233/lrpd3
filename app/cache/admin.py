"""Cliente Redis síncrono inicializado desde la URL definida en las variables de entorno."""

import os
import redis
from redis.connection import SSLConnection
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

pool = redis.ConnectionPool.from_url(
    REDIS_URL, connection_class=SSLConnection, decode_responses=True
)

redis_connection = redis.Redis(connection_pool=pool)
print(redis_connection.ping())
