"""RAG package — local sourcebook retrieval for private play."""

from app.rag.ingest import IngestError, ingest_sourcebooks, list_source_files
from app.rag.retriever import debug_hits, format_rules_for_prompt, retrieve_rule_chunks

__all__ = [
    "IngestError",
    "debug_hits",
    "format_rules_for_prompt",
    "ingest_sourcebooks",
    "list_source_files",
    "retrieve_rule_chunks",
]
