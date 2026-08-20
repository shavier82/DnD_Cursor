"""ChromaDB persistence for sourcebook chunks.

Stores embeddings locally. Does not expose full source documents.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "sourcebooks"


def _chroma_settings():
    import chromadb

    return chromadb.Settings(anonymized_telemetry=False, allow_reset=True)


@lru_cache
def get_client():
    import chromadb

    settings = get_settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(settings.chroma_path),
        settings=_chroma_settings(),
    )


def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection():
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        logger.info("Chroma collection %s did not exist yet", COLLECTION_NAME)
    return get_collection()


def collection_count() -> int:
    try:
        return int(get_collection().count())
    except Exception as exc:
        logger.error("Chroma count failed: %s", exc)
        return 0


def listed_sources() -> list[str]:
    """Return unique source filenames only — never full document text."""
    try:
        collection = get_collection()
        if collection.count() == 0:
            return []
        data = collection.get(include=["metadatas"])
        names = sorted(
            {
                str(m.get("source", ""))
                for m in (data.get("metadatas") or [])
                if m and m.get("source")
            }
        )
        return names
    except Exception as exc:
        logger.error("Chroma source listing failed: %s", exc)
        return []


def upsert_chunks(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict[str, Any]],
    embeddings: list[list[float]],
) -> int:
    if not ids:
        return 0
    collection = get_collection()
    batch = 200
    added = 0
    for start in range(0, len(ids), batch):
        end = start + batch
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            embeddings=embeddings[start:end],
        )
        added += end - start
    return added


def query_chunks(
    query_embedding: list[float],
    n_results: int = 4,
) -> list[dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    n_results = max(1, min(n_results, 8))
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    ids = (result.get("ids") or [[]])[0]
    hits: list[dict[str, Any]] = []
    for i, doc in enumerate(documents):
        meta = metadatas[i] if i < len(metadatas) else {}
        hits.append(
            {
                "id": ids[i] if i < len(ids) else "",
                "text": doc or "",
                "source": str(meta.get("source", "")),
                "section": str(meta.get("section", "")),
                "chunk_index": int(meta.get("chunk_index", 0) or 0),
                "page": meta.get("page"),
                "distance": float(distances[i]) if i < len(distances) else None,
            }
        )
    return hits
