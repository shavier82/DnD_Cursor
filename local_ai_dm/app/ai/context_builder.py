"""Build prompt context from canonical SQLite state."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.models import Campaign, CampaignMemory, ChatMessage, Encounter, MemoryKind


class ContextBuilder:
    def __init__(self, db: Session, campaign_id: str) -> None:
        self.db = db
        self.campaign_id = campaign_id

    def load_campaign(self) -> Campaign:
        campaign = (
            self.db.query(Campaign)
            .options(
                joinedload(Campaign.characters),
                joinedload(Campaign.quests),
                joinedload(Campaign.encounters).joinedload(Encounter.combatants),
            )
            .filter(Campaign.id == self.campaign_id)
            .first()
        )
        if campaign is None:
            raise ValueError(f"Campaign not found: {self.campaign_id}")
        return campaign

    def game_state_text(self, campaign: Campaign | None = None) -> str:
        campaign = campaign or self.load_campaign()
        lines: list[str] = [
            f"Campaign: {campaign.name} ({campaign.system})",
            f"Location: {campaign.current_location or 'Unknown'}",
            "Party:",
        ]
        for c in campaign.characters:
            cond = ", ".join(c.conditions) if c.conditions else "none"
            lines.append(
                f"- {c.name} [id={c.id}] HP {c.current_hp}/{c.max_hp} AC {c.armor_class} "
                f"conditions=[{cond}] class={c.character_class or '?'} L{c.level}"
            )
        active_quests = [q for q in campaign.quests if q.status == "active"]
        if active_quests:
            lines.append("Active quests:")
            for q in active_quests:
                lines.append(f"- {q.title}: {q.description[:200]}")
        else:
            lines.append("Active quests: none")

        active = next((e for e in campaign.encounters if e.status == "active"), None)
        if active:
            lines.append(f"Combat: ACTIVE ({active.name}) round {active.round_number}")
            ordered = sorted(active.combatants, key=lambda x: x.initiative, reverse=True)
            for cb in ordered:
                lines.append(
                    f"  - {cb.name} init={cb.initiative} HP {cb.current_hp}/{cb.max_hp}"
                )
        else:
            lines.append("Combat: none")
        return "\n".join(lines)

    def memories_text(self, *, kind: MemoryKind, limit: int = 12) -> str:
        rows = (
            self.db.query(CampaignMemory)
            .filter(
                CampaignMemory.campaign_id == self.campaign_id,
                CampaignMemory.kind == kind,
            )
            .order_by(CampaignMemory.importance.desc(), CampaignMemory.created_at.desc())
            .limit(limit)
            .all()
        )
        if not rows:
            return ""
        return "\n".join(f"- ({m.importance}) {m.text}" for m in rows)

    def recent_conversation_text(self, limit: int = 12) -> str:
        rows = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.campaign_id == self.campaign_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        rows = list(reversed(rows))
        if not rows:
            return ""
        return "\n".join(f"{m.role.upper()}: {m.content}" for m in rows)

    def snapshot(self, player_message: str = "") -> dict[str, Any]:
        campaign = self.load_campaign()
        rag_hits: list[dict[str, Any]] = []
        retrieved_rules = ""
        if player_message.strip():
            from app.rag.retriever import format_rules_for_prompt, retrieve_rule_chunks

            rag_hits = retrieve_rule_chunks(player_message)
            retrieved_rules = format_rules_for_prompt(rag_hits)
        return {
            "game_state": self.game_state_text(campaign),
            "campaign_memories": self.memories_text(kind=MemoryKind.CAMPAIGN),
            "dm_secrets": self.memories_text(kind=MemoryKind.DM_SECRET),
            "recent_conversation": self.recent_conversation_text(),
            "retrieved_rules": retrieved_rules,
            "rag_hits": rag_hits,
        }
