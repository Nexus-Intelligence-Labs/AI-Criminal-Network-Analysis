from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_timelines() -> dict[str, str]:
    return {"detail": "Not implemented"}


