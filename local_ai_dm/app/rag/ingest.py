"""Sourcebook ingestion for private personal use.

Reads only from the configured sourcebooks directory. Never follows
path-traversal. Never returns full documents through the API.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.config import get_settings

logger = logging.getLogger(__name__)

ALLOWED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}

# D&D Beyond dump chrome — skip so retrieval is not polluted by site UI.
_NAV_LINE_RE = re.compile(
    r"^(skip to content|d&d beyond|search everything|prev chapter|"
    r"table of contents|dismiss|please enter birthdate|avatar |"
    r"profile|account|redeem a key|my subscription|threads|"
    r"campaigns|characters|homebrew|sign out|sources dungeons|"
    r"d&d discord|tiktok|instagram|facebook|twitch|youtube|"
    r"next chapter|breadcrumb)\b",
    re.IGNORECASE,
)

_HEADING_RE = re.compile(
    r"^(ch\.\s*\d+|chapter\s+\d+|part\s+\d+|appendix|"
    r"using this book|what you need|playing the game|"
    r"combat|spellcasting|conditions|equipment|monsters|"
    r"advantage|disadvantage|saving throws?|ability checks?|"
    r"d20 tests?|proficiency|hit points?|armor class)\b",
    re.IGNORECASE,
)

_NAME_LIKE_RE = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$")


@dataclass
class TextChunk:
    text: str
    source: str
    section: str
    chunk_index: int
    page: int | None = None


class IngestError(ValueError):
    """Raised when a source path is invalid or unsupported."""


def sanitize_filename(name: str) -> str:
    base = Path(name).name
    if not base or base in {".", ".."}:
        raise IngestError("Invalid filename")
    if any(sep in name.replace("\\", "/") for sep in ("../", "..\\")):
        raise IngestError("Path traversal is not allowed")
    return base


def resolve_under_sourcebooks(path: Path, root: Path | None = None) -> Path:
    """Ensure path resolves inside the configured sourcebooks directory."""
    settings = get_settings()
    root = (root or settings.sourcebooks_path).resolve()
    candidate = path.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise IngestError("Path is outside the configured sourcebooks directory") from exc
    return candidate


def list_source_files(root: Path | None = None) -> list[Path]:
    settings = get_settings()
    allowed = settings.sourcebooks_path.resolve()
    scan_root = resolve_under_sourcebooks(root or allowed, root=allowed)
    if not scan_root.is_dir():
        raise IngestError(f"Sourcebooks directory not found: {scan_root}")
    files: list[Path] = []
    for item in sorted(scan_root.rglob("*")):
        if not item.is_file():
            continue
        if item.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        resolve_under_sourcebooks(item, root=allowed)
        files.append(item)
    return files


def _is_nav_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _NAV_LINE_RE.match(stripped):
        return True
    if len(stripped) <= 3:
        return True
    return False


def _looks_like_heading(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 90:
        return False
    if stripped.endswith((".", "!", "?")):
        return False
    if _NAME_LIKE_RE.match(stripped):
        return False
    if stripped.isupper() and len(stripped.split()) <= 4:
        return False
    if _HEADING_RE.match(stripped):
        return True
    words = stripped.split()
    # Short titles only if they look like labeled rules headers (contain a colon or number)
    if 1 <= len(words) <= 8 and (":" in stripped or any(ch.isdigit() for ch in stripped)):
        return True
    return False


def extract_text(path: Path) -> list[tuple[str, int | None]]:
    """Return (text, page_number) units. TXT/MD are a single unit."""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        raw = path.read_text(encoding="utf-8", errors="replace")
        return [(raw, None)]
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages: list[tuple[str, int | None]] = []
        for i, page in enumerate(reader.pages, start=1):
            pages.append((page.extract_text() or "", i))
        return pages
    raise IngestError(f"Unsupported file type: {path.suffix}")


def _paragraphs_from_text(text: str) -> list[str]:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        if _is_nav_line(line):
            continue
        cleaned_lines.append(line.rstrip())
    blob = "\n".join(cleaned_lines)
    parts = re.split(r"\n\s*\n+", blob)
    paragraphs = [re.sub(r"[ \t]+", " ", p).strip() for p in parts]
    return [p for p in paragraphs if p]


def chunk_text(
    text: str,
    *,
    source: str,
    page: int | None = None,
    target_chars: int = 1400,
    max_chars: int = 2200,
) -> list[TextChunk]:
    """Pack paragraphs into chunks. Prefer not cutting mid-paragraph."""
    paragraphs = _paragraphs_from_text(text)
    chunks: list[TextChunk] = []
    buf: list[str] = []
    section = ""
    buf_len = 0

    def flush() -> None:
        nonlocal buf, buf_len
        if not buf:
            return
        body = "\n\n".join(buf).strip()
        if body:
            chunks.append(
                TextChunk(
                    text=body,
                    source=source,
                    section=section or "Unknown",
                    chunk_index=len(chunks),
                    page=page,
                )
            )
        buf = []
        buf_len = 0

    for para in paragraphs:
        if _looks_like_heading(para) and buf_len >= 200:
            flush()
            section = para
            buf = [para]
            buf_len = len(para)
            continue
        if _looks_like_heading(para) and not buf:
            section = para

        extra = len(para) + (2 if buf else 0)
        if buf and buf_len + extra > target_chars:
            if buf_len >= 400 or extra > max_chars:
                flush()
        if len(para) > max_chars:
            # Last resort: split long paragraphs on sentence boundaries
            flush()
            for piece in _split_long_paragraph(para, max_chars):
                chunks.append(
                    TextChunk(
                        text=piece,
                        source=source,
                        section=section or "Unknown",
                        chunk_index=len(chunks),
                        page=page,
                    )
                )
            continue
        buf.append(para)
        buf_len += extra

    flush()
    return chunks


def _split_long_paragraph(text: str, max_chars: int) -> Iterable[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    buf = ""
    for sentence in sentences:
        if buf and len(buf) + 1 + len(sentence) > max_chars:
            yield buf.strip()
            buf = sentence
        else:
            buf = f"{buf} {sentence}".strip() if buf else sentence
    if buf.strip():
        yield buf.strip()


def chunk_file(path: Path) -> list[TextChunk]:
    path = resolve_under_sourcebooks(path)
    source = path.name
    all_chunks: list[TextChunk] = []
    for text, page in extract_text(path):
        page_chunks = chunk_text(text, source=source, page=page)
        for chunk in page_chunks:
            chunk.chunk_index = len(all_chunks)
            all_chunks.append(chunk)
    return all_chunks


def ingest_sourcebooks(filenames: list[str] | None = None) -> dict:
    """Ingest allowed files from SOURCEBOOKS_DIR into ChromaDB."""
    from app.rag.embeddings import embed_texts
    from app.rag.vector_store import reset_collection, upsert_chunks

    files = list_source_files()
    if filenames:
        wanted = {sanitize_filename(name) for name in filenames}
        files = [f for f in files if f.name in wanted]
        missing = wanted - {f.name for f in files}
        if missing:
            raise IngestError(f"File not found in sourcebooks directory: {sorted(missing)}")

    if not files:
        raise IngestError("No PDF/TXT/Markdown files found in the sourcebooks directory")

    reset_collection()
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    per_file: dict[str, int] = {}

    for path in files:
        chunks = chunk_file(path)
        per_file[path.name] = len(chunks)
        logger.info("Ingesting %s (%s chunks)", path.name, len(chunks))
        for chunk in chunks:
            ids.append(f"{chunk.source}:{chunk.chunk_index}")
            documents.append(chunk.text)
            metadatas.append(
                {
                    "source": chunk.source,
                    "section": chunk.section[:200],
                    "chunk_index": chunk.chunk_index,
                    "page": chunk.page if chunk.page is not None else -1,
                }
            )

    embeddings = embed_texts(documents)
    upsert_chunks(ids, documents, metadatas, embeddings)
    logger.info("Ingested %s chunks from %s files", len(ids), len(files))
    return {
        "files": per_file,
        "chunks": len(ids),
        "sources": list(per_file.keys()),
    }
