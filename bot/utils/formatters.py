from __future__ import annotations
from datetime import datetime

PRIORITY_EMOJI = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
PRIORITY_LABEL = {"urgent": "Urgent", "high": "High", "medium": "Medium", "low": "Low"}
STATUS_EMOJI   = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}


def fmt_task(task: dict, show_creator: bool = False) -> str:
    priority = task.get("priority", "medium")
    status   = task.get("status", "pending")
    p_emoji  = PRIORITY_EMOJI.get(priority, "🟡")
    s_emoji  = STATUS_EMOJI.get(status, "⏳")

    lines = [
        f"{s_emoji} *{task['title']}*",
        f"{p_emoji} Priority: {PRIORITY_LABEL.get(priority, priority.title())}",
    ]

    if task.get("due_date"):
        due = _parse_dt(task["due_date"])
        lines.append(f"📅 Due: {due.strftime('%d %b %Y %H:%M') if due else task['due_date']}")

    if task.get("reminder_time"):
        rem = _parse_dt(task["reminder_time"])
        lines.append(f"⏰ Reminder: {rem.strftime('%d %b %Y %H:%M') if rem else task['reminder_time']}")

    if show_creator:
        creator = task.get("creator") or {}
        name = creator.get("first_name") or creator.get("username") or "Unknown"
        lines.append(f"👤 By: {name}")

    if task.get("description"):
        lines.append(f"📄 {task['description']}")

    lines.append(f"\n`ID: {task['task_id'][:8]}…`")
    return "\n".join(lines)


def fmt_stats(stats: dict, title: str = "📊 Statistics") -> str:
    total = stats["total"]
    completed = stats["completed"]
    pending = stats["pending"]
    rate = f"{completed / total * 100:.1f}%" if total else "—"

    lines = [
        f"*{title}*\n",
        f"📈 Total tasks:  {total}",
        f"✅ Completed:    {completed}",
        f"⏳ Pending:      {pending}",
        f"🎯 Rate:         {rate}",
    ]

    if "by_priority" in stats:
        bp = stats["by_priority"]
        lines += [
            "\n🏷️ *Pending by priority:*",
            f"🚨 Urgent: {bp.get('urgent', 0)}",
            f"🔴 High:   {bp.get('high', 0)}",
            f"🟡 Medium: {bp.get('medium', 0)}",
            f"🟢 Low:    {bp.get('low', 0)}",
        ]

    return "\n".join(lines)


def _parse_dt(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
