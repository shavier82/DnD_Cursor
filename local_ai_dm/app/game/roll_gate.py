"""Deterministic roll-request gate.

The LLM often narrates past a check. Python decides when a PC roll is required.
"""

from __future__ import annotations

import re
from typing import Any

_NOT_ROLLED = re.compile(
    r"\b(i have not rolled|i haven't rolled|have not rolled|haven't rolled yet)\b",
    re.IGNORECASE,
)

_PATTERNS: list[tuple[re.Pattern[str], dict[str, Any]]] = [
    (
        re.compile(r"\b(climb|scale)\b", re.IGNORECASE),
        {"skill": "athletics", "ability": "strength", "reason": "Climb"},
    ),
    (
        re.compile(r"\b(hide|sneak|stealth)\b", re.IGNORECASE),
        {"skill": "stealth", "ability": "dexterity", "dc": 15, "reason": "Hide"},
    ),
    (
        re.compile(r"\b(search|look for|investigate)\b", re.IGNORECASE),
        {"skill": "perception", "ability": "wisdom", "reason": "Search"},
    ),
    (
        re.compile(r"\b(pick(?:ing)? (?:the )?lock|lockpick)\b", re.IGNORECASE),
        {"skill": "sleight of hand", "ability": "dexterity", "reason": "Pick a lock"},
    ),
    (
        re.compile(r"\b(jump|leap)\b", re.IGNORECASE),
        {"skill": "athletics", "ability": "strength", "reason": "Jump"},
    ),
    (
        re.compile(r"\b(swim)\b", re.IGNORECASE),
        {"skill": "athletics", "ability": "strength", "reason": "Swim"},
    ),
    (
        re.compile(r"\bgrapple\b", re.IGNORECASE),
        {"skill": "athletics", "ability": "strength", "reason": "Grapple"},
    ),
    (
        re.compile(r"\b(disarm|disable).{0,20}trap\b", re.IGNORECASE),
        {"skill": "sleight of hand", "ability": "dexterity", "reason": "Disarm a trap"},
    ),
]

_TRY_TO = re.compile(r"\b(i try to|i attempt to|trying to)\b", re.IGNORECASE)


def infer_player_roll(message: str) -> dict[str, Any] | None:
    """Return a request_player_roll payload, or None if no check is required."""
    text = (message or "").strip()
    if not text:
        return None

    explicit = bool(_NOT_ROLLED.search(text))
    attempting = bool(_TRY_TO.search(text))

    matched: dict[str, Any] | None = None
    for pattern, payload in _PATTERNS:
        if pattern.search(text):
            matched = dict(payload)
            break

    if matched is None:
        if explicit:
            return {
                "type": "request_player_roll",
                "skill": None,
                "ability": None,
                "dc": None,
                "mode": "normal",
                "reason": text[:180],
            }
        return None

    if not (explicit or attempting):
        # Risky verb without "try" / "have not rolled" — still require a roll
        # for climb/hide/search because failure matters.
        pass

    action = {
        "type": "request_player_roll",
        "skill": matched.get("skill"),
        "ability": matched.get("ability"),
        "dc": matched.get("dc"),
        "mode": "normal",
        "reason": matched.get("reason") or "Ability check",
    }
    return action


def ensure_player_roll_action(
    message: str, actions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Python owns PC check requests when intent is clear (climb/hide/search/...).

    The LLM often emits a partial request_player_roll (missing reason, skill stuffed
    into ability, a DC copied from the wrong RAG chunk). Replace those with the
    inferred check. If we cannot infer, keep the model actions as-is.
    """
    inferred = infer_player_roll(message)
    others = [
        a
        for a in actions
        if not (isinstance(a, dict) and a.get("type") == "request_player_roll")
    ]
    if inferred is not None:
        return others + [inferred]
    return list(actions)


def format_roll_call(roll: dict[str, Any]) -> str:
    skill = roll.get("skill") or roll.get("ability") or "ability check"
    dc = f" DC {roll['dc']}" if roll.get("dc") is not None else ""
    reason = roll.get("reason") or "this attempt"
    return (
        f"ROLL: {skill}{dc} — {reason}. "
        "The attempt is not resolved yet. Report the total after you roll."
    )
