from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_evidence() -> dict[str, str]:
    return {"detail": "Not implemented"}
