from unittest import mock

from client.redis import MiddlewareSDKFacade
from client.redis.redis_conn import get_caching_data


def test_get_caching_data(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "mypassword")

    result = get_caching_data()

    assert result == {
        "CACHE_TYPE": "redis",
        "CACHE_REDIS_HOST": "127.0.0.1",
        "CACHE_REDIS_PORT": 6379,
        "CACHE_REDIS_PASSWORD": "mypassword",
        "CACHE_REDIS_URL": "redis://127.0.0.1:6379/0",
    }


@mock.patch("redis.client.Redis.ping", return_value=True)
def test_redis_status(mock_ping):
    redis_status = MiddlewareSDKFacade.cache.redis_status()

    assert redis_status == "up"
    mock_ping.assert_called_once()
