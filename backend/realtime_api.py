import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ==========================================================
# Project paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_ROOT = PROJECT_ROOT / "ai"

if str(AI_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(AI_ROOT),
    )


# ==========================================================
# AI / pipeline imports
# ==========================================================

from pipelines.unified_pipeline import UnifiedPipeline
from graph.neo4j_writer import Neo4jGraphWriter


# ==========================================================
# FastAPI application
# ==========================================================

app = FastAPI(
    title="AI Criminal Network Analysis API",
    version="1.0.0",
    description=(
        "Real-time ingestion API for FIR, CDR, "
        "and financial investigative data."
    ),
)


# ==========================================================
# Request model
# ==========================================================

class IngestionRequest(BaseModel):
    """
    Generic real-time ingestion request.

    The fields inside `data` depend on record_type.
    """

    data: dict[str, Any]


# ==========================================================
# Shared Neo4j writer and pipeline
# ==========================================================

neo4j_writer = Neo4jGraphWriter()

pipeline = UnifiedPipeline(
    neo4j_writer=neo4j_writer,
)


# ==========================================================
# Serialization helper
# ==========================================================

def serialize(value):
    """
    Convert Pydantic models and nested Python structures
    into JSON-compatible data.
    """

    if isinstance(
        value,
        BaseModel,
    ):
        return value.model_dump()

    if isinstance(
        value,
        dict,
    ):
        return {
            key: serialize(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            serialize(item)
            for item in value
        ]

    if isinstance(
        value,
        tuple,
    ):
        return [
            serialize(item)
            for item in value
        ]

    return value


# ==========================================================
# Root endpoint
# ==========================================================

@app.get("/")
def root():
    """Return API information."""

    return {
        "service": (
            "AI Criminal Network Analysis API"
        ),
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "cdr": "/ingest/cdr",
            "financial": "/ingest/financial",
            "fir": "/ingest/fir",
        },
    }


# ==========================================================
# Health endpoint
# ==========================================================

@app.get("/health")
def health():
    """
    Verify that the API is running and Neo4j is reachable.
    """

    try:
        neo4j_writer.connect()

        neo4j_writer.driver.verify_connectivity()

        return {
            "status": "healthy",
            "neo4j": "connected",
        }

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "neo4j": "connection_failed",
                "error": str(exc),
            },
        )


# ==========================================================
# Real-time ingestion endpoint
# ==========================================================

@app.post("/ingest/{record_type}")
def ingest(
    record_type: str,
    request: IngestionRequest,
):
    """
    Process one live investigative record.

    Supported:
    - cdr
    - financial
    - fir
    """

    record_type = (
        record_type
        .strip()
        .lower()
    )

    supported_types = {
        "cdr",
        "financial",
        "fir",
    }

    if record_type not in supported_types:

        raise HTTPException(
            status_code=400,
            detail={
                "error": (
                    "Unsupported record type."
                ),
                "supported_types": sorted(
                    supported_types
                ),
            },
        )

    if not request.data:

        raise HTTPException(
            status_code=400,
            detail=(
                "Request data cannot be empty."
            ),
        )

    try:
        # --------------------------------------------------
        # Process the incoming record.
        # --------------------------------------------------

        result = pipeline.process(
            record_type,
            request.data,
        )

        # --------------------------------------------------
        # Persist graph data to Neo4j.
        # --------------------------------------------------

        neo4j_result = (
            pipeline.write_to_neo4j(
                result["graph_data"]
            )
        )

        # --------------------------------------------------
        # Return the live processing result.
        # --------------------------------------------------

        return {
            "status": "processed",
            "record_type": record_type,
            "source_record": result.get(
                "source_record"
            ),
            "neo4j": neo4j_result,
            "result": serialize(
                result
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
            },
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail={
                "error": str(exc),
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "Processing failed."
                ),
                "message": str(exc),
            },
        )


# ==========================================================
# Shutdown
# ==========================================================

@app.on_event("shutdown")
def shutdown():
    """
    Close the Neo4j driver when the FastAPI process exits.
    """

    neo4j_writer.close()