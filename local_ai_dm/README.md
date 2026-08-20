"""
# Local AI Dungeon Master

Self-hosted AI Dungeon Master for private tabletop play on Windows.
Uses **Ollama** for local LLM inference. Canonical game state lives in **SQLite**,
not in model prose.

## Status

| Milestone | Status |
|-----------|--------|
| **M1** — FastAPI app, campaigns, characters, chat, dice, SQLite persistence | Runnable |
| **M2** — Sourcebook RAG (ChromaDB + embeddings) | Runnable — ingest purchased files from `C:/DnD/Sourcebooks` |
| Fine-tuning / LoRA | Out of scope for now |

## Requirements

- Python 3.10+ (3.12+ preferred; this machine currently has 3.10)
- [Ollama](https://ollama.com) installed and running
- A local model, e.g. `ollama pull qwen3:4b` (recommended on 12GB GPUs)

On a 12GB GPU (RTX 4070), `qwen3:8b` plus context can exceed VRAM. Default is `qwen3:4b` with `OLLAMA_NUM_CTX=4096`. To try 8B later, set `OLLAMA_MODEL=qwen3:8b` and optionally `OLLAMA_NUM_GPU=20`.

## Setup

```powershell
cd local_ai_dm
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` if needed (`OLLAMA_URL`, `OLLAMA_MODEL`).

## Run

```powershell
cd local_ai_dm
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000

## Tests

```powershell
cd local_ai_dm
pytest -q
```

## Architecture notes

1. **LLM is not the database.** Structured actions (`damage_character`, `roll_dice`, …) are validated with Pydantic and executed by Python/`StateManager`.
2. **Dice are deterministic Python** (`app/game/dice.py`). The model must request `roll_dice` instead of inventing totals.
3. **DM secrets** are stored as `CampaignMemory` with `kind=dm_secret` and are injected into prompts but must not be shown in the player UI.
4. **RAG** reads legally obtained files from `SOURCEBOOKS_DIR` (default `C:/DnD/Sourcebooks`), chunks them, embeds locally, and injects a few excerpts into the DM prompt. Full books are never exposed via the API.

Index them once:

```powershell
# from local_ai_dm, with venv active
# POST /api/documents/ingest   (or use the DM Debug "Ingest sourcebooks" button)
```

- `GET /api/documents/status`
- `POST /api/documents/ingest`

## API (M1)

- `GET /api/health`
- `GET /api/ollama/status`
- `POST /api/dice/roll`
- `POST /api/campaigns`
- `GET /api/campaigns`
- `GET /api/campaigns/{id}`
- `POST /api/campaigns/{id}/characters`
- `GET /api/campaigns/{id}/characters`
- `GET /api/campaigns/{id}/messages`
- `POST /api/campaigns/{id}/chat`

## Copyright

Personal use with legally obtained RPG material only. Do not redistribute sourcebook contents. Milestone 2 will retrieve limited excerpts for play, not expose full documents.
"""
