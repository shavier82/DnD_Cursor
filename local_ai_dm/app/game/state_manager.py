"""Canonical state mutations — HP, conditions, inventory, combat, memory."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.game.actions import (
    AddConditionAction,
    AddMemoryAction,
    DamageCharacterAction,
    EndCombatAction,
    GameAction,
    GiveItemAction,
    HealCharacterAction,
    RemoveConditionAction,
    RemoveItemAction,
    RequestPlayerRollAction,
    RollDiceAction,
    SetLocationAction,
    StartCombatAction,
)
from app.game.dice import roll
from app.models import (
    Campaign,
    CampaignMemory,
    Character,
    Combatant,
    Encounter,
    InventoryItem,
    MemoryKind,
)

logger = logging.getLogger(__name__)


class StateError(ValueError):
    """Raised when a state mutation cannot be applied."""


class StateManager:
    """Apply validated GameAction objects to SQLite state."""

    def __init__(self, db: Session, campaign_id: str) -> None:
        self.db = db
        self.campaign_id = campaign_id

    def get_campaign(self) -> Campaign:
        campaign = self.db.get(Campaign, self.campaign_id)
        if campaign is None:
            raise StateError(f"Campaign not found: {self.campaign_id}")
        return campaign

    def get_character(self, character_id: str) -> Character:
        character = self.db.get(Character, character_id)
        if character is None or character.campaign_id != self.campaign_id:
            raise StateError(f"Character not found in campaign: {character_id}")
        return character

    def apply(self, action: GameAction) -> dict[str, Any]:
        handlers = {
            "damage_character": self._damage,
            "heal_character": self._heal,
            "add_condition": self._add_condition,
            "remove_condition": self._remove_condition,
            "set_location": self._set_location,
            "give_item": self._give_item,
            "remove_item": self._remove_item,
            "start_combat": self._start_combat,
            "end_combat": self._end_combat,
            "roll_dice": self._roll_dice,
            "request_player_roll": self._request_player_roll,
            "add_memory": self._add_memory,
        }
        handler = handlers.get(action.type)
        if handler is None:
            raise StateError(f"Unsupported action type: {action.type}")
        result = handler(action)  # type: ignore[arg-type]
        self.db.flush()
        return result

    def apply_many(self, actions: list[GameAction]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for action in actions:
            try:
                results.append({"ok": True, "type": action.type, "result": self.apply(action)})
            except StateError as exc:
                logger.warning("AI action failed validation/execution: %s (%s)", action.type, exc)
                results.append({"ok": False, "type": action.type, "error": str(exc)})
        return results

    def _damage(self, action: DamageCharacterAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        before = character.current_hp
        character.current_hp = max(0, character.current_hp - action.amount)
        return {
            "character_id": character.id,
            "name": character.name,
            "before": before,
            "after": character.current_hp,
            "amount": action.amount,
        }

    def _heal(self, action: HealCharacterAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        before = character.current_hp
        character.current_hp = min(character.max_hp, character.current_hp + action.amount)
        return {
            "character_id": character.id,
            "name": character.name,
            "before": before,
            "after": character.current_hp,
            "amount": action.amount,
        }

    def _add_condition(self, action: AddConditionAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        conditions = list(character.conditions or [])
        if action.condition not in conditions:
            conditions.append(action.condition)
        character.conditions = conditions
        return {"character_id": character.id, "conditions": conditions}

    def _remove_condition(self, action: RemoveConditionAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        conditions = [c for c in (character.conditions or []) if c != action.condition]
        character.conditions = conditions
        return {"character_id": character.id, "conditions": conditions}

    def _set_location(self, action: SetLocationAction) -> dict[str, Any]:
        campaign = self.get_campaign()
        campaign.current_location = action.location
        return {"location": action.location}

    def _give_item(self, action: GiveItemAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        existing = (
            self.db.query(InventoryItem)
            .filter(
                InventoryItem.character_id == character.id,
                InventoryItem.name == action.item,
            )
            .first()
        )
        if existing:
            existing.quantity += action.quantity
            item = existing
        else:
            item = InventoryItem(
                character_id=character.id,
                name=action.item,
                quantity=action.quantity,
            )
            self.db.add(item)
        self.db.flush()
        return {
            "character_id": character.id,
            "item": item.name,
            "quantity": item.quantity,
            "item_id": item.id,
        }

    def _remove_item(self, action: RemoveItemAction) -> dict[str, Any]:
        character = self.get_character(action.target)
        existing = (
            self.db.query(InventoryItem)
            .filter(
                InventoryItem.character_id == character.id,
                InventoryItem.name == action.item,
            )
            .first()
        )
        if existing is None:
            raise StateError(f"Item not found: {action.item}")
        if existing.quantity <= action.quantity:
            self.db.delete(existing)
            remaining = 0
        else:
            existing.quantity -= action.quantity
            remaining = existing.quantity
        return {
            "character_id": character.id,
            "item": action.item,
            "remaining": remaining,
        }

    def _start_combat(self, action: StartCombatAction) -> dict[str, Any]:
        campaign = self.get_campaign()
        active = (
            self.db.query(Encounter)
            .filter(
                Encounter.campaign_id == campaign.id,
                Encounter.status == "active",
            )
            .first()
        )
        if active:
            raise StateError("An encounter is already active")

        encounter = Encounter(campaign_id=campaign.id, name=action.name, status="active")
        self.db.add(encounter)
        self.db.flush()

        for character in campaign.characters:
            self.db.add(
                Combatant(
                    encounter_id=encounter.id,
                    name=character.name,
                    character_id=character.id,
                    max_hp=character.max_hp,
                    current_hp=character.current_hp,
                    armor_class=character.armor_class,
                    conditions=list(character.conditions or []),
                    is_player=True,
                )
            )
        self.db.flush()
        return {"encounter_id": encounter.id, "name": encounter.name}

    def _end_combat(self, action: EndCombatAction) -> dict[str, Any]:
        active = (
            self.db.query(Encounter)
            .filter(
                Encounter.campaign_id == self.campaign_id,
                Encounter.status == "active",
            )
            .first()
        )
        if active is None:
            raise StateError("No active encounter to end")
        active.status = "ended"
        return {"encounter_id": active.id, "status": "ended"}

    def _roll_dice(self, action: RollDiceAction) -> dict[str, Any]:
        result = roll(action.expression, mode=action.mode)
        payload = result.to_dict()
        if action.reason:
            payload["reason"] = action.reason
        return payload

    def _request_player_roll(self, action: RequestPlayerRollAction) -> dict[str, Any]:
        return action.model_dump()

    def _add_memory(self, action: AddMemoryAction) -> dict[str, Any]:
        kind = MemoryKind.DM_SECRET if action.kind == "dm_secret" else MemoryKind.CAMPAIGN
        memory = CampaignMemory(
            campaign_id=self.campaign_id,
            text=action.text,
            kind=kind,
            importance=action.importance,
            tags=list(action.tags or []),
            discovered=False,
        )
        self.db.add(memory)
        self.db.flush()
        return {"memory_id": memory.id, "kind": kind.value}
