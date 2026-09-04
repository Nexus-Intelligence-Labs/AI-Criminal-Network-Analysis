from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_alerts() -> dict[str, str]:
    return {"detail": "Not implemented"}


