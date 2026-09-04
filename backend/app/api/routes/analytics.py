from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_analytics() -> dict[str, str]:
    return {"detail": "Not implemented"}


