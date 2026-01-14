# Currency and Inventory Update Rules

## CRITICAL RULE: Always ADD, Never Overwrite

**This is a MANDATORY rule for all currency and inventory operations.**

## Currency Updates

### Default Behavior (OVERWRITES)
By default, `update_character_currency()` **OVERWRITES** the current currency value. This is dangerous and should only be used when you explicitly want to set a specific total amount.

### Safe Method: ADD Currency
**ALWAYS use the `--add` flag or `add_character_currency()` function when adding currency.**

**Workflow: READ → ADD → UPDATE**
1. **READ** current currency from CSV_Currency
2. **ADD** new amount to current value
3. **UPDATE** CSV_Currency with new total

### Command Line Usage

**Adding currency (SAFE - recommended):**
```bash
python update_sheets_data.py currency "Character Name" --gp 100 --add
```

**Setting currency (OVERWRITES - use with caution):**
```bash
python update_sheets_data.py currency "Character Name" --gp 100
```

### Python Function Usage

**Adding currency (SAFE - recommended):**
```python
from update_sheets_data import add_character_currency

# This function READS current, ADDS new amount, then UPDATES
add_character_currency(service, spreadsheet_id, character_id, {'gp': 100})
```

**Setting currency (OVERWRITES - use with caution):**
```python
from update_sheets_data import update_character_currency

# This OVERWRITES the current value
update_character_currency(service, spreadsheet_id, character_id, {'gp': 100}, add=False)
```

## Inventory Updates

### Adding Items (SAFE)
The `add_inventory_item()` and `add_inventory_items_batch()` functions **APPEND** new rows to CSV_Inventory. This is safe and correct.

**Workflow: APPEND**
- New items are added as new rows
- Existing items are not modified
- No overwriting occurs

### Removing Items
When removing items from inventory:
- Use the Google Sheets API `deleteDimension` to remove entire rows
- Never overwrite item quantities to 0 (this leaves empty rows)

## Examples

### ✅ CORRECT: Adding Currency
```python
# Read current, add new amount, update
add_character_currency(service, ss_id, char_id, {'gp': 50})
```

### ❌ WRONG: Overwriting Currency
```python
# This OVERWRITES current value - DANGEROUS
update_character_currency(service, ss_id, char_id, {'gp': 50}, add=False)
```

### ✅ CORRECT: Adding Inventory Items
```python
# Appends new rows - SAFE
add_inventory_item(service, ss_id, char_id, "Potion of Healing", quantity=1)
```

## Why This Rule Exists

**Problem:** Overwriting currency values causes data loss. If a character has 100 gp and you "add" 50 gp by overwriting with 50, you lose the original 100 gp.

**Solution:** Always READ current values first, then ADD the new amount, then UPDATE with the total.

## Enforcement

- **All scripts MUST use `add_character_currency()` or `--add` flag when adding currency**
- **All scripts MUST read current currency before updating**
- **All inventory additions MUST use append operations (already implemented correctly)**
- **Never overwrite currency values unless explicitly setting a total amount**

## Testing

Before deploying currency updates:
1. Check current currency value
2. Add test amount
3. Verify new value = old value + test amount
4. If values don't match, the update is overwriting instead of adding

## Related Files

- `scripts/update_sheets_data.py` - Contains currency update functions
- `.cursorrules` - Contains data source of truth rules
- `docs/SHEETS_UPDATE_GUIDE.md` - General sheets update documentation

















