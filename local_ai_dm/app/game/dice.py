"""Deterministic dice engine.

The LLM must never invent dice results when this subsystem is available.
All rolls are produced here and returned as structured data.
"""

from __future__ import annotations

import random
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DiceError(ValueError):
    """Raised when a dice expression is invalid."""


class RollMode(str, Enum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


# Examples: 1d20, 2d6+3, 4d8-2, 2d20kh1, 2d20kl1, d20 (implied 1)
_DICE_RE = re.compile(
    r"""
    ^\s*
    (?P<count>\d*)d(?P<sides>\d+)
    (?:(?P<keep_op>kh|kl)(?P<keep_n>\d+))?
    (?:(?P<mod_sign>[+-])(?P<mod_value>\d+))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


@dataclass
class DiceResult:
    expression: str
    rolls: list[int]
    kept: list[int]
    dropped: list[int]
    modifier: int
    total: int
    mode: str = RollMode.NORMAL.value
    natural_20: bool = False
    natural_1: bool = False
    is_critical_hit: bool = False  # natural 20 on a d20 check/attack context
    is_critical_miss: bool = False  # natural 1 on a d20 check/attack context
    sides: int = 20
    count: int = 1
    detail: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Compact primary shape requested by the product spec
        return {
            "expression": data["expression"],
            "rolls": data["rolls"],
            "kept": data["kept"],
            "dropped": data["dropped"],
            "modifier": data["modifier"],
            "total": data["total"],
            "mode": data["mode"],
            "natural_20": data["natural_20"],
            "natural_1": data["natural_1"],
            "is_critical_hit": data["is_critical_hit"],
            "is_critical_miss": data["is_critical_miss"],
            "sides": data["sides"],
            "count": data["count"],
            "detail": data["detail"],
            "meta": data["meta"],
        }


def parse_expression(expression: str) -> dict[str, Any]:
    """Parse a dice expression into structured components (no rolling)."""
    if not expression or not expression.strip():
        raise DiceError("Empty dice expression")

    match = _DICE_RE.match(expression.strip())
    if not match:
        raise DiceError(f"Invalid dice expression: {expression!r}")

    count_raw = match.group("count")
    count = int(count_raw) if count_raw else 1
    sides = int(match.group("sides"))
    keep_op = (match.group("keep_op") or "").lower() or None
    keep_n = int(match.group("keep_n")) if match.group("keep_n") else None

    mod_sign = match.group("mod_sign")
    mod_value = match.group("mod_value")
    modifier = 0
    if mod_sign and mod_value:
        modifier = int(mod_value) if mod_sign == "+" else -int(mod_value)

    if count < 1 or count > 100:
        raise DiceError("Dice count must be between 1 and 100")
    if sides < 2 or sides > 1000:
        raise DiceError("Die sides must be between 2 and 1000")
    if keep_op and (keep_n is None or keep_n < 1 or keep_n > count):
        raise DiceError("Keep count must be between 1 and the number of dice")

    return {
        "count": count,
        "sides": sides,
        "keep_op": keep_op,
        "keep_n": keep_n,
        "modifier": modifier,
        "normalized": _normalize_expression(count, sides, keep_op, keep_n, modifier),
    }


def _normalize_expression(
    count: int,
    sides: int,
    keep_op: str | None,
    keep_n: int | None,
    modifier: int,
) -> str:
    base = f"{count}d{sides}"
    if keep_op and keep_n is not None:
        base += f"{keep_op}{keep_n}"
    if modifier > 0:
        base += f"+{modifier}"
    elif modifier < 0:
        base += str(modifier)
    return base


def _roll_die(sides: int, rng: random.Random) -> int:
    return rng.randint(1, sides)


def _apply_keep(
    rolls: list[int], keep_op: str | None, keep_n: int | None
) -> tuple[list[int], list[int]]:
    if not keep_op or keep_n is None:
        return list(rolls), []

    indexed = list(enumerate(rolls))
    if keep_op == "kh":
        selected = sorted(indexed, key=lambda x: x[1], reverse=True)[:keep_n]
    else:  # kl
        selected = sorted(indexed, key=lambda x: x[1])[:keep_n]

    selected_indices = {i for i, _ in selected}
    kept = [v for i, v in indexed if i in selected_indices]
    dropped = [v for i, v in indexed if i not in selected_indices]
    # Preserve original relative order of kept dice
    kept = [v for i, v in indexed if i in selected_indices]
    return kept, dropped


def roll(
    expression: str,
    *,
    mode: RollMode | str = RollMode.NORMAL,
    seed: int | None = None,
    rng: random.Random | None = None,
) -> DiceResult:
    """Roll a dice expression.

    Advantage / disadvantage apply to a single d20 (or Nd20kh1 / Nd20kl1 patterns):
    - advantage: roll 2d20kh1 (+ any modifier from the expression)
    - disadvantage: roll 2d20kl1 (+ any modifier)
    """
    if rng is None:
        rng = random.Random(seed)

    mode_enum = RollMode(mode) if not isinstance(mode, RollMode) else mode
    parsed = parse_expression(expression)
    count = parsed["count"]
    sides = parsed["sides"]
    keep_op = parsed["keep_op"]
    keep_n = parsed["keep_n"]
    modifier = parsed["modifier"]

    # Advantage/disadvantage rewrite for d20 checks
    if mode_enum in (RollMode.ADVANTAGE, RollMode.DISADVANTAGE):
        if sides != 20:
            raise DiceError("Advantage/disadvantage only supported for d20 expressions")
        if keep_op is not None and not (count == 2 and keep_n == 1):
            raise DiceError(
                "Cannot combine custom keep rules with advantage/disadvantage"
            )
        count = 2
        keep_op = "kh" if mode_enum == RollMode.ADVANTAGE else "kl"
        keep_n = 1

    rolls = [_roll_die(sides, rng) for _ in range(count)]
    kept, dropped = _apply_keep(rolls, keep_op, keep_n)
    total = sum(kept) + modifier

    # Natural 20 / 1 detection: based on kept d20 face(s)
    natural_20 = sides == 20 and any(r == 20 for r in kept)
    natural_1 = sides == 20 and any(r == 1 for r in kept)
    # Critical hit/miss: classic single-die attack roll semantics
    is_critical_hit = sides == 20 and len(kept) == 1 and kept[0] == 20
    is_critical_miss = sides == 20 and len(kept) == 1 and kept[0] == 1

    normalized = _normalize_expression(count, sides, keep_op, keep_n, modifier)
    detail_parts = [f"rolls={rolls}"]
    if dropped:
        detail_parts.append(f"kept={kept}")
        detail_parts.append(f"dropped={dropped}")
    if modifier:
        detail_parts.append(f"modifier={modifier:+d}")
    detail_parts.append(f"total={total}")

    return DiceResult(
        expression=normalized,
        rolls=rolls,
        kept=kept,
        dropped=dropped,
        modifier=modifier,
        total=total,
        mode=mode_enum.value,
        natural_20=natural_20,
        natural_1=natural_1,
        is_critical_hit=is_critical_hit,
        is_critical_miss=is_critical_miss,
        sides=sides,
        count=count,
        detail=", ".join(detail_parts),
        meta={"original_expression": expression.strip()},
    )


def roll_with_modifier(
    sides: int = 20,
    *,
    modifier: int = 0,
    mode: RollMode | str = RollMode.NORMAL,
    seed: int | None = None,
) -> DiceResult:
    """Convenience helper for ability checks / attacks."""
    expression = f"1d{sides}"
    if modifier > 0:
        expression += f"+{modifier}"
    elif modifier < 0:
        expression += str(modifier)
    return roll(expression, mode=mode, seed=seed)
