"""Validated structured actions produced by the DM LLM.

LLM output is untrusted. Every action must pass Pydantic validation
before Python mutates canonical SQLite state. Never use eval().
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter, ValidationError, model_validator


class DamageCharacterAction(BaseModel):
    type: Literal["damage_character"] = "damage_character"
    target: str = Field(description="Character ID")
    amount: int = Field(ge=0, le=10_000)


class HealCharacterAction(BaseModel):
    type: Literal["heal_character"] = "heal_character"
    target: str
    amount: int = Field(ge=0, le=10_000)


class AddConditionAction(BaseModel):
    type: Literal["add_condition"] = "add_condition"
    target: str
    condition: str = Field(min_length=1, max_length=100)


class RemoveConditionAction(BaseModel):
    type: Literal["remove_condition"] = "remove_condition"
    target: str
    condition: str = Field(min_length=1, max_length=100)


class SetLocationAction(BaseModel):
    type: Literal["set_location"] = "set_location"
    location: str = Field(min_length=1, max_length=200)


class GiveItemAction(BaseModel):
    type: Literal["give_item"] = "give_item"
    target: str
    item: str = Field(min_length=1, max_length=200)
    quantity: int = Field(default=1, ge=1, le=1000)


class RemoveItemAction(BaseModel):
    type: Literal["remove_item"] = "remove_item"
    target: str
    item: str = Field(min_length=1, max_length=200)
    quantity: int = Field(default=1, ge=1, le=1000)


class StartCombatAction(BaseModel):
    type: Literal["start_combat"] = "start_combat"
    name: str = Field(default="Combat", max_length=200)


class EndCombatAction(BaseModel):
    type: Literal["end_combat"] = "end_combat"


class RollDiceAction(BaseModel):
    type: Literal["roll_dice"] = "roll_dice"
    expression: str = Field(min_length=1, max_length=100)
    mode: Literal["normal", "advantage", "disadvantage"] = "normal"
    # Optional label for narration; result always comes from Python dice engine
    reason: Optional[str] = Field(default=None, max_length=200)


SKILL_ABILITIES = {
    "athletics": "strength",
    "acrobatics": "dexterity",
    "sleight of hand": "dexterity",
    "stealth": "dexterity",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "animal handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}


class RequestPlayerRollAction(BaseModel):
    """Ask the human player to roll. Do not resolve the check in narration."""

    type: Literal["request_player_roll"] = "request_player_roll"
    skill: Optional[str] = Field(default=None, max_length=50)
    ability: Optional[str] = Field(default=None, max_length=50)
    dc: Optional[int] = Field(default=None, ge=1, le=40)
    mode: Literal["normal", "advantage", "disadvantage"] = "normal"
    reason: str = Field(default="Ability check", min_length=1, max_length=200)

    @model_validator(mode="before")
    @classmethod
    def normalize_skill_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        skill = str(data.get("skill") or "").strip().lower()
        ability = str(data.get("ability") or "").strip().lower()
        if ability in SKILL_ABILITIES and not skill:
            data["skill"] = ability
            data["ability"] = SKILL_ABILITIES[ability]
        elif skill in SKILL_ABILITIES:
            data["skill"] = skill
            if not ability or ability in SKILL_ABILITIES:
                data["ability"] = SKILL_ABILITIES[skill]
        if not str(data.get("reason") or "").strip():
            data["reason"] = data.get("skill") or data.get("ability") or "Ability check"
        return data


class AddMemoryAction(BaseModel):
    type: Literal["add_memory"] = "add_memory"
    text: str = Field(min_length=1, max_length=2000)
    importance: int = Field(default=5, ge=1, le=10)
    tags: list[str] = Field(default_factory=list)
    kind: Literal["campaign", "dm_secret"] = "campaign"


GameAction = Annotated[
    Union[
        DamageCharacterAction,
        HealCharacterAction,
        AddConditionAction,
        RemoveConditionAction,
        SetLocationAction,
        GiveItemAction,
        RemoveItemAction,
        StartCombatAction,
        EndCombatAction,
        RollDiceAction,
        RequestPlayerRollAction,
        AddMemoryAction,
    ],
    Field(discriminator="type"),
]

_action_adapter: TypeAdapter[GameAction] = TypeAdapter(GameAction)


class DMAgentResponse(BaseModel):
    narration: str = Field(min_length=1)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    requires_player_input: bool = True


def parse_game_action(raw: dict[str, Any]) -> GameAction:
    return _action_adapter.validate_python(raw)


def validate_actions(
    raw_actions: list[Any],
) -> tuple[list[GameAction], list[dict[str, Any]]]:
    """Validate a list of action dicts. Returns (accepted, rejected)."""
    accepted: list[GameAction] = []
    rejected: list[dict[str, Any]] = []
    for item in raw_actions:
        if not isinstance(item, dict):
            rejected.append({"action": item, "error": "Action must be an object"})
            continue
        try:
            accepted.append(parse_game_action(item))
        except ValidationError as exc:
            rejected.append({"action": item, "error": exc.errors()})
    return accepted, rejected
