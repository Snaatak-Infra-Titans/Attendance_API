from unittest import mock

from client.redis import MiddlewareSDKFacade
from client.redis.redis_conn import get_caching_data


REDIS_CONFIG = """
redis:
  host: 127.0.0.1
  port: 6379
  password: mypassword
"""


@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=REDIS_CONFIG,
)
def test_get_caching_data(mock_open, monkeypatch):
    monkeypatch.setenv("CONFIG_FILE", "config.yaml")

    result = get_caching_data()

    assert result == {
        "CACHE_TYPE": "redis",
        "CACHE_REDIS_HOST": "127.0.0.1",
        "CACHE_REDIS_PORT": 6379,
        "CACHE_REDIS_URL": "redis://127.0.0.1:6379/0",
    }


@mock.patch("redis.client.Redis.ping", return_value=True)
@mock.patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data=REDIS_CONFIG,
)
def test_redis_status(mock_open, mock_ping, monkeypatch):
    monkeypatch.setenv("CONFIG_FILE", "config.yaml")

    redis_status = MiddlewareSDKFacade.cache.redis_status()

    assert redis_status == "up"
    mock_ping.assert_called_once()
