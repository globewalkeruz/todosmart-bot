from __future__ import annotations
from supabase import AsyncClient


async def upsert_group(db: AsyncClient, group_id: int, title: str, chat_type: str) -> None:
    await db.table("groups").upsert(
        {"group_id": group_id, "title": title, "chat_type": chat_type},
        on_conflict="group_id",
    ).execute()


async def add_member(db: AsyncClient, group_id: int, user_id: int, role: str = "member") -> None:
    await db.table("group_members").upsert(
        {"group_id": group_id, "user_id": user_id, "role": role},
        on_conflict="group_id,user_id",
    ).execute()


async def get_members(db: AsyncClient, group_id: int) -> list[dict]:
    res = (
        await db.table("group_members")
        .select("*, users(user_id, username, first_name, last_name)")
        .eq("group_id", group_id)
        .order("joined_at")
        .execute()
    )
    return res.data or []
