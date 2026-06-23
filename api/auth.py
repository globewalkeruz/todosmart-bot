import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException

from config import settings
from db import get_client


def _validate_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData and return the user object."""
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
        raise ValueError("initData hash mismatch — invalid or tampered request")

    user_json = parsed.get("user")
    if not user_json:
        raise ValueError("No user field in initData")
    return json.loads(user_json)


async def _upsert_user(tg_user: dict) -> dict:
    """Upsert a Telegram user into the users table and return the DB row."""
    db = await get_client()
    res = await (
        db.table("users")
        .upsert(
            {
                "telegram_id": tg_user["id"],
                "username": tg_user.get("username"),
                "first_name": tg_user.get("first_name", ""),
                "last_name": tg_user.get("last_name"),
            },
            on_conflict="telegram_id",
        )
        .execute()
    )
    return res.data[0]


async def get_user(authorization: str = Header(None)) -> dict:
    """FastAPI dependency: validate Telegram initData, upsert user, return DB row."""
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header (expected: tma <initData>)",
        )
    try:
        tg_user = _validate_init_data(authorization[4:])
        return await _upsert_user(tg_user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))
