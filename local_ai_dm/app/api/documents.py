"""Document ingest / index status. Never returns full sourcebook text."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.rag.ingest import IngestError, ingest_sourcebooks, list_source_files, sanitize_filename
from app.rag.vector_store import collection_count, listed_sources
from app.schemas import DocumentIngestRequest, DocumentStatusResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/status", response_model=DocumentStatusResponse)
def documents_status() -> DocumentStatusResponse:
    settings = get_settings()
    try:
        files = [p.name for p in list_source_files()]
    except IngestError:
        files = []
    return DocumentStatusResponse(
        rag_enabled=settings.rag_enabled,
        sourcebooks_dir=str(settings.sourcebooks_path),
        indexed_chunks=collection_count(),
        sources=listed_sources(),
        available_files=files,
    )


@router.post("/ingest")
def ingest_documents(payload: DocumentIngestRequest | None = None) -> dict:
    payload = payload or DocumentIngestRequest()
    filenames = None
    if payload.filenames:
        try:
            filenames = [sanitize_filename(name) for name in payload.filenames]
        except IngestError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        result = ingest_sourcebooks(filenames)
    except IngestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc
    return result
