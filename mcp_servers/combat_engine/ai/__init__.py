"""AI logic for enemy combatants"""

from .target_selection import select_target
from .action_priority import decide_action
from .tactical_positioning import decide_position

__all__ = ["select_target", "decide_action", "decide_position"]




