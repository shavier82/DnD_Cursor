"""Campaign / character persistence and HP mutation tests."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.game.actions import validate_actions
from app.game.state_manager import StateManager
from app.models import Character
from app.schemas import CampaignCreate, CharacterCreate
from app.services import CampaignService, CharacterService


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_create_campaign_and_character(db):
    campaign = CampaignService(db).create(
        CampaignCreate(name="Test Saga", current_location="Tavern")
    )
    assert campaign.id
    assert campaign.name == "Test Saga"

    character = CharacterService(db).create(
        campaign.id,
        CharacterCreate(name="Torgga", max_hp=30, armor_class=16, character_class="Cleric"),
    )
    assert character.campaign_id == campaign.id
    assert character.current_hp == 30

    # Persistence within same session / flush cycle
    loaded = db.get(Character, character.id)
    assert loaded is not None
    assert loaded.name == "Torgga"


def test_damage_and_heal(db):
    campaign = CampaignService(db).create(CampaignCreate(name="HP Test"))
    character = CharacterService(db).create(
        campaign.id,
        CharacterCreate(name="Eglath", max_hp=40, current_hp=40),
    )
    sm = StateManager(db, campaign.id)

    accepted, rejected = validate_actions(
        [{"type": "damage_character", "target": character.id, "amount": 12}]
    )
    assert not rejected
    results = sm.apply_many(list(accepted))
    db.commit()
    db.refresh(character)
    assert character.current_hp == 28
    assert results[0]["ok"] is True

    accepted, _ = validate_actions(
        [{"type": "heal_character", "target": character.id, "amount": 5}]
    )
    sm.apply_many(list(accepted))
    db.commit()
    db.refresh(character)
    assert character.current_hp == 33


def test_damage_does_not_go_below_zero(db):
    campaign = CampaignService(db).create(CampaignCreate(name="KO Test"))
    character = CharacterService(db).create(
        campaign.id,
        CharacterCreate(name="Hero", max_hp=10, current_hp=5),
    )
    sm = StateManager(db, campaign.id)
    accepted, _ = validate_actions(
        [{"type": "damage_character", "target": character.id, "amount": 99}]
    )
    sm.apply_many(list(accepted))
    db.commit()
    db.refresh(character)
    assert character.current_hp == 0


def test_llm_athletics_payload_validates_after_normalize():
    from app.game.actions import parse_game_action

    action = parse_game_action(
        {"type": "request_player_roll", "ability": "Athletics", "dc": 10}
    )
    assert action.type == "request_player_roll"
    assert action.skill == "athletics"
    assert action.ability == "strength"
    assert action.reason == "athletics"
    assert action.dc == 10


def test_invalid_ai_actions_rejected():
    accepted, rejected = validate_actions(
        [
            {"type": "damage_character", "target": "x", "amount": -5},
            {"type": "explode_server", "cmd": "rm -rf /"},
            "not-an-object",
            {"type": "heal_character", "target": "x", "amount": 3},
        ]
    )
    assert len(accepted) == 1
    assert accepted[0].type == "heal_character"
    assert len(rejected) == 3


def test_request_player_roll_is_valid_and_does_not_change_hp(db):
    campaign = CampaignService(db).create(CampaignCreate(name="Roll Ask"))
    character = CharacterService(db).create(
        campaign.id,
        CharacterCreate(name="Torgga", max_hp=20, current_hp=20),
    )
    sm = StateManager(db, campaign.id)
    accepted, rejected = validate_actions(
        [
            {
                "type": "request_player_roll",
                "skill": "athletics",
                "ability": "strength",
                "dc": 15,
                "reason": "Climb the city wall",
            }
        ]
    )
    assert not rejected
    results = sm.apply_many(list(accepted))
    db.commit()
    db.refresh(character)
    assert character.current_hp == 20
    assert results[0]["ok"] is True
    assert results[0]["result"]["skill"] == "athletics"


def test_campaign_survives_new_session():
    """Simulate app restart with a file-backed temp DB via two engines on same file."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        url = f"sqlite:///{db_path.as_posix()}"

        engine1 = create_engine(url, future=True)
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(bind=engine1, future=True)
        s1 = Session1()
        campaign = CampaignService(s1).create(CampaignCreate(name="Persistent"))
        CharacterService(s1).create(campaign.id, CharacterCreate(name="A", max_hp=12))
        cid = campaign.id
        s1.close()
        engine1.dispose()

        engine2 = create_engine(url, future=True)
        Session2 = sessionmaker(bind=engine2, future=True)
        s2 = Session2()
        loaded = CampaignService(s2).get(cid)
        assert loaded is not None
        assert loaded.name == "Persistent"
        chars = CharacterService(s2).list_for_campaign(cid)
        assert len(chars) == 1
        assert chars[0].name == "A"
        s2.close()
        engine2.dispose()
