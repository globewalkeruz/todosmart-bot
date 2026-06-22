from __future__ import annotations
from datetime import datetime, timezone
from supabase import AsyncClient
from aiogram.types import User


async def upsert_user(db: AsyncClient, user: User) -> None:
    await db.table("users").upsert(
        {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "last_active": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="user_id",
    ).execute()


async def get_user(db: AsyncClient, user_id: int) -> dict | None:
    res = await db.table("users").select("*").eq("user_id", user_id).maybe_single().execute()
    return res.data
