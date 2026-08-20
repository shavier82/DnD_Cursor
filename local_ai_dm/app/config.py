"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# local_ai_dm/ — project root (parent of app/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime settings. Prefer env vars / .env over hard-coded values."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    ollama_url: str = Field(default="http://localhost:11434", alias="OLLAMA_URL")
    ollama_model: str = Field(default="qwen3:4b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: float = Field(default=120.0, alias="OLLAMA_TIMEOUT_SECONDS")
    # Smaller context + optional GPU layer cap reduce VRAM spikes (RTX 4070 12GB friendly)
    ollama_num_ctx: int = Field(default=4096, alias="OLLAMA_NUM_CTX")
    ollama_num_gpu: int | None = Field(default=None, alias="OLLAMA_NUM_GPU")

    # App server
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="DEBUG")
    dm_debug_panel: bool = Field(default=True, alias="DM_DEBUG_PANEL")

    # Storage
    database_url: str = Field(
        default=f"sqlite:///{(PROJECT_ROOT / 'data' / 'campaigns' / 'ai_dm.db').as_posix()}",
        alias="DATABASE_URL",
    )
    sourcebooks_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "sourcebooks"),
        alias="SOURCEBOOKS_DIR",
    )
    chroma_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "chroma"),
        alias="CHROMA_DIR",
    )
    rag_enabled: bool = Field(default=True, alias="RAG_ENABLED")
    rag_top_k: int = Field(default=4, alias="RAG_TOP_K")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dm_secrets: bool = Field(default=False, alias="LOG_DM_SECRETS")
    log_rag_chunk_text: bool = Field(default=False, alias="LOG_RAG_CHUNK_TEXT")

    @property
    def sourcebooks_path(self) -> Path:
        path = Path(self.sourcebooks_dir)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()

    @property
    def chroma_path(self) -> Path:
        path = Path(self.chroma_dir)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()

    @property
    def resolved_database_url(self) -> str:
        """Ensure relative sqlite paths resolve under PROJECT_ROOT."""
        url = self.database_url
        if url.startswith("sqlite:///./"):
            relative = url.removeprefix("sqlite:///./")
            return f"sqlite:///{(PROJECT_ROOT / relative).as_posix()}"
        if url.startswith("sqlite:///../") or url == "sqlite:///:memory:":
            return url
        if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
            # Absolute-looking path after sqlite:/// — leave as-is if drive-like or absolute
            rest = url.removeprefix("sqlite:///")
            candidate = Path(rest)
            if not candidate.is_absolute():
                return f"sqlite:///{(PROJECT_ROOT / rest).as_posix()}"
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
