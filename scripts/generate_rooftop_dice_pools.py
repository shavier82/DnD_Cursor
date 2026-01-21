#!/usr/bin/env python3
"""Generate dice pools for rooftop goblin encounter"""

import random
import json

# Generate dice pools for goblins
pools = {}

enemies = ['Goblin Psi Commander', 'Goblin Psi Brawler 1', 'Goblin Psi Brawler 2']

for enemy in enemies:
    pools[enemy] = {
        'hit_pool': [random.randint(1, 20) + 4 for _ in range(25)],
        'damage_pool': [random.randint(1, 6) + 2 for _ in range(25)],
        'hit_index': 0,
        'damage_index': 0
    }

print(json.dumps(pools, indent=2))































