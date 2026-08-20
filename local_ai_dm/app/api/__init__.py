"""Dice and health/status API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import __version__
from app.ai.llm import OllamaClient
from app.game.dice import DiceError, roll
from app.schemas import (
    DiceRollRequest,
    DiceRollResponse,
    HealthResponse,
    OllamaStatusResponse,
)

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get("/ollama/status", response_model=OllamaStatusResponse)
def ollama_status() -> OllamaStatusResponse:
    status = OllamaClient().status()
    return OllamaStatusResponse(**status)


@router.post("/dice/roll", response_model=DiceRollResponse)
def dice_roll(payload: DiceRollRequest) -> DiceRollResponse:
    try:
        result = roll(payload.expression, mode=payload.mode, seed=payload.seed)
    except DiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    data = result.to_dict()
    return DiceRollResponse(
        expression=data["expression"],
        rolls=data["rolls"],
        kept=data["kept"],
        dropped=data["dropped"],
        modifier=data["modifier"],
        total=data["total"],
        mode=data["mode"],
        natural_20=data["natural_20"],
        natural_1=data["natural_1"],
        is_critical_hit=data["is_critical_hit"],
        is_critical_miss=data["is_critical_miss"],
        detail=data["detail"],
    )
