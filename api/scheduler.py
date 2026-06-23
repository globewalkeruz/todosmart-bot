import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _check_reminders(bot, db) -> None:
    now = datetime.now(timezone.utc)
    try:
        res = await (
            db.table("reminders")
            .select("id, remind_at, todos(id, title, user_id, users(telegram_id))")
            .eq("is_sent", False)
            .lte("remind_at", now.isoformat())
            .execute()
        )
        for reminder in res.data or []:
            todo = reminder.get("todos") or {}
            tg_user = todo.get("users") or {}
            telegram_id = tg_user.get("telegram_id")
            if not telegram_id:
                continue
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=(
                        f"⏰ *Reminder*\n\n"
                        f"📝 {todo.get('title', 'A task')} is due soon!\n\n"
                        "Open the app to check your todos."
                    ),
                    parse_mode="Markdown",
                )
                await (
                    db.table("reminders")
                    .update({"is_sent": True})
                    .eq("id", reminder["id"])
                    .execute()
                )
            except Exception as exc:
                logger.error("Failed to send reminder %s: %s", reminder["id"], exc)
    except Exception as exc:
        logger.error("Error in check_reminders: %s", exc)


def setup_scheduler(bot, db) -> None:
    scheduler.add_job(
        _check_reminders,
        trigger=IntervalTrigger(minutes=1),
        args=[bot, db],
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Reminder scheduler started")
