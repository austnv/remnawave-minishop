from datetime import datetime, timedelta, timezone

from bot.handlers.admin.sync_admin import (
    _coerce_panel_telegram_id,
    _description_matches,
    _subscription_update_delta,
)
from db.models import Subscription


def test_description_match_ignores_whitespace_shape():
    assert _description_matches("email@example.com username", "email@example.com\nusername")


def test_panel_telegram_id_is_coerced_to_int():
    assert _coerce_panel_telegram_id("12345") == 12345
    assert _coerce_panel_telegram_id("") is None


def test_subscription_update_delta_skips_unchanged_fields():
    end_date = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    subscription = Subscription(
        user_id=1,
        panel_user_uuid="panel-1",
        panel_subscription_uuid="sub-1",
        end_date=end_date,
        is_active=True,
        status_from_panel="ACTIVE",
    )

    assert (
        _subscription_update_delta(
            subscription,
            {
                "user_id": 1,
                "panel_user_uuid": "panel-1",
                "end_date": end_date + timedelta(milliseconds=500),
                "is_active": True,
                "status_from_panel": "ACTIVE",
            },
        )
        == {}
    )


def test_subscription_update_delta_returns_only_changed_fields():
    end_date = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    subscription = Subscription(
        user_id=1,
        panel_user_uuid="panel-1",
        panel_subscription_uuid="sub-1",
        end_date=end_date,
        is_active=True,
        status_from_panel="ACTIVE",
    )

    assert _subscription_update_delta(
        subscription,
        {
            "user_id": 2,
            "panel_user_uuid": "panel-1",
            "end_date": end_date + timedelta(seconds=2),
            "is_active": False,
            "status_from_panel": "EXPIRED",
        },
    ) == {
        "user_id": 2,
        "end_date": end_date + timedelta(seconds=2),
        "is_active": False,
        "status_from_panel": "EXPIRED",
    }
