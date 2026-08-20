"""DM agent: prompt → Ollama → validate actions → mutate state → narrate."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.ai.context_builder import ContextBuilder
from app.ai.llm import OllamaClient, OllamaError
from app.ai.prompts import DM_SYSTEM_PROMPT, build_user_prompt
from app.game.actions import DMAgentResponse, validate_actions
from app.game.roll_gate import ensure_player_roll_action, format_roll_call
from app.game.state_manager import StateManager
from app.models import ChatMessage

logger = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _stamp_roll_call(narration: str, pending_rolls: list[dict[str, Any]]) -> str:
    calls = "\n".join(format_roll_call(r) for r in pending_rolls)
    text = (narration or "").strip()
    if "ROLL:" in text:
        return text
    if not text:
        return calls
    return f"{text}\n\n{calls}"


class DMAgent:
    def __init__(
        self,
        db: Session,
        campaign_id: str,
        *,
        llm: OllamaClient | None = None,
        debug: bool = False,
    ) -> None:
        self.db = db
        self.campaign_id = campaign_id
        self.llm = llm or OllamaClient()
        self.debug = debug
        self.context_builder = ContextBuilder(db, campaign_id)
        self.state_manager = StateManager(db, campaign_id)

    def handle_player_message(self, message: str) -> dict[str, Any]:
        # Persist player message first
        user_msg = ChatMessage(
            campaign_id=self.campaign_id,
            role="user",
            content=message,
            meta_json={},
        )
        self.db.add(user_msg)
        self.db.flush()

        ctx = self.context_builder.snapshot(message)
        user_prompt = build_user_prompt(
            game_state=ctx["game_state"],
            retrieved_rules=ctx["retrieved_rules"],
            campaign_memories=ctx["campaign_memories"],
            dm_secrets=ctx["dm_secrets"],
            recent_conversation=ctx["recent_conversation"],
            player_action=message,
        )

        try:
            raw_text = self.llm.generate_text(
                [
                    {"role": "system", "content": DM_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                format_json=True,
                temperature=0.7,
            )
        except OllamaError as exc:
            logger.error("DM agent Ollama failure: %s", exc)
            raise

        parsed = self._parse_dm_json(raw_text)
        gated_actions = ensure_player_roll_action(message, list(parsed.actions or []))
        accepted, rejected = validate_actions(gated_actions)
        if rejected:
            logger.warning("Rejected %s AI action(s)", len(rejected))

        execution = self.state_manager.apply_many(list(accepted))
        pending_rolls = [
            item["result"]
            for item in execution
            if item.get("ok") and item.get("type") == "request_player_roll"
        ]
        if pending_rolls:
            parsed.requires_player_input = True
            parsed.narration = _stamp_roll_call(parsed.narration, pending_rolls)
        self.db.commit()

        meta: dict[str, Any] = {
            "actions_requested": parsed.actions,
            "actions_accepted": [a.model_dump() for a in accepted],
            "actions_rejected": rejected,
            "actions_executed": execution,
            "pending_rolls": pending_rolls,
            "requires_player_input": parsed.requires_player_input,
        }
        if self.debug:
            from app.rag.retriever import debug_hits

            meta["debug"] = {
                "raw_model_output": raw_text[:4000],
                "roll_gate_injected": bool(pending_rolls),
                "rag_chunks": debug_hits(ctx.get("rag_hits") or []),
                "context_preview": {
                    "game_state": ctx["game_state"],
                    "retrieved_rules": ctx["retrieved_rules"],
                    "campaign_memories": ctx["campaign_memories"],
                    "dm_secrets_present": bool(ctx["dm_secrets"]),
                },
            }

        assistant_msg = ChatMessage(
            campaign_id=self.campaign_id,
            role="assistant",
            content=parsed.narration,
            meta_json=meta,
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "narration": parsed.narration,
            "actions_executed": execution,
            "actions_rejected": rejected,
            "pending_rolls": pending_rolls,
            "requires_player_input": parsed.requires_player_input,
            "message_id": assistant_msg.id,
            "debug": meta.get("debug") if self.debug else None,
        }

    def _parse_dm_json(self, raw_text: str) -> DMAgentResponse:
        text = raw_text.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = _JSON_FENCE_RE.search(text)
            if match:
                data = json.loads(match.group(1))
            else:
                # Fallback: treat entire reply as narration (no actions)
                logger.warning("DM JSON parse failed; falling back to plain narration")
                return DMAgentResponse(narration=text or "...", actions=[], requires_player_input=True)

        if isinstance(data, dict) and "narration" not in data and "message" in data:
            # Some models wrap oddly
            data = {"narration": str(data.get("message")), "actions": data.get("actions", [])}

        try:
            return DMAgentResponse.model_validate(data)
        except Exception:
            narration = str(data.get("narration") or data.get("content") or text)
            return DMAgentResponse(narration=narration, actions=[], requires_player_input=True)
