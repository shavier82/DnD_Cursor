"""
Discord Bot for D&D Campaign - Captures Dice Rolls from D&D Beyond
"""
import discord
from discord.ext import commands
import re
import json
import shutil
import time
from pathlib import Path
from datetime import datetime

def safe_write_json_log(log_file: Path, logs: list):
    """Safely write JSON log file with retry logic for Windows file locking"""
    temp_file = log_file.with_suffix('.tmp')
    
    # Try to remove temp file if it exists (might be locked)
    if temp_file.exists():
        try:
            temp_file.unlink()
        except (IOError, OSError):
            pass  # Ignore if can't delete
    
    try:
        # Write to temp file
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        # Atomic replace - try multiple times if needed (Windows file locking)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if log_file.exists():
                    log_file.unlink()  # Remove old file first on Windows
                shutil.move(str(temp_file), str(log_file))
                return True
            except (IOError, OSError) as e:
                if attempt < max_retries - 1:
                    time.sleep(0.2)  # Wait a bit and retry
                else:
                    raise
    except (IOError, OSError) as e:
        print(f"[ERROR] Failed to write dice log: {e}")
        # Try direct write as fallback (less safe but might work)
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            print("[INFO] Used fallback direct write method")
            return True
        except (IOError, OSError) as e2:
            print(f"[ERROR] Fallback write also failed: {e2}")
            print(f"[WARNING] Dice roll detected but could not be logged to file!")
            return False
    return True

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Dice roll pattern matching - improved to capture modifiers better
DICE_PATTERN = re.compile(r'(\d+)d(\d+)([+-]\d+)?', re.IGNORECASE)
# Pattern for rolls with results: "1d20+5 = 15" or "1d20+5: 15" or "1d20+5 (15)"
DND_BEYOND_PATTERN = re.compile(r'(\d+)d(\d+)\s*([+-]\d+)?\s*[=:]\s*(\d+)', re.IGNORECASE)
# Pattern to find results near dice notation
RESULT_PATTERN = re.compile(r'[=:]\s*(\d+)|result[:\s]+(\d+)|total[:\s]+(\d+)|\((\d+)\)', re.IGNORECASE)
# Pattern to find modifier near dice: "1d20 +5" or "1d20+5" or "1d20 + 5"
MODIFIER_PATTERN = re.compile(r'(\d+)d(\d+)\s*([+-])\s*(\d+)', re.IGNORECASE)
# Avrae/D&D Beyond format: 
# - "1d20 (12) + 5" with "Total: 17" 
# - "1d4 (1)" with "Total: 1"
# - "4d6 (1, 2, 3, 4)" or "4d6 (10)" with "Total: 10"
# - "4d6 (5, 2, 3)" - might be truncated or showing sum
# Pattern matches: num_dice, die_size, roll_value(s), modifier
# Use non-greedy match to capture full parentheses content
AVRAE_PATTERN = re.compile(r'(\d+)d(\d+)\s*\(([^)]+?)\)(?:\s*([+-]\s*\d+))?', re.IGNORECASE)
# Pattern to extract character name and action: "Character: Action: Type:" or "Action: Type:" or "Result:"
# Examples: "Torgga Brawnanvil: Initiative: Roll:" or "Guiding Bolt: To Hit:" or "Result:"
CHARACTER_ACTION_PATTERN = re.compile(r'([^:\n]+?):\s*([^:\n]+?):\s*(To Hit|Roll|Check|Damage|Save|Result)', re.IGNORECASE)
SIMPLE_ACTION_PATTERN = re.compile(r'([^:\n]+?):\s*(To Hit|Roll|Check|Damage|Save|Result)', re.IGNORECASE)
RESULT_ONLY_PATTERN = re.compile(r'Result[:\s]+', re.IGNORECASE)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check for D&D Beyond embeds (they often contain dice roll info)
    if message.embeds:
        for embed in message.embeds:
            # D&D Beyond embeds usually have description or fields with dice info
            # Include message content too, as sometimes info is split
            text_to_check = message.content + "\n" if message.content else ""
            if embed.title:
                text_to_check += embed.title + "\n"
            if embed.description:
                text_to_check += embed.description + "\n"
            if embed.fields:
                for field in embed.fields:
                    text_to_check += field.name + ": " + field.value + "\n"
            if embed.footer and embed.footer.text:
                text_to_check += embed.footer.text + "\n"
            
            # Check for Avrae format first: "1d20 (12) + 5" with "Total: 17"
            avrae_matches = AVRAE_PATTERN.findall(text_to_check)
            if avrae_matches:
                await process_avrae_roll(message, avrae_matches, text_to_check, source="D&D Beyond Embed")
                return
            
            # Look for dice patterns with results: "1d20+5 = 15"
            dnd_beyond_matches = DND_BEYOND_PATTERN.findall(text_to_check)
            if dnd_beyond_matches:
                # Extract full match with result
                await process_dice_roll_with_result(message, dnd_beyond_matches, text_to_check, source="D&D Beyond Embed")
                return
            
            # Fallback: Look for dice patterns without results
            dice_matches = DICE_PATTERN.findall(text_to_check)
            if dice_matches:
                await process_dice_roll(message, dice_matches, text_to_check, source="D&D Beyond Embed")
                return
    
    # Check message content for dice rolls (if no embeds processed)
    # Combine message content with any remaining embed info
    full_text = message.content
    if message.embeds and not any(embed.processed for embed in message.embeds if hasattr(embed, 'processed')):
        # Add embed text to message content for better parsing
        for embed in message.embeds:
            if embed.title:
                full_text += "\n" + embed.title
            if embed.description:
                full_text += "\n" + embed.description
            if embed.fields:
                for field in embed.fields:
                    full_text += "\n" + field.name + ": " + field.value
    
    # Check for Avrae format in message content
    avrae_matches = AVRAE_PATTERN.findall(full_text)
    if avrae_matches:
        await process_avrae_roll(message, avrae_matches, full_text, source="Message")
        return
    
    # Pattern: "1d20+5 = 15" or "rolled 2d6" or "1d20+3"
    dnd_beyond_matches = DND_BEYOND_PATTERN.findall(full_text)
    if dnd_beyond_matches:
        await process_dice_roll_with_result(message, dnd_beyond_matches, full_text, source="Message")
    else:
        dice_matches = DICE_PATTERN.findall(full_text)
        if dice_matches:
            await process_dice_roll(message, dice_matches, full_text, source="Message")
    
    # Process commands
    await bot.process_commands(message)

async def process_dice_roll(message, dice_matches, text="", source="Unknown"):
    """Process and log dice roll information"""
    roll_data = {
        "timestamp": datetime.now().isoformat(),
        "user": str(message.author),
        "user_id": message.author.id,
        "channel": str(message.channel),
        "source": source,
        "rolls": []
    }
    
    for match in dice_matches:
        num_dice, die_size, modifier = match
        num_dice = int(num_dice)
        die_size = int(die_size)
        
        # Better modifier extraction - handle spaces and missing modifiers
        if modifier:
            modifier = modifier.strip()
        else:
            # Try to find modifier in text context
            notation_base = f"{num_dice}d{die_size}"
            # Look for patterns like "1d20 +5" or "1d20+5" in text
            mod_match = MODIFIER_PATTERN.search(text)
            if mod_match and mod_match.group(1) == str(num_dice) and mod_match.group(2) == str(die_size):
                modifier = f"{mod_match.group(3)}{mod_match.group(4)}"
            else:
                modifier = "+0"
        
        # Ensure modifier has sign
        if modifier and not modifier.startswith(('+', '-')):
            modifier = '+' + modifier
        
        # Parse modifier value for calculation
        try:
            mod_value = int(modifier.replace('+', ''))
            if modifier.startswith('-'):
                mod_value = -mod_value
        except ValueError:
            mod_value = 0
        
        # Try to extract individual roll values from text (e.g., "1d6 (4)" or "2d6 (3, 4)")
        roll_values = []
        roll_total = None
        notation = f"{num_dice}d{die_size}"
        idx = text.lower().find(notation.lower())
        if idx >= 0:
            # Look for parentheses with roll values: "1d6 (4)" or "2d6 (3, 4)"
            after_notation = text[idx:]
            paren_match = re.search(r'\(([^)]+)\)', after_notation)
            if paren_match:
                roll_value_str = paren_match.group(1).strip()
                if ',' in roll_value_str:
                    # Multiple dice: "3, 4"
                    parts = roll_value_str.split(',')
                    for part in parts:
                        digits = ''.join(filter(str.isdigit, part.strip()))
                        if digits:
                            roll_values.append(int(digits))
                    roll_total = sum(roll_values) if roll_values else None
                else:
                    # Single value
                    digits = ''.join(filter(str.isdigit, roll_value_str))
                    if digits:
                        single_value = int(digits)
                        if num_dice == 1:
                            roll_values = [single_value]
                            roll_total = single_value
                        else:
                            # Multi-dice showing sum
                            roll_values = [single_value]
                            roll_total = single_value
        
        # Try to extract result from text
        result = None
        if text:
            # Look for result near this dice notation
            if idx >= 0:
                # Look for "= X", ": X", "result: X", "Total: X" after the notation
                after_text = text[idx + len(notation):idx + len(notation) + 50]
                result_patterns = [
                    r'[=:]\s*(\d+)',
                    r'result[:\s]+(\d+)',
                    r'total[:\s]+(\d+)',
                    r'\((\d+)\)'
                ]
                for pattern in result_patterns:
                    result_match = re.search(pattern, after_text, re.IGNORECASE)
                    if result_match:
                        try:
                            result = int(result_match.group(1))
                            break
                        except (ValueError, IndexError):
                            continue
        
        # Calculate result if not found and we have roll_total
        if result is None:
            if roll_total is not None:
                result = roll_total + mod_value
            elif num_dice == 1 and roll_values:
                # Single die, we have the value
                result = roll_values[0] + mod_value
        
        # If we still don't have roll_values but have result, try to infer
        if not roll_values and result is not None:
            # Can't infer individual dice from total, but we can set roll_total
            if roll_total is None:
                # Estimate: result - modifier = roll_total
                roll_total = result - mod_value
                # For single die, we can set the value
                if num_dice == 1:
                    roll_values = [roll_total]
        
        roll_info = {
            "dice": f"{num_dice}d{die_size}",
            "modifier": modifier,
            "full_notation": f"{num_dice}d{die_size}{modifier}",
            "roll_values": roll_values if roll_values else None,
            "roll_total": roll_total,
            "result": result,
            "character": None,
            "action": None
        }
        roll_data["rolls"].append(roll_info)
    
    # Save to log file
    log_file = Path("C:/Users/ksist/scripts/discord_dice_logs.json")
    logs = load_logs_safely(log_file)
    logs.append(roll_data)
    safe_write_json_log(log_file, logs)
    
    # Print to console with full info
    for roll in roll_data['rolls']:
        notation = roll['full_notation']
        if roll.get('roll_values'):
            if len(roll['roll_values']) > 1:
                rolls_str = f"{roll['roll_values']}"
            else:
                rolls_str = str(roll['roll_values'][0])
        else:
            rolls_str = "?"
        result = roll.get('result', '?')
        roll_total = roll.get('roll_total', '?')
        modifier = roll.get('modifier', '?')
        print(f"[DICE ROLL] {message.author}: {notation} (rolls: {rolls_str}, total: {roll_total}{modifier}) = {result}")

async def process_avrae_roll(message, avrae_matches, text="", source="D&D Beyond Embed"):
    """Process Avrae/D&D Beyond rolls in format: '1d20 (12) + 5' with 'Total: 17'"""
    roll_data = {
        "timestamp": datetime.now().isoformat(),
        "user": str(message.author),
        "user_id": message.author.id,
        "channel": str(message.channel),
        "source": source,
        "rolls": []
    }
    
    # Extract character name and action from text
    character_name = None
    action_description = None
    
    # First, try to extract from @mentions in the message
    if message.mentions:
        # Use the first mentioned user's display name or username
        character_name = message.mentions[0].display_name or str(message.mentions[0])
    
    # Look for pattern: "Character: Action: Type:" or "Action: Type:"
    # Examples: "Torgga Brawnanvil: Initiative: Roll:" or "Guiding Bolt: To Hit:"
    char_action_match = CHARACTER_ACTION_PATTERN.search(text)
    if char_action_match:
        potential_char = char_action_match.group(1).strip()
        action = char_action_match.group(2).strip()
        roll_type = char_action_match.group(3).strip()
        
        # Check if first part is a character name (usually has spaces or is longer, or contains common name patterns)
        # Character names often have spaces or are proper nouns
        if len(potential_char.split()) > 1 or (len(potential_char) > 8 and ' ' in potential_char):
            character_name = potential_char
            action_description = f"{action}: {roll_type}"
        else:
            # It's probably part of the action (e.g., "Guiding Bolt")
            action_description = f"{potential_char}: {action}: {roll_type}"
    else:
        # Try simpler pattern: "Action: Type:" (e.g., "Guiding Bolt: To Hit:" or "Warhammer: To Hit:")
        simple_match = SIMPLE_ACTION_PATTERN.search(text)
        if simple_match:
            action = simple_match.group(1).strip()
            roll_type = simple_match.group(2).strip()
            action_description = f"{action}: {roll_type}"
        elif RESULT_ONLY_PATTERN.search(text):
            # Just "Result:" (damage roll)
            action_description = "Damage"
    
    # If we still don't have character name, try to extract from message content
    # Look for patterns like "@username rolled" or check message mentions
    if not character_name:
        # Check for mention pattern in text
        mention_pattern = re.search(r'@(\w+)', text)
        if mention_pattern:
            character_name = mention_pattern.group(1)
        # Also check actual message mentions (Discord @mentions) - already done above, but check again
        elif message.mentions:
            character_name = message.mentions[0].display_name or str(message.mentions[0])
    
    # Extract total from text (look for "Total: X" - can be on same or next line)
    # Try multiple patterns - use MULTILINE and DOTALL to match across lines
    total_result = None
    total_patterns = [
        r'Total[:\s]+(\d+)',  # "Total: 14" or "Total 14"
        r'Total\s*=\s*(\d+)', # "Total = 14"
        r'=\s*(\d+)\s*$',     # "= 14" at end of line
    ]
    
    for pattern in total_patterns:
        total_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if total_match:
            try:
                total_result = int(total_match.group(1))
                break
            except (ValueError, IndexError):
                continue
    
    # If still no total found, try to calculate from roll + modifier
    if total_result is None and avrae_matches:
        for match in avrae_matches:
            num_dice, die_size, roll_value_str, modifier_str = match
            # Try to calculate total
            if ',' in roll_value_str:
                roll_values = [int(x.strip()) for x in roll_value_str.split(',') if x.strip().isdigit()]
                roll_total = sum(roll_values)
            else:
                try:
                    roll_total = int(roll_value_str.strip())
                except ValueError:
                    continue
            
            if modifier_str:
                try:
                    mod_value = int(modifier_str.strip().replace(' ', '').replace('+', ''))
                    if modifier_str.strip().startswith('-'):
                        mod_value = -mod_value
                    total_result = roll_total + mod_value
                    break
                except (ValueError, AttributeError):
                    pass
    
    for match in avrae_matches:
        num_dice, die_size, roll_value_str, modifier_str = match
        
        # Parse roll_value - could be single number "12" or multiple "1, 2, 3, 4"
        roll_values = []
        roll_value_str = roll_value_str.strip()
        expected_dice = int(num_dice)
        
        if ',' in roll_value_str:
            # Multiple dice: "1, 2, 3, 4" or "5, 2, 3" (might be truncated)
            # Split by comma and parse each value
            parts = roll_value_str.split(',')
            for part in parts:
                part = part.strip()
                # Handle numbers that might have spaces or other chars
                # Extract just the digits
                digits = ''.join(filter(str.isdigit, part))
                if digits:
                    roll_values.append(int(digits))
            roll_total = sum(roll_values) if roll_values else None
            
            # Check if we got fewer dice than expected (might be truncated or showing sum)
            if len(roll_values) < expected_dice and roll_total is not None:
                # If we only got one value and it matches the expected total, it might be showing sum
                if len(roll_values) == 1 and roll_values[0] == roll_total:
                    # This is likely showing the sum, not individual dice
                    # We can't recover individual dice, so keep the sum
                    pass
                # Otherwise, warn but keep what we have
                elif len(roll_values) > 0:
                    print(f"[WARNING] Expected {expected_dice} dice but only captured {len(roll_values)} values: {roll_values}")
        else:
            # Single value - could be individual roll (for 1dX) or sum (for multi-dice)
            # Extract just digits in case there are other characters
            digits = ''.join(filter(str.isdigit, roll_value_str))
            if digits:
                single_value = int(digits)
                if expected_dice == 1:
                    # Single die roll
                    roll_values = [single_value]
                    roll_total = single_value
                else:
                    # Multi-dice showing sum (e.g., "4d6 (10)" means sum is 10)
                    roll_values = [single_value]  # Store sum as single value
                    roll_total = single_value
            else:
                roll_total = None
        
        # Clean up modifier (handle None from optional group)
        if modifier_str:
            modifier = modifier_str.strip().replace(' ', '')
            # Ensure modifier has sign
            if modifier and not modifier.startswith(('+', '-')):
                modifier = '+' + modifier
            # Parse modifier value
            try:
                mod_value = int(modifier.replace('+', ''))
                if modifier.startswith('-'):
                    mod_value = -mod_value
            except ValueError:
                mod_value = 0
        else:
            # No modifier shown, but calculate from total if available
            if total_result and roll_total is not None:
                calculated_mod = total_result - roll_total
                mod_value = calculated_mod
                modifier = f"{'+' if calculated_mod >= 0 else ''}{calculated_mod}" if calculated_mod != 0 else "+0"
            else:
                modifier = "+0"
                mod_value = 0
        
        # Calculate final result if not found in text
        final_result = total_result
        if final_result is None and roll_total is not None:
            final_result = roll_total + mod_value
        
        roll_info = {
            "dice": f"{num_dice}d{die_size}",
            "modifier": modifier,
            "full_notation": f"{num_dice}d{die_size}{modifier}",
            "roll_values": roll_values,  # Individual die rolls (list)
            "roll_total": roll_total,  # Sum of individual rolls
            "result": final_result,  # The final total (roll_total + modifier)
            "character": character_name,
            "action": action_description
        }
        roll_data["rolls"].append(roll_info)
    
    # Save to log file
    log_file = Path("C:/Users/ksist/scripts/discord_dice_logs.json")
    logs = load_logs_safely(log_file)
    logs.append(roll_data)
    safe_write_json_log(log_file, logs)
    
    # Print to console with full info
    char_info = f" ({character_name})" if character_name else ""
    action_info = f" - {action_description}" if action_description else ""
    for roll in roll_data['rolls']:
        notation = roll['full_notation']
        if roll.get('roll_values'):
            if len(roll['roll_values']) > 1:
                rolls_str = f"{roll['roll_values']}"
            else:
                rolls_str = str(roll['roll_values'][0])
        else:
            rolls_str = "?"
        result = roll.get('result', '?')
        roll_total = roll.get('roll_total', '?')
        modifier = roll.get('modifier', '?')
        print(f"[DICE ROLL] {message.author}{char_info}{action_info}: {notation} (rolls: {rolls_str}, total: {roll_total}{modifier}) = {result}")

async def process_dice_roll_with_result(message, dnd_matches, text="", source="D&D Beyond Embed"):
    """Process D&D Beyond rolls that include results (e.g., '1d20+5 = 15')"""
    roll_data = {
        "timestamp": datetime.now().isoformat(),
        "user": str(message.author),
        "user_id": message.author.id,
        "channel": str(message.channel),
        "source": source,
        "rolls": []
    }
    
    for match in dnd_matches:
        num_dice, die_size, modifier, result = match
        num_dice = int(num_dice)
        die_size = int(die_size)
        
        # Clean up modifier
        if modifier:
            modifier = modifier.strip()
            if not modifier.startswith(('+', '-')):
                modifier = '+' + modifier
        else:
            modifier = "+0"
        
        # Parse modifier value
        try:
            mod_value = int(modifier.replace('+', ''))
            if modifier.startswith('-'):
                mod_value = -mod_value
        except ValueError:
            mod_value = 0
        
        result = int(result) if result else None
        
        # Try to extract roll values from text if available
        roll_values = None
        roll_total = None
        notation = f"{num_dice}d{die_size}"
        idx = text.lower().find(notation.lower())
        if idx >= 0:
            # Look for parentheses with roll values
            after_notation = text[idx:]
            paren_match = re.search(r'\(([^)]+)\)', after_notation)
            if paren_match:
                roll_value_str = paren_match.group(1).strip()
                if ',' in roll_value_str:
                    parts = roll_value_str.split(',')
                    roll_values = []
                    for part in parts:
                        digits = ''.join(filter(str.isdigit, part.strip()))
                        if digits:
                            roll_values.append(int(digits))
                    roll_total = sum(roll_values) if roll_values else None
                else:
                    digits = ''.join(filter(str.isdigit, roll_value_str))
                    if digits:
                        single_value = int(digits)
                        if num_dice == 1:
                            roll_values = [single_value]
                            roll_total = single_value
                        else:
                            roll_values = [single_value]
                            roll_total = single_value
        
        # If we have result but no roll_total, calculate it
        if roll_total is None and result is not None:
            roll_total = result - mod_value
            if num_dice == 1:
                roll_values = [roll_total]
        
        roll_info = {
            "dice": f"{num_dice}d{die_size}",
            "modifier": modifier,
            "full_notation": f"{num_dice}d{die_size}{modifier}",
            "roll_values": roll_values,
            "roll_total": roll_total,
            "result": result,
            "character": None,
            "action": None
        }
        roll_data["rolls"].append(roll_info)
    
    # Save to log file
    log_file = Path("C:/Users/ksist/scripts/discord_dice_logs.json")
    logs = load_logs_safely(log_file)
    logs.append(roll_data)
    safe_write_json_log(log_file, logs)
    
    # Print to console with full info
    for roll in roll_data['rolls']:
        notation = roll['full_notation']
        if roll.get('roll_values'):
            if len(roll['roll_values']) > 1:
                rolls_str = f"{roll['roll_values']}"
            else:
                rolls_str = str(roll['roll_values'][0])
        else:
            rolls_str = "?"
        result = roll.get('result', '?')
        roll_total = roll.get('roll_total', '?')
        modifier = roll.get('modifier', '?')
        print(f"[DICE ROLL] {message.author}: {notation} (rolls: {rolls_str}, total: {roll_total}{modifier}) = {result}")

def load_logs_safely(log_file: Path) -> list:
    """Safely load logs from JSON file with error recovery"""
    logs = []
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # Try to parse as JSON array
                    try:
                        logs = json.loads(content)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError as e:
                        # If parsing fails, try to extract valid JSON from the file
                        # Sometimes there's extra data - try to find the last valid JSON array
                        print(f"[WARNING] JSON parse error: {e}, attempting recovery...")
                        # Try to find the last complete JSON array by looking for closing bracket
                        # Find the last ']' that closes a valid array
                        last_bracket = content.rfind(']')
                        if last_bracket > 0:
                            # Try to find matching opening bracket
                            bracket_count = 0
                            start_pos = last_bracket
                            for i in range(last_bracket, -1, -1):
                                if content[i] == ']':
                                    bracket_count += 1
                                elif content[i] == '[':
                                    bracket_count -= 1
                                    if bracket_count == 0:
                                        start_pos = i
                                        break
                            
                            try:
                                partial = content[start_pos:last_bracket+1]
                                if partial.strip():
                                    logs = json.loads(partial)
                                    if isinstance(logs, list):
                                        print(f"[INFO] Recovered {len(logs)} entries from corrupted file")
                            except:
                                # Fallback: try line by line
                                lines = content.split('\n')
                                for i in range(len(lines), 0, -1):
                                    try:
                                        partial = '\n'.join(lines[:i])
                                        if partial.strip() and partial.strip().endswith(']'):
                                            logs = json.loads(partial)
                                            if isinstance(logs, list):
                                                print(f"[INFO] Recovered {len(logs)} entries from corrupted file")
                                                break
                                    except:
                                        continue
                        if not logs:
                            logs = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Error reading dice log file: {e}, starting fresh")
            logs = []
    return logs

@bot.command(name='roll', help='Roll dice: !roll 1d20+5 or !roll 2d6')
async def roll_dice(ctx, *, dice_notation: str):
    """Manual dice roll command"""
    dice_notation = dice_notation.strip()
    
    # Try to match with modifier first (handles spaces: "1d20 +5")
    match = MODIFIER_PATTERN.match(dice_notation)
    if match:
        num_dice, die_size, mod_sign, mod_value = match.groups()
        modifier = int(f"{mod_sign}{mod_value}")
    else:
        # Try standard pattern
        match = DICE_PATTERN.match(dice_notation)
        if not match:
            await ctx.send(f"Invalid dice notation. Use format like: `!roll 1d20+5` or `!roll 2d6`")
            return
        num_dice, die_size, modifier_str = match.groups()
        modifier = int(modifier_str) if modifier_str else 0
    
    # Simple dice roll (you can enhance this with actual random rolling)
    import random
    num_dice_int = int(num_dice)
    die_size_int = int(die_size)
    rolls = [random.randint(1, die_size_int) for _ in range(num_dice_int)]
    roll_total = sum(rolls)
    total = roll_total + modifier
    modifier_str = f"{'+' if modifier >= 0 else ''}{modifier}"
    
    result = f"{ctx.author.mention} rolled {num_dice}d{die_size}"
    if modifier != 0:
        result += modifier_str
    result += f": {rolls} = **{total}**"
    
    await ctx.send(result)
    
    # Log the roll with result
    roll_data = {
        "timestamp": datetime.now().isoformat(),
        "user": str(ctx.author),
        "user_id": ctx.author.id,
        "channel": str(ctx.channel),
        "source": "Command",
        "rolls": [{
            "dice": f"{num_dice}d{die_size}",
            "modifier": modifier_str,
            "full_notation": f"{num_dice}d{die_size}{modifier_str}",
            "roll_values": rolls,  # Individual die rolls (list)
            "roll_total": roll_total,  # Sum of individual rolls
            "result": total,  # The final total (roll_total + modifier)
            "character": None,  # Manual rolls don't have character context
            "action": None  # Manual rolls don't have action context
        }]
    }
    
    # Print to console
    rolls_str = f"{rolls}" if len(rolls) > 1 else str(rolls[0])
    print(f"[DICE ROLL] {ctx.author} (Command): {num_dice}d{die_size}{modifier_str} (rolls: {rolls_str}, total: {roll_total}{modifier_str}) = {total}")
    
    log_file = Path("C:/Users/ksist/scripts/discord_dice_logs.json")
    logs = load_logs_safely(log_file)
    logs.append(roll_data)
    safe_write_json_log(log_file, logs)

@bot.command(name='dice_logs', help='View recent dice roll logs')
async def view_logs(ctx, limit: int = 10):
    """View recent dice roll logs"""
    log_file = Path("C:/Users/ksist/scripts/discord_dice_logs.json")
    if not log_file.exists():
        await ctx.send("No dice logs found yet.")
        return
    
    logs = load_logs_safely(log_file)
    
    recent_logs = logs[-limit:]
    if not recent_logs:
        await ctx.send("No dice rolls logged yet.")
        return
    
    response = "**Recent Dice Rolls:**\n```\n"
    for log in recent_logs:
        response += f"{log['user']}: {', '.join([r['full_notation'] for r in log['rolls']])}\n"
    response += "```"
    
    await ctx.send(response)

if __name__ == "__main__":
    # Load bot token from environment variable or config file
    import os
    from pathlib import Path
    
    # Try to load from config file
    config_file = Path("C:/Users/ksist/scripts/discord_bot_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            token = config.get('token')
    else:
        # Try environment variable
        token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("ERROR: Discord bot token not found!")
        print("Please create a file: C:/Users/ksist/scripts/discord_bot_config.json")
        print("With content: {\"token\": \"YOUR_BOT_TOKEN_HERE\"}")
        print("\nOr set environment variable: DISCORD_BOT_TOKEN")
        print("\nTo get a token:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a new application")
        print("3. Go to 'Bot' section and create a bot")
        print("4. Copy the token and add it to the config file")
        exit(1)
    
    bot.run(token)
