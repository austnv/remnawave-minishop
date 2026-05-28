import json
from datetime import datetime, timezone

import bot.app.web.subscription_webapp  # noqa: F401
from bot.app.web.webapp.devices import _serialize_device


def test_device_serializer_accepts_datetime_created_at():
    created_at = datetime(2099, 1, 2, 3, 4, tzinfo=timezone.utc)

    payload = _serialize_device(
        {
            "hwid": "abcdef123456",
            "deviceModel": "Laptop",
            "createdAt": created_at,
        },
        1,
    )

    assert payload["created_at"] == created_at.isoformat()
    assert payload["created_at_text"] == "02.01.2099 03:04"
    json.dumps(payload)
