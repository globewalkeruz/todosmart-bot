from __future__ import annotations
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _fire_reminder(bot, chat_id: int, task_id: str, title: str) -> None:
    from bot.database.client import get_client
    from bot.database.queries.reminders import clear_reminder

    try:
        await bot.send_message(
            chat_id,
            f"⏰ *Reminder!*\n\n📝 {title}\n\n_This task is waiting for you._",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning("Could not send reminder to %s: %s", chat_id, e)
    finally:
        db = await get_client()
        await clear_reminder(db, task_id)


def schedule_reminder(bot, chat_id: int, task_id: str, title: str, run_at: datetime) -> str:
    job_id = f"rem_{task_id}"
    scheduler.add_job(
        _fire_reminder,
        trigger="date",
        run_date=run_at,
        args=[bot, chat_id, task_id, title],
        id=job_id,
        replace_existing=True,
        misfire_grace_time=300,
    )
    logger.info("Scheduled reminder %s at %s", job_id, run_at)
    return job_id


def cancel_reminder(job_id: str) -> None:
    try:
        scheduler.remove_job(job_id)
        logger.info("Cancelled reminder job %s", job_id)
    except JobLookupError:
        pass


async def restore_reminders(bot) -> None:
    """Re-schedule all reminders from DB that are still in the future (called on startup)."""
    from bot.database.client import get_client
    from bot.database.queries.reminders import get_pending_reminders

    try:
        db = await get_client()
        pending = await get_pending_reminders(db)
    except Exception as e:
        logger.warning("Could not restore reminders (DB unavailable): %s", e)
        return
    now = datetime.utcnow()
    count = 0
    for row in pending:
        try:
            run_at_str = row["reminder_time"]
            run_at = datetime.fromisoformat(run_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            if run_at > now:
                schedule_reminder(bot, row["created_by"], row["task_id"], row["title"], run_at)
                count += 1
        except Exception as e:
            logger.warning("Could not restore reminder for task %s: %s", row.get("task_id"), e)
    logger.info("Restored %d pending reminder(s)", count)
