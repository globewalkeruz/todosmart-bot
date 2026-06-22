import logging
from aiogram import Router
from aiogram.types import ErrorEvent, CallbackQuery, Message

logger = logging.getLogger(__name__)
router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent) -> None:
    logger.error("Unhandled error: %s", event.exception, exc_info=event.exception)


@router.callback_query()
async def catch_all_callback(query: CallbackQuery) -> None:
    logger.warning("UNHANDLED callback_query data=%r from user=%s", query.data, query.from_user.id)
    await query.answer("Unknown action, please try again.", show_alert=True)


@router.message()
async def catch_all_message(message: Message) -> None:
    logger.warning("UNHANDLED message text=%r from user=%s", message.text, message.from_user.id)
