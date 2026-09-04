from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_cases() -> dict[str, str]:
    return {"detail": "Not implemented"}
