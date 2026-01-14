# Rage Tracking System for Eglath Bearkiller

**Automatic rage management in Obsidian**

---

## Overview

Eglath's Obsidian character sheet now has a **rage tracking system** that:
- ✅ Shows a checkbox for "RAGE ACTIVE"
- ✅ Automatically deducts rage uses when activated
- ✅ Displays both normal and raging weapon variants
- ✅ Reminds about damage resistance while raging

---

## How It Works

### Manual Method (In Obsidian)

1. **Open Eglath's character sheet** in Obsidian
2. **Check the box:** `- [ ] **RAGE ACTIVE**`
3. **Manually decrement rage:** Change `●●●` to `●●○` (3/3 → 2/3)
4. **Use "Raging" weapon variants** for attacks

### Automatic Method (Using MCP Tool)

```python
# Activate rage
toggle_rage("Eglath Bearkiller", activate=True)

# Returns:
{
  "success": true,
  "message": "Eglath Bearkiller is now RAGING!",
  "rage_uses_remaining": 2,
  "reminder": "Use 'Raging' weapon variants (+2 damage, resistance to physical damage)"
}

# Automatically:
# - Checks the checkbox
# - Deducts 1 rage use (3/3 → 2/3)
# - Updates metadata
```

```python
# End rage
toggle_rage("Eglath Bearkiller", activate=False)

# Returns:
{
  "success": true,
  "message": "Eglath Bearkiller's rage has ended",
  "reminder": "Use normal weapon damage (no +2 rage bonus)"
}

# Automatically:
# - Unchecks the checkbox
# - Updates metadata
```

---

## Eglath's Weapons

### Normal Attacks (Not Raging)
- **Greataxe:** +7 to hit, **1d12+4** slashing
- **Handaxe:** +7 to hit, **1d6+4** slashing

### While Raging (Checkbox Checked)
- **Greataxe (RAGING):** +7 to hit, **1d12+6** slashing (**+2 rage damage**)
- **Handaxe (RAGING):** +7 to hit, **1d6+6** slashing (**+2 rage damage**)

**Damage Breakdown:**
- Base damage: 1d12 (Greataxe) or 1d6 (Handaxe)
- **+4** (STR modifier)
- **+2** (Rage damage bonus at level 5)
- **Total: +6** when raging

---

## Rage Benefits (Level 5 Barbarian)

### While Raging:
1. **+2 Damage** on melee attacks using STR
2. **Resistance to Physical Damage** (take half damage from bludgeoning, piercing, slashing)
3. **Advantage on STR checks and saves**

### Rage Count:
- **3 uses per long rest** (Level 5)
- **Duration:** 1 minute (10 rounds) or until:
  - You fall unconscious
  - Your turn ends and you haven't attacked or taken damage since your last turn
  - You end it early (bonus action)

---

## Usage Examples

### Example 1: Starting Combat

```python
# Eglath enters combat, activates rage
toggle_rage("Eglath Bearkiller", activate=True)

# ✓ Rage checkbox: - [x] **RAGE ACTIVE**
# ✓ Rage uses: ●●○ (2/3 remaining)
# ✓ Use raging weapons: Greataxe +7 to hit, 1d12+6 damage
```

### Example 2: Out of Rages

```python
# Eglath tries to rage but has 0 uses left
toggle_rage("Eglath Bearkiller", activate=True)

# Returns:
{
  "error": "No rage uses remaining! Take a long rest to recover."
}

# ✗ Rage not activated
# ✗ Rage count: ○○○ (0/3)
```

### Example 3: After Combat

```python
# Combat ends, Eglath's rage expires
toggle_rage("Eglath Bearkiller", activate=False)

# ✓ Rage checkbox: - [ ] **RAGE ACTIVE**
# ✓ Back to normal damage
```

---

## Integration with Combat Engine (Phase 2)

**When Combat Engine is integrated:**
1. Combat Engine checks `raging: true/false` in metadata
2. Automatically applies correct weapon damage
3. Applies damage resistance when calculating incoming damage
4. Can auto-toggle rage at start of combat (optional)

---

## Character Sheet Structure

### Frontmatter
```yaml
---
raging: false
hp_current: 65
hp_max: 65
---
```

### Markdown Content
```markdown
## Class Resources

**Rage:** ●●● (3/3)

### Currently Raging
- [ ] **RAGE ACTIVE** (Deals +2 damage, resistance to physical damage)

## Weapons & Attacks

### Normal Attacks
**Greataxe:** +7 to hit, 1d12+4 slashing

### While Raging (Use when checkbox above is checked)
**Greataxe (RAGING):** +7 to hit, **1d12+6** slashing (**+2 rage damage**)
```

---

## Manual Rage Management

If you prefer to manage rage manually in Obsidian:

1. **Check the box** when Eglath rages
2. **Use "Raging" weapon stats** for damage
3. **Remember to:**
   - Decrement rage count manually
   - Apply physical damage resistance
   - Uncheck box when rage ends (1 minute or early)

---

## Notes

- **Rage damage increases** at higher levels:
  - Level 1-8: +2 damage
  - Level 9-15: +3 damage
  - Level 16-20: +4 damage

- **Rage uses increase** at higher levels:
  - Level 1-2: 2 uses
  - Level 3-5: 3 uses
  - Level 6-11: 4 uses
  - Level 12-16: 5 uses
  - Level 17-19: 6 uses
  - Level 20: Unlimited (Primal Champion)

- **Reckless Attack:** Eglath can also use Reckless Attack (advantage on melee attacks, but enemies have advantage against him)

---

**Eglath's rage is now fully tracked in Obsidian!** 💢⚔️




