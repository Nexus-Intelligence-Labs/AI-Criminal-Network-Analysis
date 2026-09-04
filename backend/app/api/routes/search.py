from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def search() -> dict[str, str]:
    return {"detail": "Not implemented"}
