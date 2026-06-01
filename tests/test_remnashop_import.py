from datetime import datetime, timezone

from scripts.import_legacy import (
    remnashop_months_from_plan_snapshot,
    remnashop_pricing_amount,
    remnashop_pricing_currency,
    remnashop_sale_mode,
    remnashop_traffic_gb_to_bytes,
    remnashop_transaction_status,
)


def test_remnashop_pricing_helpers_read_final_amount_and_currency():
    pricing = {"final_amount": "199.50", "currency": "rub"}

    assert remnashop_pricing_amount(pricing) == 199.5
    assert remnashop_pricing_currency(pricing) == "RUB"


def test_remnashop_traffic_limit_is_converted_from_gib():
    assert remnashop_traffic_gb_to_bytes(10) == 10 * 1024**3
    assert remnashop_traffic_gb_to_bytes(None) is None


def test_remnashop_status_and_sale_mode_mapping_matches_current_payment_model():
    assert remnashop_transaction_status("COMPLETED", "YOOKASSA") == "succeeded"
    assert remnashop_transaction_status("PENDING", "WATA") == "pending_wata"
    assert remnashop_transaction_status("CANCELED", "WATA") == "canceled"
    assert remnashop_sale_mode("NEW") == "subscription"
    assert remnashop_sale_mode("RENEW") == "subscription"
    assert remnashop_sale_mode("CHANGE") == "tariff_upgrade"


def test_remnashop_plan_months_prefers_snapshot_then_dates():
    assert remnashop_months_from_plan_snapshot({"duration_days": 90}) == 3
    assert remnashop_months_from_plan_snapshot({"months": 12}) == 12
    assert (
        remnashop_months_from_plan_snapshot(
            {},
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            expire_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )
        == 3
    )
