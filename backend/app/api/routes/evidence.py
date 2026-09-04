from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/")
def list_evidence(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"detail": "Not implemented"}