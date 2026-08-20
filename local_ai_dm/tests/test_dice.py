"""Dice engine unit tests — no LLM required."""

from __future__ import annotations

import pytest

from app.game.dice import DiceError, RollMode, parse_expression, roll


class TestParseExpression:
    def test_simple_d20(self):
        parsed = parse_expression("1d20")
        assert parsed["count"] == 1
        assert parsed["sides"] == 20
        assert parsed["modifier"] == 0
        assert parsed["keep_op"] is None

    def test_implied_count(self):
        parsed = parse_expression("d20")
        assert parsed["count"] == 1
        assert parsed["normalized"] == "1d20"

    def test_modifier_positive(self):
        parsed = parse_expression("1d20+5")
        assert parsed["modifier"] == 5
        assert parsed["normalized"] == "1d20+5"

    def test_modifier_negative(self):
        parsed = parse_expression("4d8-2")
        assert parsed["count"] == 4
        assert parsed["sides"] == 8
        assert parsed["modifier"] == -2

    def test_keep_highest(self):
        parsed = parse_expression("2d20kh1")
        assert parsed["keep_op"] == "kh"
        assert parsed["keep_n"] == 1

    def test_keep_lowest(self):
        parsed = parse_expression("2d20kl1")
        assert parsed["keep_op"] == "kl"
        assert parsed["keep_n"] == 1

    def test_invalid_expression(self):
        with pytest.raises(DiceError):
            parse_expression("not-dice")

    def test_empty_expression(self):
        with pytest.raises(DiceError):
            parse_expression("")


class TestRoll:
    def test_deterministic_with_seed(self):
        a = roll("1d20+5", seed=42)
        b = roll("1d20+5", seed=42)
        assert a.to_dict() == b.to_dict()
        assert a.modifier == 5
        assert a.total == a.rolls[0] + 5

    def test_2d6_plus_modifier(self):
        result = roll("2d6+3", seed=1)
        assert len(result.rolls) == 2
        assert result.modifier == 3
        assert result.total == sum(result.rolls) + 3
        assert all(1 <= r <= 6 for r in result.rolls)

    def test_keep_highest(self):
        # Force known rolls via a custom rng sequence by using seed search —
        # instead, monkey the Random by rolling many times and checking invariants.
        result = roll("2d20kh1", seed=7)
        assert len(result.rolls) == 2
        assert len(result.kept) == 1
        assert len(result.dropped) == 1
        assert result.kept[0] == max(result.rolls)
        assert result.total == result.kept[0]

    def test_keep_lowest(self):
        result = roll("2d20kl1", seed=7)
        assert result.kept[0] == min(result.rolls)
        assert result.total == result.kept[0]

    def test_advantage_keeps_highest(self):
        result = roll("1d20+2", mode=RollMode.ADVANTAGE, seed=11)
        assert result.mode == "advantage"
        assert len(result.rolls) == 2
        assert result.kept[0] == max(result.rolls)
        assert result.total == result.kept[0] + 2

    def test_disadvantage_keeps_lowest(self):
        result = roll("1d20+2", mode=RollMode.DISADVANTAGE, seed=11)
        assert result.mode == "disadvantage"
        assert len(result.rolls) == 2
        assert result.kept[0] == min(result.rolls)
        assert result.total == result.kept[0] + 2

    def test_advantage_rejects_non_d20(self):
        with pytest.raises(DiceError):
            roll("2d6", mode=RollMode.ADVANTAGE)

    def test_natural_20_and_critical(self):
        # Find a seed that produces a natural 20 on 1d20
        found = None
        for seed in range(5000):
            result = roll("1d20", seed=seed)
            if result.rolls[0] == 20:
                found = result
                break
        assert found is not None
        assert found.natural_20 is True
        assert found.is_critical_hit is True
        assert found.is_critical_miss is False

    def test_natural_1_and_critical_miss(self):
        found = None
        for seed in range(5000):
            result = roll("1d20", seed=seed)
            if result.rolls[0] == 1:
                found = result
                break
        assert found is not None
        assert found.natural_1 is True
        assert found.is_critical_miss is True
        assert found.is_critical_hit is False

    def test_structured_dict_shape(self):
        result = roll("1d20+5", seed=0)
        data = result.to_dict()
        assert set(data.keys()) >= {
            "expression",
            "rolls",
            "modifier",
            "total",
        }
        assert data["expression"] == "1d20+5"
        assert data["modifier"] == 5
        assert data["total"] == data["rolls"][0] + 5
