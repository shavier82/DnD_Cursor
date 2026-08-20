"""Local embedding model wrapper.

Uses sentence-transformers on this machine. No cloud embedding APIs.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Sequence

from app.config import get_settings

logger = logging.getLogger(__name__)

_model = None


def get_embedding_model():
    """Lazy-load the embedding model (first call may download weights)."""
    global _model
    if _model is None:
        settings = get_settings()
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model %s", settings.embedding_model)
        _model = SentenceTransformer(settings.embedding_model)
    return _model


@lru_cache
def embedding_dimension() -> int:
    model = get_embedding_model()
    dim = model.get_sentence_embedding_dimension()
    return int(dim)


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(
        list(texts),
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 32,
        batch_size=32,
    )
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
