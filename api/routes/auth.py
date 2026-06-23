from fastapi import APIRouter, Depends

from auth import get_user

router = APIRouter()


@router.post("/me")
async def me(user: dict = Depends(get_user)) -> dict:
    """Return the current authenticated user's profile."""
    return user
