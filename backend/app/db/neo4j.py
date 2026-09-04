from functools import lru_cache

from neo4j import Driver, GraphDatabase

from app.core.config import get_settings


@lru_cache
def get_neo4j_driver() -> Driver:
    """Create the Neo4j driver only when a caller requests it."""
    settings = get_settings()
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


def close_neo4j_driver() -> None:
    if get_neo4j_driver.cache_info().currsize:
        get_neo4j_driver().close()
        get_neo4j_driver.cache_clear()
