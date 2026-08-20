"""Campaign and character service layer."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy.orm import Session, joinedload

from app.models import Campaign, Character, ChatMessage
from app.schemas import CampaignCreate, CharacterCreate


class CampaignService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: CampaignCreate) -> Campaign:
        campaign = Campaign(
            name=payload.name,
            system=payload.system,
            description=payload.description,
            current_location=payload.current_location,
            state_json={},
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def list(self) -> Sequence[Campaign]:
        return self.db.query(Campaign).order_by(Campaign.created_at.desc()).all()

    def get(self, campaign_id: str) -> Campaign | None:
        return (
            self.db.query(Campaign)
            .options(
                joinedload(Campaign.characters),
                joinedload(Campaign.quests),
                joinedload(Campaign.messages),
            )
            .filter(Campaign.id == campaign_id)
            .first()
        )


class CharacterService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, campaign_id: str, payload: CharacterCreate) -> Character:
        campaign = self.db.get(Campaign, campaign_id)
        if campaign is None:
            raise ValueError("Campaign not found")

        current_hp = payload.current_hp if payload.current_hp is not None else payload.max_hp
        character = Character(
            campaign_id=campaign_id,
            name=payload.name,
            player_name=payload.player_name,
            race=payload.race,
            character_class=payload.character_class,
            level=payload.level,
            max_hp=payload.max_hp,
            current_hp=min(current_hp, payload.max_hp),
            armor_class=payload.armor_class,
            speed=payload.speed,
            ability_scores=payload.ability_scores,
            saving_throws=payload.saving_throws,
            skills=payload.skills,
            conditions=payload.conditions,
            notes=payload.notes,
        )
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        return character

    def list_for_campaign(self, campaign_id: str) -> Sequence[Character]:
        return (
            self.db.query(Character)
            .filter(Character.campaign_id == campaign_id)
            .order_by(Character.name.asc())
            .all()
        )


class MessageService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_campaign(self, campaign_id: str, limit: int = 100) -> Sequence[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.campaign_id == campaign_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )
