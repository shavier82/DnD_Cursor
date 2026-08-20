"""Pydantic request/response schemas (API boundary)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    system: str = "D&D 5e (2024)"
    description: str = ""
    current_location: Optional[str] = None


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    system: str
    description: str
    current_location: Optional[str]
    state_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    player_name: Optional[str] = None
    race: Optional[str] = None
    character_class: Optional[str] = None
    level: int = Field(default=1, ge=1, le=20)
    max_hp: int = Field(default=10, ge=1)
    current_hp: Optional[int] = None
    armor_class: int = Field(default=10, ge=1)
    speed: int = Field(default=30, ge=0)
    ability_scores: dict[str, Any] = Field(default_factory=dict)
    saving_throws: dict[str, Any] = Field(default_factory=dict)
    skills: dict[str, Any] = Field(default_factory=dict)
    conditions: list[Any] = Field(default_factory=list)
    notes: str = ""


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    name: str
    player_name: Optional[str]
    race: Optional[str]
    character_class: Optional[str]
    level: int
    max_hp: int
    current_hp: int
    armor_class: int
    speed: int
    ability_scores: dict[str, Any]
    saving_throws: dict[str, Any]
    skills: dict[str, Any]
    conditions: list[Any]
    notes: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    character_id: Optional[str] = None


class ChatResponse(BaseModel):
    narration: str
    actions_executed: list[dict[str, Any]] = Field(default_factory=list)
    actions_rejected: list[dict[str, Any]] = Field(default_factory=list)
    pending_rolls: list[dict[str, Any]] = Field(default_factory=list)
    requires_player_input: bool = True
    message_id: str
    debug: Optional[dict[str, Any]] = None


class DiceRollRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=100)
    mode: str = Field(default="normal", pattern="^(normal|advantage|disadvantage)$")
    seed: Optional[int] = None


class DiceRollResponse(BaseModel):
    expression: str
    rolls: list[int]
    kept: list[int]
    dropped: list[int]
    modifier: int
    total: int
    mode: str
    natural_20: bool
    natural_1: bool
    is_critical_hit: bool
    is_critical_miss: bool
    detail: str


class HealthResponse(BaseModel):
    status: str
    version: str


class OllamaStatusResponse(BaseModel):
    available: bool
    url: str
    model: str
    message: str
    models: list[str] = Field(default_factory=list)


class DocumentIngestRequest(BaseModel):
    filenames: list[str] | None = None


class DocumentStatusResponse(BaseModel):
    rag_enabled: bool
    sourcebooks_dir: str
    indexed_chunks: int
    sources: list[str]
    available_files: list[str]
