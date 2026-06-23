from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from auth import get_user
from db import get_client

router = APIRouter()

_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@router.get("/{user_id}")
async def get_stats(user_id: str, user: dict = Depends(get_user)) -> dict:
    if user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db = await get_client()
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today_start - timedelta(days=6)

    # Totals
    total_res = await (
        db.table("todos").select("id", count="exact").eq("user_id", user_id).execute()
    )
    completed_res = await (
        db.table("todos")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("is_completed", True)
        .execute()
    )
    overdue_res = await (
        db.table("todos")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("is_completed", False)
        .lt("deadline", now.isoformat())
        .not_.is_("deadline", "null")
        .execute()
    )

    total = total_res.count or 0
    completed = completed_res.count or 0
    overdue = overdue_res.count or 0

    # Weekly completed (last 7 days including today)
    weekly_raw = await (
        db.table("todos")
        .select("completed_at")
        .eq("user_id", user_id)
        .eq("is_completed", True)
        .gte("completed_at", week_ago.isoformat())
        .execute()
    )
    daily: dict[str, int] = {}
    for row in weekly_raw.data or []:
        if row.get("completed_at"):
            day = row["completed_at"][:10]
            daily[day] = daily.get(day, 0) + 1

    weekly = []
    for i in range(7):
        d = (week_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        weekly.append({"date": d, "count": daily.get(d, 0)})

    # Streak — consecutive days ending today where count >= 1
    streak = 0
    for i in range(7):
        d = (today_start - timedelta(days=i)).strftime("%Y-%m-%d")
        if daily.get(d, 0) > 0:
            streak += 1
        else:
            break

    # Most productive day (all-time)
    all_completed = await (
        db.table("todos")
        .select("completed_at")
        .eq("user_id", user_id)
        .eq("is_completed", True)
        .not_.is_("completed_at", "null")
        .execute()
    )
    day_totals: dict[int, int] = {}
    for row in all_completed.data or []:
        if row.get("completed_at"):
            weekday = datetime.fromisoformat(row["completed_at"].replace("Z", "+00:00")).weekday()
            day_totals[weekday] = day_totals.get(weekday, 0) + 1

    most_productive = None
    if day_totals:
        best = max(day_totals, key=day_totals.__getitem__)
        most_productive = _DAY_NAMES[best]

    # By category
    all_todos = await (
        db.table("todos")
        .select("category_id, categories(name, color, icon)")
        .eq("user_id", user_id)
        .execute()
    )
    cat_map: dict[str, dict] = {}
    for row in all_todos.data or []:
        cat = row.get("categories")
        if cat:
            key = cat["name"]
            if key not in cat_map:
                cat_map[key] = {**cat, "count": 0}
            cat_map[key]["count"] += 1

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "overdue": overdue,
        "completion_rate": round(completed / total * 100) if total else 0,
        "weekly": weekly,
        "streak": streak,
        "most_productive_day": most_productive,
        "by_category": list(cat_map.values()),
    }
