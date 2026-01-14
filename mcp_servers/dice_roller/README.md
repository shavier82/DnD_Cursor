# True Random Dice Roller MCP Server

Provides cryptographically secure dice rolling with audit trails for D&D campaigns.

## Features

- **Cryptographically Secure**: Uses Python's `secrets` module for true randomness
- **Audit Trail**: All rolls logged to `dice_rolls_audit.jsonl` with timestamps
- **D&D 5e Support**: Attack rolls, saving throws, initiative, and generic dice
- **Advantage/Disadvantage**: Full support for D&D 5e mechanics
- **Roll History**: Query past rolls for verification

## Installation

1. Install dependencies:
```powershell
cd C:\DnD\DnD_Cursor\mcp_servers\dice_roller
pip install -r requirements.txt
```

2. Configure in Cursor MCP settings (see Configuration below)

## Tools

### `roll_dice`
Roll any dice expression with cryptographically secure randomness.

**Parameters:**
- `dice_expression` (required): Format `NdX+modifier` (e.g., `2d6+3`, `1d20`, `4d8-2`)
- `reason` (required): Reason for the roll (for audit trail)
- `character` (optional): Character making the roll

**Examples:**
```json
{
  "dice_expression": "2d6+3",
  "reason": "Damage for greatsword attack",
  "character": "Vandross"
}
```

### `roll_attack`
Roll an attack (1d20 + modifier) with advantage, disadvantage, or normal.

**Parameters:**
- `modifier` (required): Attack modifier to add
- `character` (required): Character making the attack
- `advantage` (optional): Roll with advantage (2d20, take higher)
- `disadvantage` (optional): Roll with disadvantage (2d20, take lower)
- `target_ac` (optional): Target AC for hit/miss determination
- `weapon` (optional): Weapon being used

**Example:**
```json
{
  "modifier": 7,
  "character": "Brevin",
  "weapon": "Dragon Claw Dagger",
  "advantage": true,
  "target_ac": 15
}
```

### `roll_initiative`
Roll initiative for one or more combatants.

**Parameters:**
- `combatants` (required): Array of combatants with `name`, `modifier`, and optional `advantage`

**Example:**
```json
{
  "combatants": [
    {"name": "Brevin", "modifier": 5},
    {"name": "Goblin 1", "modifier": 2},
    {"name": "Goblin 2", "modifier": 2}
  ]
}
```

### `roll_saving_throw`
Roll a saving throw (1d20 + modifier) against a DC.

**Parameters:**
- `modifier` (required): Saving throw modifier
- `dc` (required): Difficulty Class
- `ability` (required): Ability being saved (e.g., "Dexterity")
- `character` (required): Character making the save
- `advantage` (optional): Roll with advantage
- `disadvantage` (optional): Roll with disadvantage

**Example:**
```json
{
  "modifier": 3,
  "dc": 15,
  "ability": "Dexterity",
  "character": "Zephyr",
  "advantage": false
}
```

### `get_roll_history`
Retrieve recent roll history from audit log.

**Parameters:**
- `limit` (optional): Number of recent rolls to retrieve (default: 10)
- `character` (optional): Filter by character name

**Example:**
```json
{
  "limit": 20,
  "character": "Brevin"
}
```

## Audit Trail

All rolls are logged to `dice_rolls_audit.jsonl` in JSONL format (one JSON object per line).

**Example log entry:**
```json
{
  "type": "attack_roll",
  "character": "Brevin",
  "weapon": "Dragon Claw Dagger",
  "roll": 18,
  "modifier": 7,
  "total": 25,
  "advantage": true,
  "disadvantage": false,
  "target_ac": 15,
  "result": "HIT",
  "timestamp": "2026-01-13T12:34:56.789Z"
}
```

## Configuration

Add to Cursor's MCP settings (`settings.json`):

```json
{
  "mcp": {
    "servers": {
      "dice-roller": {
        "command": "python",
        "args": ["C:\\DnD\\DnD_Cursor\\mcp_servers\\dice_roller\\dice_roller_server.py"],
        "env": {}
      }
    }
  }
}
```

Or use the configuration helper (see `configure_mcp.ps1`).

## Usage in AI Assistant

The AI assistant can call these tools during gameplay:

```
AI: Rolling attack for Brevin with Dragon Claw Dagger...
[Calls roll_attack tool]
Result: ⚔️ Attack Roll: Brevin with Dragon Claw Dagger
Roll: 18, 12 (advantage, taking 18)
Modifier: +7
Total: 25
✅ HIT (AC 15)
```

## Benefits Over Dice Pools

**Dice Pools (Current):**
- ✅ Faster (pre-rolled)
- ❌ Predictable (stored in state)
- ❌ No audit trail
- ❌ No true randomness

**True Random Roller (This MCP):**
- ✅ Cryptographically secure randomness
- ✅ Full audit trail with timestamps
- ✅ Unpredictable (no pattern)
- ✅ Verifiable (check logs)
- ❌ Slightly slower (real-time rolls)

## When to Use

**Use True Random Roller when:**
- Player attacks/saves/checks (fairness matters)
- Important story moments
- You want unpredictability
- You need roll verification

**Use Dice Pools when:**
- Enemy attacks (speed optimization)
- Many quick rolls needed
- Combat with 5+ enemies
- Speed > true randomness

## Testing

Test the server:

```powershell
cd C:\DnD\DnD_Cursor\mcp_servers\dice_roller
python dice_roller_server.py
```

Then send test requests via MCP protocol.

## Troubleshooting

**MCP package not found:**
```powershell
pip install mcp
```

**Server won't start:**
- Check Python path in Cursor settings
- Verify `dice_roller_server.py` is executable
- Check logs in Cursor output panel

**Rolls not logging:**
- Check file permissions for `dice_rolls_audit.jsonl`
- Verify write access to `mcp_servers/dice_roller/` directory

















