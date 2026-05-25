import asyncio
import json
from types import SimpleNamespace

from bot.payment_providers import wata
from bot.payment_providers.wata import WataConfig, WataService


class _FakeRequest:
    def __init__(self, payload):
        self.headers = {}
        self.remote = "127.0.0.1"
        self._raw_body = json.dumps(payload).encode("utf-8")

    async def read(self):
        return self._raw_body


class _FakeSession:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def __call__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1


def _payment(**overrides):
    values = {
        "payment_id": 465,
        "user_id": 748116183,
        "status": "pending_wata",
        "amount": 100.0,
        "provider_payment_id": "link-id",
        "purchased_gb": None,
        "subscription_duration_months": 1,
        "sale_mode": "subscription",
        "user": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _service(session):
    settings = SimpleNamespace(
        DEFAULT_CURRENCY_SYMBOL="RUB",
        DEFAULT_LANGUAGE="ru",
        traffic_sale_mode=False,
        trusted_proxies=[],
    )
    return WataService(
        bot=SimpleNamespace(),
        settings=settings,
        config=WataConfig(
            ENABLED=True,
            API_TOKEN="token",
            WEBHOOK_VERIFY_SIGNATURE=False,
            TRUSTED_IPS="",
        ),
        i18n=SimpleNamespace(),
        async_session_factory=session,
        subscription_service=SimpleNamespace(),
        referral_service=SimpleNamespace(),
        default_return_url="test_bot",
    )


def test_wata_created_webhook_returns_ok_and_persists_transaction_id(monkeypatch):
    session = _FakeSession()
    payment = _payment()
    updates = []

    async def lookup_payment(_session, *, order_id_raw=None, provider_payment_id=None):
        assert _session is session
        assert order_id_raw == "465"
        assert provider_payment_id == "tx-1"
        return payment

    async def update_provider_payment_and_status(
        _session,
        payment_id,
        provider_payment_id,
        status,
    ):
        updates.append((payment_id, provider_payment_id, status))

    monkeypatch.setattr(wata, "lookup_payment_by_order_or_provider_id", lookup_payment)
    monkeypatch.setattr(
        wata.payment_dal,
        "update_provider_payment_and_status",
        update_provider_payment_and_status,
    )

    response = asyncio.run(
        _service(session).webhook_route(
            _FakeRequest(
                {
                    "transactionStatus": "Created",
                    "transactionId": "tx-1",
                    "orderId": "465",
                    "amount": 100,
                    "currency": "RUB",
                }
            )
        )
    )

    assert response.status == 200
    assert updates == [(465, "tx-1", "pending_wata")]
    assert session.commits == 1
    assert session.rollbacks == 0


def test_wata_created_webhook_can_find_payment_by_payment_link_id(monkeypatch):
    session = _FakeSession()
    payment = _payment()
    lookup_calls = []
    updates = []

    async def lookup_payment(_session, *, order_id_raw=None, provider_payment_id=None):
        lookup_calls.append((order_id_raw, provider_payment_id))
        if provider_payment_id == "link-id":
            return payment
        return None

    async def update_provider_payment_and_status(
        _session,
        payment_id,
        provider_payment_id,
        status,
    ):
        updates.append((payment_id, provider_payment_id, status))

    monkeypatch.setattr(wata, "lookup_payment_by_order_or_provider_id", lookup_payment)
    monkeypatch.setattr(
        wata.payment_dal,
        "update_provider_payment_and_status",
        update_provider_payment_and_status,
    )

    response = asyncio.run(
        _service(session).webhook_route(
            _FakeRequest(
                {
                    "transactionStatus": "Created",
                    "transactionId": "tx-1",
                    "paymentLinkId": "link-id",
                    "amount": 100,
                    "currency": "RUB",
                }
            )
        )
    )

    assert response.status == 200
    assert lookup_calls == [(None, "tx-1"), (None, "link-id")]
    assert updates == [(465, "tx-1", "pending_wata")]
    assert session.commits == 1


def test_wata_known_payment_with_unknown_status_still_acknowledges_webhook(monkeypatch):
    session = _FakeSession()
    payment = _payment(provider_payment_id="tx-1")

    async def lookup_payment(_session, *, order_id_raw=None, provider_payment_id=None):
        return payment

    async def update_provider_payment_and_status(*args, **kwargs):
        raise AssertionError("unknown statuses must not mutate payment state")

    monkeypatch.setattr(wata, "lookup_payment_by_order_or_provider_id", lookup_payment)
    monkeypatch.setattr(
        wata.payment_dal,
        "update_provider_payment_and_status",
        update_provider_payment_and_status,
    )

    response = asyncio.run(
        _service(session).webhook_route(
            _FakeRequest(
                {
                    "transactionStatus": "WaitingForBank",
                    "transactionId": "tx-1",
                    "orderId": "465",
                }
            )
        )
    )

    assert response.status == 200
    assert session.commits == 0


def test_wata_refresh_finds_paid_transaction_by_order_id_and_finalizes(monkeypatch):
    session = _FakeSession()
    payment = _payment(provider="wata", provider_payment_id="link-id")
    updates = []
    finalized = []
    service = _service(session)

    async def search_transactions(*, order_id=None, payment_link_id=None, status=None, limit=5):
        assert order_id == "465"
        assert payment_link_id is None
        assert status == "Paid"
        assert limit == 5
        return True, {
            "items": [
                {
                    "id": "tx-paid",
                    "status": "Paid",
                    "orderId": "465",
                    "amount": 100,
                    "currency": "RUB",
                    "paymentLinkId": "link-id",
                }
            ]
        }

    async def get_payment_by_db_id(_session, payment_id):
        assert _session is session
        assert payment_id == 465
        return payment

    async def update_provider_payment_and_status(
        _session,
        payment_id,
        provider_payment_id,
        status,
    ):
        updates.append((payment_id, provider_payment_id, status))
        payment.provider_payment_id = provider_payment_id
        payment.status = status

    async def finalize_successful_payment(request):
        finalized.append(
            (
                request.payment.payment_id,
                request.provider_subscription,
                request.provider_notification,
            )
        )
        return SimpleNamespace()

    service.search_transactions = search_transactions
    monkeypatch.setattr(wata.payment_dal, "get_payment_by_db_id", get_payment_by_db_id)
    monkeypatch.setattr(
        wata.payment_dal,
        "update_provider_payment_and_status",
        update_provider_payment_and_status,
    )
    monkeypatch.setattr(wata, "finalize_successful_payment", finalize_successful_payment)

    result = asyncio.run(service.refresh_payment_status(session, payment))

    assert result is payment
    assert updates == [(465, "tx-paid", "succeeded")]
    assert finalized == [(465, "wata", "wata")]
    assert session.commits == 1
