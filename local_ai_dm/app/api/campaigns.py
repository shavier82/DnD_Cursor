"""Campaign API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.dm_agent import DMAgent
from app.ai.llm import OllamaError
from app.config import get_settings
from app.database import get_db
from app.schemas import (
    CampaignCreate,
    CampaignRead,
    CharacterCreate,
    CharacterRead,
    ChatRequest,
    ChatResponse,
)
from app.services import CampaignService, CharacterService, MessageService

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignRead)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> CampaignRead:
    campaign = CampaignService(db).create(payload)
    return CampaignRead.model_validate(campaign)


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db)) -> list[CampaignRead]:
    campaigns = CampaignService(db).list()
    return [CampaignRead.model_validate(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)) -> CampaignRead:
    campaign = CampaignService(db).get(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignRead.model_validate(campaign)


@router.post("/{campaign_id}/characters", response_model=CharacterRead)
def add_character(
    campaign_id: str,
    payload: CharacterCreate,
    db: Session = Depends(get_db),
) -> CharacterRead:
    try:
        character = CharacterService(db).create(campaign_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CharacterRead.model_validate(character)


@router.get("/{campaign_id}/characters", response_model=list[CharacterRead])
def list_characters(campaign_id: str, db: Session = Depends(get_db)) -> list[CharacterRead]:
    if CampaignService(db).get(campaign_id) is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    characters = CharacterService(db).list_for_campaign(campaign_id)
    return [CharacterRead.model_validate(c) for c in characters]


@router.get("/{campaign_id}/messages")
def list_messages(campaign_id: str, db: Session = Depends(get_db), limit: int = 100):
    if CampaignService(db).get(campaign_id) is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    messages = MessageService(db).list_for_campaign(campaign_id, limit=limit)
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "meta_json": m.meta_json,
        }
        for m in messages
    ]


@router.post("/{campaign_id}/chat", response_model=ChatResponse)
def chat(
    campaign_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    if CampaignService(db).get(campaign_id) is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    settings = get_settings()
    agent = DMAgent(db, campaign_id, debug=settings.dm_debug_panel)
    try:
        result = agent.handle_player_message(payload.message)
    except OllamaError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(**result)
