from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_graph() -> dict[str, str]:
    return {"detail": "Not implemented"}
