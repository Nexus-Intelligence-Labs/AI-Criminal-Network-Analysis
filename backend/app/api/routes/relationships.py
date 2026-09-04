from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_relationships() -> dict[str, str]:
    return {"detail": "Not implemented"}
