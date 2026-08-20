"""Deterministic game mechanics (dice, combat helpers, state mutations)."""

from app.game.dice import DiceError, DiceResult, RollMode, parse_expression, roll, roll_with_modifier

__all__ = [
    "DiceError",
    "DiceResult",
    "RollMode",
    "parse_expression",
    "roll",
    "roll_with_modifier",
]
