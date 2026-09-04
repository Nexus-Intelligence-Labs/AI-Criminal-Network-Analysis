from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.graph_service import GraphService

router = APIRouter()

graph_service = GraphService()


@router.get("/{case_id}")
def get_graph(case_id: str, current_user: User = Depends(get_current_user)):
    """
    Return the complete graph for an investigation.
    """
    return graph_service.get_case_graph(case_id)


@router.get("/neighbors/{entity_id}")
def get_neighbors(entity_id: str, current_user: User = Depends(get_current_user)):
    """
    Return all entities directly connected to the given entity.
    """
    return graph_service.get_neighbors(entity_id)


@router.get("/shortest-path")
def get_shortest_path(source: str, target: str, current_user: User = Depends(get_current_user)):
    """
    Return the shortest path between two entities.
    """
    return graph_service.get_shortest_path(source, target)

