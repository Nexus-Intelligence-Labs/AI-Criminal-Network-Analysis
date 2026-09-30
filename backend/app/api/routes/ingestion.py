from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.ingestion import IngestionJobResponse, IngestionPreview, IngestionRequest
from app.services.audit_service import (
    INGESTION_FAILURE,
    INGESTION_IMPORT,
    INGESTION_UPLOAD,
    INGESTION_VALIDATION,
    log_event,
)
from app.services.ingestion_service import get_job, import_records, preview

router = APIRouter()


@router.post("/preview", response_model=IngestionPreview)
def preview_source(
    request: IngestionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> IngestionPreview:
    log_event(session, INGESTION_UPLOAD, actor=str(current_user.id), details={"filename": request.filename})
    result = preview(request)
    log_event(
        session,
        INGESTION_VALIDATION,
        actor=str(current_user.id),
        details={"filename": request.filename, "issue_count": len(result.issues)},
    )
    return result


@router.post("/import", response_model=IngestionJobResponse, status_code=status.HTTP_201_CREATED)
def import_source(
    request: IngestionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> IngestionJobResponse:
    result = preview(request)
    if result.issues:
        log_event(session, INGESTION_FAILURE, actor=str(current_user.id), details={"reason": "validation_failed"})
        raise HTTPException(status_code=422, detail=[issue.model_dump() for issue in result.issues])
    try:
        job_id, result, provenance_path, graph_counts = import_records(request)
    except (OSError, ValueError):
        log_event(session, INGESTION_FAILURE, actor=str(current_user.id), details={"reason": "artifact_write_failed"})
        raise HTTPException(status_code=500, detail="Ingestion could not be persisted")
    log_event(session, INGESTION_IMPORT, actor=str(current_user.id), details={"job_id": job_id, "case_id": request.case_id})
    return IngestionJobResponse(
        job_id=job_id,
        status="completed",
        filename=request.filename,
        case_id=request.case_id,
        source_type=request.source_type,
        row_count=result.provenance["record_count"],
        issue_count=len(result.issues),
        provenance_path=provenance_path,
        entities_written=graph_counts["entities_written"],
        relationships_written=graph_counts["relationships_written"],
    )


@router.get("/{job_id}", response_model=dict[str, object])
def get_import_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return job
