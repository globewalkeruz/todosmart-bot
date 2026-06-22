import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from api.config import settings


def _validate_init_data(init_data: str) -> dict:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("No hash in initData")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )
    secret = hmac.new(
        b"WebAppData",
        settings.bot_token.encode(),
        hashlib.sha256,
    ).digest()
    computed = hmac.new(
        secret,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        raise ValueError("Hash mismatch — invalid initData")

    return json.loads(parsed["user"])


async def get_user(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(status_code=401, detail="Missing Telegram auth header")
    try:
        return _validate_init_data(authorization[4:])
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))
