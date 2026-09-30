from typing import Any

from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    case_id: str = Field(min_length=1, max_length=100)
    source_type: str = Field(min_length=1, max_length=100)


class ValidationIssue(BaseModel):
    row: int | None = None
    field: str | None = None
    message: str


class IngestionPreview(BaseModel):
    filename: str
    case_id: str
    source_type: str
    columns: list[str]
    rows: list[dict[str, Any]]
    issues: list[ValidationIssue]
    provenance: dict[str, Any]


class IngestionJobResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    case_id: str
    source_type: str
    row_count: int
    issue_count: int
    provenance_path: str
    entities_written: int
    relationships_written: int
