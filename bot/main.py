import asyncio
import logging
from datetime import time as dt_time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config
from bot.middlewares.db_middleware import DBMiddleware
from bot.middlewares.user_middleware import UserMiddleware
from bot.middlewares.group_middleware import GroupMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.scheduler.jobs import scheduler, restore_reminders

from bot.handlers import errors, start, tasks, reminders, groups, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def send_daily_summary(bot: Bot) -> None:
    """Send daily task summary to all users with pending tasks."""
    from bot.database.client import get_client
    from bot.database.queries.tasks import list_personal_tasks

    db = await get_client()
    # Fetch all distinct user IDs from tasks table
    res = await db.table("tasks").select("created_by").is_("group_id", "null").eq("status", "pending").execute()
    user_ids = {row["created_by"] for row in (res.data or [])}

    for uid in user_ids:
        try:
            tasks_list = await list_personal_tasks(db, uid)
            if not tasks_list:
                continue
            lines = [f"📅 *Daily Summary — {len(tasks_list)} pending task(s):*\n"]
            for t in tasks_list[:10]:
                lines.append(f"• {t['title']}")
            if len(tasks_list) > 10:
                lines.append(f"_…and {len(tasks_list) - 10} more_")
            await bot.send_message(uid, "\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.warning("Daily summary failed for user %s: %s", uid, e)


async def main() -> None:
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Middleware chain ────────────────────────────────────────────────────────
    dp.update.middleware(ThrottlingMiddleware(rate=0.5))
    dp.update.middleware(DBMiddleware())
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(GroupMiddleware())

    # ── Routers ─────────────────────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(reminders.router)
    dp.include_router(groups.router)
    dp.include_router(stats.router)
    dp.include_router(errors.router)  # last: catch-all fallback

    # ── APScheduler ─────────────────────────────────────────────────────────────
    scheduler.start()
    await restore_reminders(bot)

    # Daily summary job
    summary_time = dt_time(
        hour=config.daily_summary_hour,
        minute=config.daily_summary_minute,
    )
    scheduler.add_job(
        send_daily_summary,
        trigger="cron",
        hour=summary_time.hour,
        minute=summary_time.minute,
        args=[bot],
        id="daily_summary",
        replace_existing=True,
    )
    logger.info(
        "Daily summary scheduled at %02d:%02d",
        summary_time.hour,
        summary_time.minute,
    )

    # ── Start polling ────────────────────────────────────────────────────────────
    logger.info("TodoSmart bot starting...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
