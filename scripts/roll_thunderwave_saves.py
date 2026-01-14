#!/usr/bin/env python3
"""Roll Constitution saves for Thunderwave"""

import random

dc = 13
commander_roll = random.randint(1, 20)
commander_total = commander_roll + 1  # CON +1
brawler1_roll = random.randint(1, 20)
brawler1_total = brawler1_roll + 1  # CON +1
brawler2_roll = random.randint(1, 20)
brawler2_total = brawler2_roll + 1  # CON +1

print(f"Commander CON save: {commander_roll} + 1 = {commander_total} (DC {dc}) = {'FAIL' if commander_total < dc else 'SUCCESS'}")
print(f"Brawler 1 CON save: {brawler1_roll} + 1 = {brawler1_total} (DC {dc}) = {'FAIL' if brawler1_total < dc else 'SUCCESS'}")
print(f"Brawler 2 CON save: {brawler2_roll} + 1 = {brawler2_total} (DC {dc}) = {'FAIL' if brawler2_total < dc else 'SUCCESS'}")

















