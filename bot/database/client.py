from supabase import AsyncClient, acreate_client
from bot.config import config

_client: AsyncClient | None = None


async def get_client() -> AsyncClient:
    global _client
    if _client is None:
        _client = await acreate_client(config.supabase_url, config.supabase_key)
    return _client
