from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_user
from db import get_client

router = APIRouter()


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    priority: str = "medium"
    deadline: Optional[str] = None
    reminder_at: Optional[str] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[str] = None
    is_completed: Optional[bool] = None


@router.get("/{user_id}")
async def list_todos(
    user_id: str,
    status: str = "all",
    user: dict = Depends(get_user),
) -> list:
    if user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db = await get_client()
    q = (
        db.table("todos")
        .select("*, categories(id, name, color, icon)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if status == "completed":
        q = q.eq("is_completed", True)
    elif status == "pending":
        q = q.eq("is_completed", False)

    res = await q.execute()
    return res.data or []


@router.post("/")
async def create_todo(body: TodoCreate, user: dict = Depends(get_user)) -> dict:
    db = await get_client()
    payload: dict = {
        "user_id": user["id"],
        "title": body.title.strip(),
        "priority": body.priority,
        "is_completed": False,
    }
    if body.description:
        payload["description"] = body.description.strip()
    if body.category_id:
        payload["category_id"] = body.category_id
    if body.deadline:
        payload["deadline"] = body.deadline

    res = await db.table("todos").insert(payload).execute()
    todo = res.data[0]

    if body.reminder_at:
        await (
            db.table("reminders")
            .insert({"todo_id": todo["id"], "remind_at": body.reminder_at})
            .execute()
        )

    return todo


@router.patch("/{todo_id}")
async def update_todo(
    todo_id: str,
    body: TodoUpdate,
    user: dict = Depends(get_user),
) -> dict:
    db = await get_client()
    updates: dict = {}

    if body.title is not None:
        updates["title"] = body.title.strip()
    if body.description is not None:
        updates["description"] = body.description.strip() or None
    if body.category_id is not None:
        updates["category_id"] = body.category_id
    if body.priority is not None:
        updates["priority"] = body.priority
    if body.deadline is not None:
        updates["deadline"] = body.deadline or None
    if body.is_completed is True:
        updates["is_completed"] = True
        updates["completed_at"] = datetime.now(timezone.utc).isoformat()
    elif body.is_completed is False:
        updates["is_completed"] = False
        updates["completed_at"] = None

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    res = await (
        db.table("todos")
        .update(updates)
        .eq("id", todo_id)
        .eq("user_id", user["id"])
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Todo not found")
    return res.data[0]


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(todo_id: str, user: dict = Depends(get_user)) -> None:
    db = await get_client()
    await (
        db.table("todos")
        .delete()
        .eq("id", todo_id)
        .eq("user_id", user["id"])
        .execute()
    )
