# Response Guard Integration Guide

## Overview

`scripts/response_guard.py` validates DM responses to prevent combat turn authority violations (e.g., asking "What does the enemy do?" on enemy turns).

## Usage

### Manual Validation

```bash
# Validate enemy turn response
echo "Ontharyx attacks. What does he do?" | python scripts/response_guard.py --is-pc-turn false
# Exits 1 (blocked)

# Validate PC turn response
echo "What do you do?" | python scripts/response_guard.py --is-pc-turn true
# Exits 0 (valid)
```

### Integration Points

**Option 1: Pre-send validation (if using custom CLI loop)**

If you have a custom script that generates responses:

```python
# pseudocode
response = generate_dm_response(...)
is_pc_turn = check_turn_type(...)

# Validate before sending
result = subprocess.run(
    ["python", "scripts/response_guard.py", "--is-pc-turn", str(is_pc_turn).lower()],
    input=response,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    # Blocked - regenerate or hard fail
    print("BLOCKED: Response failed validation")
    # Option: regenerate with specific instruction
    response = regenerate_with_instruction("Enemy turn delegation detected. Resolve turn automatically.")
```

**Option 2: Post-send detection (monitoring)**

Run guard in background to detect violations:

```bash
# In a monitoring script
cat response.txt | python scripts/response_guard.py --is-pc-turn false --verbose
```

**Option 3: Cursor Agent Mode (limited integration)**

Cursor's agent mode doesn't expose a response pre-send hook, but you can:

1. **Manual validation during development** - Run guard on problematic responses to refine prompts
2. **Post-session review** - Check logs for violations
3. **Preflight-style integration** - If you create a custom DM workflow loop, add guard as a step

## Current Limitations

Cursor's agent mode generates responses internally - we can't intercept before the response is shown. The guard script is useful for:

- **Testing** - Validate specific response patterns
- **Custom workflows** - If you build a DM automation pipeline
- **Training data** - Identify violations to improve prompts

## Future Integration Ideas

If Cursor adds response hooks or you build a custom loop:

```python
# Hypothetical integration
def dm_response_loop():
    while True:
        turn_info = get_combat_status()
        is_pc_turn = turn_info['current_turn']['creature_id'] in PC_ROSTER
        
        response = generate_response(turn_info)
        
        # Guard validates before sending
        if not validate_with_guard(response, is_pc_turn):
            response = regenerate_safe_response(turn_info)
        
        send_response(response)
```

## Testing

```bash
# Test enemy turn violation
echo "What does Ontharyx do?" | python scripts/response_guard.py --is-pc-turn false
# Expected: exit code 1, "BLOCKED: monster turn delegation detected"

# Test valid enemy turn
echo "Ontharyx attacks with unarmed strike. Any reactions?" | python scripts/response_guard.py --is-pc-turn false
# Expected: exit code 0

# Test PC turn
echo "What do you do?" | python scripts/response_guard.py --is-pc-turn true
# Expected: exit code 0
```
