import logging
from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)
router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent) -> None:
    logger.error("Unhandled error: %s", event.exception, exc_info=event.exception)
    # Silently ignore — avoids crashing the polling loop
