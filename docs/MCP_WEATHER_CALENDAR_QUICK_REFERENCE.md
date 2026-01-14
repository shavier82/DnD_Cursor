# Weather & Calendar MCP - Quick Reference

## Essential Tools

### Session Start
```
get_current_date_time()     # "15 Mirtul, 1492 DR, 3:00 PM"
get_current_weather()        # "Light Rain, Cool, 90% travel speed"
get_moon_phase()             # "Waxing Gibbous, 50% lycanthropy risk"
```

### Time Advancement
```
advance_time(hours=4)        # Advance 4 hours
advance_time(days=2)         # Advance 2 days
long_rest()                  # Advance 8 hours + weather update
```

### Travel
```
calculate_travel_time(
  distance_miles=30,
  terrain="trail",           # road/trail/wilderness/difficult
  pace="normal"              # slow/normal/fast
)
# Output: "1 day, 6 hours"
```

### Manual Date Set
```
set_date_time(
  day=1,
  month=6,                   # Kythorn (Summer)
  year=1492,
  hour=8,
  minute=0
)
```

---

## Weather Effects Reference

| Condition | Travel | Visibility | Combat Effects |
|-----------|--------|------------|----------------|
| Clear | 100% | Excellent | None |
| Light Rain | 90% | Fair | Disadvantage Perception (sight) |
| Heavy Rain | 75% | Poor | Disadvantage Perception, Difficult terrain |
| Thunderstorm | 50% | Poor | Lightning hazard |
| Blizzard | 25% | Very Poor | DC 10 CON save or exhaustion |
| Fog | 75% | Poor | Lightly obscured |

---

## Moon Phases (for Lycanthropy)

- **New Moon:** 0% risk, Very Dark (-2 Perception)
- **Full Moon:** 100% risk, Bright (+2 Perception)
- Other phases: 50% risk, Moderate visibility

---

## Harptos Calendar Quick Ref

**Months:** Hammer (1), Alturiak (2), Ches (3), Tarsakh (4), Mirtul (5), Kythorn (6), Flamerule (7), Eleasis (8), Eleint (9), Marpenoth (10), Uktar (11), Nightal (12)

**Seasons:** Winter (1-2, 12), Spring (3-5), Summer (6-8), Autumn (9-11)

**Festivals:** Midwinter, Greengrass, Midsummer, Highharvestide, Feast of the Moon

---

## Common Scenarios

**Traveling to next town:**
```
1. calculate_travel_time(distance_miles=20, terrain="road")
2. advance_time(days=X, hours=Y)
3. Narrate arrival
```

**Long rest:**
```
1. long_rest()
2. Update spell slots/HP in character sheets
3. Narrate morning weather
```

**Werewolf encounter:**
```
1. get_moon_phase()
2. If Full Moon → lycanthropy transformation
3. Apply night visibility effects
```

---

## Integration Commands

**With Obsidian:**
- After `advance_time()` → `sync_campaign_events()` to update timeline

**With Session Recorder:**
- `log_event(event_type="narration", content=f"Weather: {weather}")`

**With Combat Engine:**
- Check weather before combat → apply terrain/visibility effects



