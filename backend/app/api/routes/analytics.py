from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/")
def get_analytics(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"detail": "Not implemented"}