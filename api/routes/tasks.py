from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_user
from db import get_client

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    priority: str = "medium"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[str] = None


@router.get("/")
async def list_tasks(status: str = "pending", user: dict = Depends(get_user)):
    db = await get_client()
    res = (
        await db.table("tasks")
        .select("*")
        .eq("created_by", user["id"])
        .is_("group_id", "null")
        .eq("status", status)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


@router.post("/")
async def create_task(body: TaskCreate, user: dict = Depends(get_user)):
    db = await get_client()
    payload: dict = {
        "title": body.title,
        "priority": body.priority,
        "created_by": user["id"],
        "status": "pending",
    }
    if body.due_date:
        payload["due_date"] = body.due_date
    res = await db.table("tasks").insert(payload).execute()
    return res.data[0]


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, user: dict = Depends(get_user)):
    db = await get_client()
    await db.table("task_completions").upsert(
        {"task_id": task_id, "user_id": user["id"]},
        on_conflict="task_id,user_id",
    ).execute()
    res = (
        await db.table("tasks")
        .update({"status": "completed"})
        .eq("task_id", task_id)
        .eq("created_by", user["id"])
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return res.data[0]


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, user: dict = Depends(get_user)):
    db = await get_client()
    await (
        db.table("tasks")
        .delete()
        .eq("task_id", task_id)
        .eq("created_by", user["id"])
        .execute()
    )


@router.patch("/{task_id}")
async def update_task(task_id: str, body: TaskUpdate, user: dict = Depends(get_user)):
    db = await get_client()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = (
        await db.table("tasks")
        .update(updates)
        .eq("task_id", task_id)
        .eq("created_by", user["id"])
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return res.data[0]
