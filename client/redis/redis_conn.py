"""
Module for Redis data and interface
"""

import os
import redis


def get_caching_data():
    """Function to get cache config for redis cache"""

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", "")

    config_dict = {
        "CACHE_TYPE": "redis",
        "CACHE_REDIS_HOST": redis_host,
        "CACHE_REDIS_PORT": redis_port,
        "CACHE_REDIS_PASSWORD": redis_password,
        "CACHE_REDIS_URL": f"redis://{redis_host}:{redis_port}/0"
    }

    return config_dict


class CoreRedisClient:
    """Class for defining the structure of Redis database"""

    def __init__(self):

        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True
        )

    def redis_status(self):
        """Function for getting the health of redis"""

        try:
            self.client.ping()
            return "up"

        except redis.ConnectionError:
            return "down"