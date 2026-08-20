"""Tests for deterministic PC roll requests."""

from app.game.roll_gate import ensure_player_roll_action, infer_player_roll


def test_climb_without_roll_requests_athletics():
    action = infer_player_roll("I try to climb the wall. I have not rolled.")
    assert action is not None
    assert action["skill"] == "athletics"
    assert action["ability"] == "strength"
    assert action["reason"] == "Climb"


def test_hide_uses_stealth_dc_15():
    action = infer_player_roll("I try to hide behind the barrel. I have not rolled yet.")
    assert action is not None
    assert action["skill"] == "stealth"
    assert action["dc"] == 15


def test_walking_does_not_request_a_roll():
    assert infer_player_roll("I walk across the empty tavern and sit at the bar.") is None


def test_ensure_does_not_duplicate_existing_request():
    existing = [
        {
            "type": "request_player_roll",
            "skill": "athletics",
            "ability": "strength",
            "reason": "Climb",
        }
    ]
    out = ensure_player_roll_action("I try to climb the wall. I have not rolled.", existing)
    assert len(out) == 1


def test_ensure_injects_when_llm_omits_action():
    out = ensure_player_roll_action("I try to climb the wall. I have not rolled.", [])
    assert len(out) == 1
    assert out[0]["skill"] == "athletics"


def test_ensure_replaces_invalid_llm_roll_with_inferred_climb():
    out = ensure_player_roll_action(
        "I try to climb the wall. I have not rolled.",
        [{"type": "request_player_roll", "ability": "Athletics", "dc": 10}],
    )
    assert len(out) == 1
    assert out[0]["skill"] == "athletics"
    assert out[0]["ability"] == "strength"
    assert out[0]["reason"] == "Climb"
    assert out[0].get("dc") is None
