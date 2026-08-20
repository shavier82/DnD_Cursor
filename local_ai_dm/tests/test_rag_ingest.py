"""RAG ingest helpers — no LLM, no embedding model required."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.rag.ingest import IngestError, chunk_text, resolve_under_sourcebooks, sanitize_filename
from app.rag.retriever import debug_hits, format_rules_for_prompt


def test_sanitize_filename_rejects_traversal():
    with pytest.raises(IngestError):
        sanitize_filename("../secret.txt")
    with pytest.raises(IngestError):
        sanitize_filename("..\\secret.txt")
    assert sanitize_filename("PlayersHandbook2024.txt") == "PlayersHandbook2024.txt"


def test_resolve_under_sourcebooks_blocks_escape(tmp_path: Path):
    root = tmp_path / "books"
    root.mkdir()
    allowed = root / "phb.txt"
    allowed.write_text("ok", encoding="utf-8")
    outside = tmp_path / "secret.txt"
    outside.write_text("nope", encoding="utf-8")

    assert resolve_under_sourcebooks(allowed, root=root) == allowed.resolve()
    with pytest.raises(IngestError):
        resolve_under_sourcebooks(outside, root=root)


def test_chunk_text_keeps_paragraphs_and_skips_nav():
    sample = """
Skip to Content
D&D Beyond
Search Everything...

Playing the Game

The Dungeon Master describes a scene.

Players describe what they want to do.

The DM narrates the result of those actions.
"""
    chunks = chunk_text(sample, source="phb.txt")
    assert chunks
    combined = "\n".join(c.text for c in chunks)
    assert "Skip to Content" not in combined
    assert "D&D Beyond" not in combined
    assert "The Dungeon Master describes a scene." in combined
    assert "Players describe what they want to do." in combined
    # Heading captured as section
    assert any(c.section == "Playing the Game" for c in chunks)


def test_format_rules_limits_excerpt_length():
    long_text = "word " * 500
    formatted = format_rules_for_prompt(
        [{"text": long_text, "source": "phb.txt", "section": "Combat", "page": 12}]
    )
    assert "phb.txt" in formatted
    assert "Combat" in formatted
    assert len(formatted) < len(long_text)


def test_debug_hits_are_previews_not_full_docs():
    hits = debug_hits(
        [
            {
                "text": "A" * 1000,
                "source": "phb.txt",
                "section": "Rules",
                "chunk_index": 3,
                "distance": 0.2,
            }
        ]
    )
    assert hits[0]["source"] == "phb.txt"
    assert hits[0]["chunk_index"] == 3
    assert len(hits[0]["preview"]) < 300
    assert hits[0]["preview"].endswith("…")
