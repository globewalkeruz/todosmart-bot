from __future__ import annotations
from datetime import datetime
from supabase import AsyncClient


async def create_task(
    db: AsyncClient,
    title: str,
    created_by: int,
    priority: str = "medium",
    group_id: int | None = None,
    description: str | None = None,
    due_date: datetime | None = None,
) -> dict:
    payload: dict = {
        "title": title,
        "created_by": created_by,
        "priority": priority,
    }
    if group_id:
        payload["group_id"] = group_id
    if description:
        payload["description"] = description
    if due_date:
        payload["due_date"] = due_date.isoformat()

    res = await db.table("tasks").insert(payload).execute()
    return res.data[0]


async def get_task(db: AsyncClient, task_id: str) -> dict | None:
    res = await db.table("tasks").select("*").eq("task_id", task_id).maybe_single().execute()
    return res.data


async def list_personal_tasks(
    db: AsyncClient, user_id: int, status: str = "pending"
) -> list[dict]:
    res = (
        await db.table("tasks")
        .select("*")
        .eq("created_by", user_id)
        .is_("group_id", "null")
        .eq("status", status)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def list_group_tasks(
    db: AsyncClient, group_id: int, status: str = "pending"
) -> list[dict]:
    res = (
        await db.table("tasks")
        .select("*, creator:created_by(first_name, username)")
        .eq("group_id", group_id)
        .eq("status", status)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


async def update_task(db: AsyncClient, task_id: str, **fields) -> dict | None:
    res = await db.table("tasks").update(fields).eq("task_id", task_id).execute()
    return res.data[0] if res.data else None


async def complete_task(db: AsyncClient, task_id: str, user_id: int) -> bool:
    # Record the completion
    await db.table("task_completions").upsert(
        {"task_id": task_id, "user_id": user_id},
        on_conflict="task_id,user_id",
    ).execute()
    # Mark task as completed
    await db.table("tasks").update({"status": "completed"}).eq("task_id", task_id).execute()
    return True


async def delete_task(db: AsyncClient, task_id: str) -> bool:
    await db.table("tasks").delete().eq("task_id", task_id).execute()
    return True


async def assign_task(db: AsyncClient, task_id: str, user_id: int, assigned_by: int) -> bool:
    await db.table("task_assignments").upsert(
        {"task_id": task_id, "user_id": user_id, "assigned_by": assigned_by},
        on_conflict="task_id,user_id",
    ).execute()
    return True


async def get_user_stats(db: AsyncClient, user_id: int) -> dict:
    all_tasks = (
        await db.table("tasks")
        .select("status, priority")
        .eq("created_by", user_id)
        .is_("group_id", "null")
        .execute()
    )
    tasks = all_tasks.data or []
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    pending = sum(1 for t in tasks if t["status"] == "pending")
    by_priority = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
    for t in tasks:
        if t["status"] == "pending" and t["priority"] in by_priority:
            by_priority[t["priority"]] += 1
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "by_priority": by_priority,
    }


async def get_group_stats(db: AsyncClient, group_id: int) -> dict:
    all_tasks = (
        await db.table("tasks")
        .select("status, priority")
        .eq("group_id", group_id)
        .execute()
    )
    tasks = all_tasks.data or []
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    pending = total - completed
    return {"total": total, "completed": completed, "pending": pending}
