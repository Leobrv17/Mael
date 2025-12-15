from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.user import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_me(current_user=Depends(get_current_user)) -> UserOut:
    return current_user
