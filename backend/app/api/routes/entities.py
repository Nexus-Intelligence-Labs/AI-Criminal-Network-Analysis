from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_entities() -> dict[str, str]:
    return {"detail": "Not implemented"}


