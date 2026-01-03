# Testing Chapter 1: Goblin Ambush

## Quick Start Guide

### Step 1: Update Session Preload (Chapter 1)

The `session_preload.json` needs to reference Chapter 1:

```json
{
  "pack_type": "session_preload",
  "pack_version": "1.0",
  "source": "Mines of Phandelver and Below",
  "current_chapter": 1,
  "current_scene_id": "goblin_ambush",
  ...
}
```

### Step 2: Create Initial Encounter Pack

The `encounter_pack.json` should contain the starting scene - the Goblin Ambush:

```json
{
  "pack_type": "encounter_pack",
  "pack_version": "1.0",
  "source": "Mines of Phandelver and Below",
  "chapter": 1,
  "scene_id": "goblin_ambush",
  "keyword": "ambush",
  "cards": [
    {
      "id": "encounter_goblin_ambush_001",
      "type": "encounter",
      "title": "Goblin Ambush on Triboar Trail",
      "boxed_text": "You've been on the Triboar Trail for about half a day and are nearing a side road leading south toward Phandalin. As you come around a bend, you stumble upon the scene of a recent battle. The woods press close to the trail here, with a steep embankment and dense thickets on either side. Two horses wander the road, sniffing at ransacked personal effects.",
      "mechanics": "",
      "references": "Chapter 1, Goblin Ambush"
    }
  ]
}
```

### Step 3: Bootstrap Session

```powershell
cd C:\DnD\DnD_Cursor
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_agents.ps1 -SessionId "test-ch1-001"
```

This creates: `C:\DnD\.coord-test-ch1-001\`

### Step 4: Run First Turn

In Cursor Chat, run:

```
/dnd_turn_parallel test-ch1-001
```

**TURN_TEXT example:**
"The party approaches the ambush site cautiously. The rogue scouts ahead while the fighter examines the horses and the scene of battle."

### Step 5: Merge Outputs

After all 4 agents complete, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\merge_outputs.ps1 -SessionId test-ch1-001
```

Or in Cursor Chat:
```
/dnd_turn_merge test-ch1-001
```

## Expected First Scene

**Starting Location:** Triboar Trail, ambush site
- Two horses (Gundren's and Sildar's)
- Ransacked personal effects
- Empty leather map case
- **Four goblins hiding** (two on each side of road)

**Initial Actions:**
- Characters approach the scene
- Goblins attack when someone approaches the horses
- Combat or capture options
- Trail leads to Cragmaw Hideout (H1-H8)

## Chapter 1 Structure

- **Starting Scene:** Goblin Ambush (road encounter)
- **Main Location:** Cragmaw Hideout (H1-H8)
- **Key NPCs:** Gundren Rockseeker, Sildar Hallwinter, Klarg (bugbear)
- **Level:** Characters start at 1st level
- **Advancement:** Level up after clearing Cragmaw Hideout

## Testing Checklist

- [ ] session_preload.json has `current_chapter: 1`
- [ ] encounter_pack.json has Goblin Ambush scene
- [ ] chapter_pack_1.json exists and is valid
- [ ] Bootstrap script creates coordination directory
- [ ] /dnd_turn_parallel runs without errors
- [ ] All 4 agent outputs are created
- [ ] Merge produces valid 3-block output (NARRATION/ASK/PATCH)



