import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from config.settings import Settings
from bot.services.tariff_worker import TariffTrafficWorker
from bot.utils.date_utils import month_start


class TariffWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_monthly_reset_triggers_on_calendar_change_before_30_days(self):
        settings = Settings(
            _env_file=None,
            BOT_TOKEN="token",
            POSTGRES_USER="app_user",
            POSTGRES_PASSWORD="app_password",
        )
        panel_service = AsyncMock()
        panel_service.reset_user_traffic = AsyncMock(return_value=True)
        panel_service.add_users_to_internal_squad = AsyncMock(return_value=True)
        subscription_service = SimpleNamespace()
        worker = TariffTrafficWorker(
            settings=settings,
            session_factory=SimpleNamespace(),
            panel_service=panel_service,
            subscription_service=subscription_service,
        )

        now = datetime.now(timezone.utc)
        current_month_start = month_start(now)
        previous_month_anchor = current_month_start - timedelta(days=2)
        sub = SimpleNamespace(
            subscription_id=1,
            panel_user_uuid="panel-uuid",
            period_start_at=previous_month_anchor,
            end_date=now + timedelta(days=10),
            traffic_used_bytes=123,
            traffic_limit_bytes=456,
            topup_balance_bytes=0,
            is_throttled=False,
            status_from_panel="ACTIVE",
        )
        tariff = SimpleNamespace(billing_model="period", squad_uuids=["squad-1"])

        session = object()

        with patch(
            "bot.services.tariff_worker.subscription_dal.update_subscription",
            new=AsyncMock(),
        ) as update_subscription, patch(
            "bot.services.tariff_worker.tariff_dal.clear_period_warnings",
            new=AsyncMock(),
        ) as clear_period_warnings:
            await worker._maybe_reset_period(session, sub, tariff, used=123)

        panel_service.reset_user_traffic.assert_awaited_once_with("panel-uuid")
        update_subscription.assert_awaited_once()
        update_payload = update_subscription.await_args.args[2]
        self.assertEqual(update_payload["period_start_at"], current_month_start)
        self.assertEqual(update_payload["traffic_used_bytes"], 0)
        clear_period_warnings.assert_awaited_once_with(session, 1)
