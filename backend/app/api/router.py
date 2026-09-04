from fastapi import APIRouter

from app.api.routes import (
    alerts,
    analytics,
    auth,
    cases,
    entities,
    evidence,
    graph,
    health,
    relationships,
    search,
    timelines,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/auth", tags=["auth"])
api_router.include_router(entities.router, prefix="/api/entities", tags=["entities"])
api_router.include_router(relationships.router, prefix="/api/relationships", tags=["relationships"])
api_router.include_router(graph.router, prefix="/api/graph", tags=["graph"])
api_router.include_router(search.router, prefix="/api/search", tags=["search"])
api_router.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
api_router.include_router(cases.router, prefix="/api/cases", tags=["cases"])
api_router.include_router(timelines.router, prefix="/api/timelines", tags=["timelines"])
api_router.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"])
api_router.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
