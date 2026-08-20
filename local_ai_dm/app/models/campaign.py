"""SQLAlchemy ORM models for campaign state.

Canonical game state lives here — not in LLM prose.
JSON columns are used for flexible v1 fields (ability scores, skills, etc.).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MemoryKind(str, enum.Enum):
    CAMPAIGN = "campaign"
    DM_SECRET = "dm_secret"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    system: Mapped[str] = mapped_column(String(100), default="D&D 5e (2024)")
    description: Mapped[str] = mapped_column(Text, default="")
    current_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    # Free-form structured snapshot for UI / context builder
    state_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    characters: Mapped[list[Character]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    npcs: Mapped[list[NPC]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    locations: Mapped[list[Location]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    quests: Mapped[list[Quest]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    encounters: Mapped[list[Encounter]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    memories: Mapped[list[CampaignMemory]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    player_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    race: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    character_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    max_hp: Mapped[int] = mapped_column(Integer, default=10)
    current_hp: Mapped[int] = mapped_column(Integer, default=10)
    armor_class: Mapped[int] = mapped_column(Integer, default=10)
    speed: Mapped[int] = mapped_column(Integer, default=30)
    # {"str": 10, "dex": 14, ...}
    ability_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    saving_throws: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    skills: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    conditions: Mapped[list[Any]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    campaign: Mapped[Campaign] = relationship(back_populates="characters")
    inventory: Mapped[list[InventoryItem]] = relationship(
        back_populates="character", cascade="all, delete-orphan"
    )


class NPC(Base):
    __tablename__ = "npcs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    disposition: Mapped[str] = mapped_column(String(100), default="neutral")
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    secrets: Mapped[str] = mapped_column(Text, default="")  # DM-only; never show to players
    stats_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    relationship_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="npcs")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    parent_location_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    secrets: Mapped[str] = mapped_column(Text, default="")
    meta_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="locations")


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active|completed|failed
    objectives_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="quests")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")
    meta_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    character: Mapped[Character] = relationship(back_populates="inventory")


class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), default="Encounter")
    status: Mapped[str] = mapped_column(String(50), default="active")  # active|ended
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    current_turn_index: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="encounters")
    combatants: Mapped[list[Combatant]] = relationship(
        back_populates="encounter", cascade="all, delete-orphan"
    )


class Combatant(Base):
    __tablename__ = "combatants"
    __table_args__ = (UniqueConstraint("encounter_id", "name", name="uq_encounter_combatant_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    encounter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("encounters.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # Optional link to a PC
    character_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    initiative: Mapped[int] = mapped_column(Integer, default=0)
    max_hp: Mapped[int] = mapped_column(Integer, default=1)
    current_hp: Mapped[int] = mapped_column(Integer, default=1)
    armor_class: Mapped[int] = mapped_column(Integer, default=10)
    conditions: Mapped[list[Any]] = mapped_column(JSON, default=list)
    is_player: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    encounter: Mapped[Encounter] = relationship(back_populates="combatants")


class CampaignMemory(Base):
    __tablename__ = "campaign_memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[MemoryKind] = mapped_column(
        Enum(MemoryKind), default=MemoryKind.CAMPAIGN, index=True
    )
    importance: Mapped[int] = mapped_column(Integer, default=5)  # 1-10
    tags: Mapped[list[Any]] = mapped_column(JSON, default=list)
    discovered: Mapped[bool] = mapped_column(Boolean, default=False)  # for DM secrets
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="memories")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user|assistant|system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Structured payload from DM agent (actions, debug, etc.) — never trust blindly
    meta_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    campaign: Mapped[Campaign] = relationship(back_populates="messages")
