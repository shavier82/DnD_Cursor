"""Ollama HTTP client for local LLM inference."""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Raised when Ollama is unreachable or returns an error."""


class OllamaClient:
    """Thin wrapper around the Ollama HTTP API.

    Model name and base URL come from Settings — never hard-code a model
    throughout the application.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_url.rstrip("/")
        self.model = self.settings.ollama_model
        self.timeout = self.settings.ollama_timeout_seconds

    def status(self) -> dict[str, Any]:
        """Check connectivity and optionally list local models."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                payload = response.json()
                models = [m.get("name", "") for m in payload.get("models", [])]
                model_present = any(
                    self.model == name or name.startswith(f"{self.model}:") or name.startswith(self.model)
                    for name in models
                )
                if not models:
                    message = "Ollama is reachable but no models are installed."
                elif not model_present:
                    message = (
                        f"Ollama is reachable. Configured model '{self.model}' "
                        f"was not found in installed models."
                    )
                else:
                    message = "Ollama is available."
                return {
                    "available": True,
                    "url": self.base_url,
                    "model": self.model,
                    "message": message,
                    "models": models,
                }
        except httpx.TimeoutException:
            logger.error("Ollama status check timed out (%s)", self.base_url)
            return {
                "available": False,
                "url": self.base_url,
                "model": self.model,
                "message": "Ollama timed out. Is it running?",
                "models": [],
            }
        except httpx.HTTPError as exc:
            logger.error("Ollama status check failed: %s", exc)
            return {
                "available": False,
                "url": self.base_url,
                "model": self.model,
                "message": f"Ollama unavailable: {exc}",
                "models": [],
            }

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        format_json: bool = False,
    ) -> dict[str, Any]:
        """Call /api/chat and return the raw JSON response.

        Raises OllamaError on failure.
        """
        options: dict[str, Any] = {
            "temperature": temperature,
            "num_ctx": self.settings.ollama_num_ctx,
        }
        if self.settings.ollama_num_gpu is not None:
            options["num_gpu"] = self.settings.ollama_num_gpu

        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        if format_json:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            logger.error("Ollama chat timed out after %ss", self.timeout)
            raise OllamaError(
                f"Ollama timed out after {self.timeout}s. Try a smaller model or raise OLLAMA_TIMEOUT_SECONDS."
            ) from exc
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response is not None else ""
            logger.error("Ollama HTTP error %s: %s", exc.response.status_code, body)
            lower = body.lower()
            if "out of memory" in lower or "cudamalloc" in lower:
                raise OllamaError(
                    "Ollama ran out of GPU memory loading this model. "
                    "Use a smaller model (OLLAMA_MODEL=qwen3:4b) or lower OLLAMA_NUM_CTX / OLLAMA_NUM_GPU."
                ) from exc
            raise OllamaError(f"Ollama HTTP {exc.response.status_code}: {body}") from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama connection error: %s", exc)
            raise OllamaError(
                "Cannot reach Ollama. Start it with `ollama serve` and ensure OLLAMA_URL is correct."
            ) from exc

    def generate_text(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        format_json: bool = False,
    ) -> str:
        """Return assistant message content only."""
        data = self.chat(
            messages,
            model=model,
            temperature=temperature,
            format_json=format_json,
        )
        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str):
            raise OllamaError("Ollama response missing message.content")
        return content
