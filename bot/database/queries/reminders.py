from __future__ import annotations
from datetime import datetime
from supabase import AsyncClient


async def set_reminder(
    db: AsyncClient, task_id: str, reminder_time: datetime, job_id: str
) -> None:
    await db.table("tasks").update(
        {"reminder_time": reminder_time.isoformat(), "reminder_job_id": job_id}
    ).eq("task_id", task_id).execute()


async def clear_reminder(db: AsyncClient, task_id: str) -> None:
    await db.table("tasks").update(
        {"reminder_time": None, "reminder_job_id": None}
    ).eq("task_id", task_id).execute()


async def get_pending_reminders(db: AsyncClient) -> list[dict]:
    """Return all tasks with a future reminder_time (used on bot startup to restore jobs)."""
    now = datetime.utcnow().isoformat()
    res = (
        await db.table("tasks")
        .select("task_id, title, created_by, reminder_time, reminder_job_id")
        .gt("reminder_time", now)
        .eq("status", "pending")
        .execute()
    )
    return res.data or []
