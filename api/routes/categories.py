from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_user
from db import get_client

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    color: str = "#667eea"
    icon: str = "📁"


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


@router.get("/{user_id}")
async def list_categories(user_id: str, user: dict = Depends(get_user)) -> list:
    if user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db = await get_client()
    res = await (
        db.table("categories")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    categories = res.data or []

    # Attach todo count per category
    for cat in categories:
        count_res = await (
            db.table("todos")
            .select("id", count="exact")
            .eq("category_id", cat["id"])
            .eq("is_completed", False)
            .execute()
        )
        cat["todo_count"] = count_res.count or 0

    return categories


@router.post("/")
async def create_category(body: CategoryCreate, user: dict = Depends(get_user)) -> dict:
    db = await get_client()
    res = await (
        db.table("categories")
        .insert(
            {
                "user_id": user["id"],
                "name": body.name.strip(),
                "color": body.color,
                "icon": body.icon,
            }
        )
        .execute()
    )
    return res.data[0]


@router.patch("/{cat_id}")
async def update_category(
    cat_id: str,
    body: CategoryUpdate,
    user: dict = Depends(get_user),
) -> dict:
    db = await get_client()
    updates: dict = {}
    if body.name is not None:
        updates["name"] = body.name.strip()
    if body.color is not None:
        updates["color"] = body.color
    if body.icon is not None:
        updates["icon"] = body.icon

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    res = await (
        db.table("categories")
        .update(updates)
        .eq("id", cat_id)
        .eq("user_id", user["id"])
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Category not found")
    return res.data[0]


@router.delete("/{cat_id}", status_code=204)
async def delete_category(cat_id: str, user: dict = Depends(get_user)) -> None:
    db = await get_client()
    await (
        db.table("categories")
        .delete()
        .eq("id", cat_id)
        .eq("user_id", user["id"])
        .execute()
    )
