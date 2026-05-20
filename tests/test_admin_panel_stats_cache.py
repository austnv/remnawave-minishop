import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import bot.app.web.subscription_webapp  # noqa: F401
from bot.app.web.admin_api_impl import stats as stats_module


class AdminPanelStatsCacheTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        stats_module._ADMIN_PANEL_STATS_CACHES.clear()

    async def asyncTearDown(self):
        stats_module._ADMIN_PANEL_STATS_CACHES.clear()

    def _settings(self):
        return SimpleNamespace(
            ADMIN_PANEL_STATS_CACHE_TTL_SECONDS=15,
            REDIS_URL="redis://redis:6379/0",
            REDIS_KEY_PREFIX="shop",
        )

    def _panel_service(self):
        return SimpleNamespace(
            get_system_stats=AsyncMock(return_value={"users": {"totalUsers": 10}}),
            get_bandwidth_stats=AsyncMock(return_value={"current": 123}),
            get_nodes_statistics=AsyncMock(return_value={"nodes": []}),
            get_nodes_bandwidth_usage=AsyncMock(return_value={"topNodes": []}),
            get_nodes_online_lookups=AsyncMock(return_value={"byUuid": {}, "byName": {}}),
        )

    async def test_admin_panel_stats_are_cached_between_requests(self):
        settings = self._settings()
        panel_service = self._panel_service()
        cache_store = {}

        async def fake_get(_settings, key):
            return cache_store.get(key)

        async def fake_set(_settings, key, value, ttl):
            cache_store[key] = value

        with (
            patch("bot.infra.redis.cache_get_json", fake_get),
            patch("bot.infra.redis.cache_set_json", fake_set),
        ):
            first = await stats_module._load_admin_panel_stats(None, settings, panel_service)
            second = await stats_module._load_admin_panel_stats(None, settings, panel_service)

        self.assertEqual(first, second)
        panel_service.get_system_stats.assert_awaited_once()
        panel_service.get_bandwidth_stats.assert_awaited_once()
        panel_service.get_nodes_statistics.assert_awaited_once()
        panel_service.get_nodes_bandwidth_usage.assert_awaited_once()
        panel_service.get_nodes_online_lookups.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
