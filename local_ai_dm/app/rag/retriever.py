"""Retrieve limited rule excerpts for the current player action."""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

MAX_PROMPT_EXCERPT = 700
MAX_DEBUG_PREVIEW = 240


def retrieve_rule_chunks(query: str, *, n_results: int | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.rag_enabled or not query.strip():
        return []
    try:
        from app.rag.embeddings import embed_query
        from app.rag.vector_store import collection_count, query_chunks
    except Exception as exc:
        logger.error("RAG imports failed: %s", exc)
        return []

    if collection_count() == 0:
        return []

    k = n_results if n_results is not None else settings.rag_top_k
    hits = query_chunks(embed_query(query.strip()), n_results=k)
    if settings.log_rag_chunk_text:
        logger.info("RAG retrieved %s chunks for query", len(hits))
    else:
        logger.info(
            "RAG retrieved %s chunks: %s",
            len(hits),
            [(h.get("source"), h.get("chunk_index"), h.get("distance")) for h in hits],
        )
    return hits


def format_rules_for_prompt(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return (
            "(none indexed — run POST /api/documents/ingest after placing legally obtained "
            "source files in SOURCEBOOKS_DIR. Do not invent precise rules numbers.)"
        )
    blocks: list[str] = []
    for i, hit in enumerate(hits, start=1):
        excerpt = (hit.get("text") or "").strip()
        if len(excerpt) > MAX_PROMPT_EXCERPT:
            excerpt = excerpt[:MAX_PROMPT_EXCERPT].rsplit(" ", 1)[0] + "…"
        source = hit.get("source") or "unknown"
        section = hit.get("section") or ""
        page = hit.get("page")
        page_bit = f", page {page}" if isinstance(page, int) and page > 0 else ""
        header = f"[{i}] {source}{page_bit}"
        if section:
            header += f" — {section}"
        blocks.append(f"{header}\n{excerpt}")
    return "\n\n".join(blocks)


def debug_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Limited excerpts for the DM debug panel — not full documents."""
    out: list[dict[str, Any]] = []
    for hit in hits:
        text = (hit.get("text") or "").strip()
        preview = text[:MAX_DEBUG_PREVIEW] + ("…" if len(text) > MAX_DEBUG_PREVIEW else "")
        out.append(
            {
                "source": hit.get("source"),
                "section": hit.get("section"),
                "chunk_index": hit.get("chunk_index"),
                "page": hit.get("page") if hit.get("page") not in (None, -1) else None,
                "distance": hit.get("distance"),
                "preview": preview,
            }
        )
    return out
