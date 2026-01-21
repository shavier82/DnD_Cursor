"""Fix encoding and formatting on all character files."""
from pathlib import Path

def fix_character_file(file_path):
    """Fix encoding and table formatting in a character file."""
    print(f"\nProcessing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Replace Unicode and garbled characters with ASCII
    replacements = [
        ('✓', 'Yes', 'Unicode checkmark'),
        ('—', '-', 'Em dash'),
        ('–', '-', 'En dash'),
        ('âœ"', 'Yes', 'Garbled checkmark'),
        ('â€"', '-', 'Garbled em dash'),
        ('â€"', '-', 'Garbled en dash variant'),
    ]
    
    for old, new, desc in replacements:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes.append(f"  - Replaced {count}x {desc}")
    
    # Fix double pipes at start of lines
    lines = content.split('\n')
    fixed_lines = []
    double_pipe_count = 0
    
    for line in lines:
        if line.startswith('||'):
            fixed_lines.append(line[1:])
            double_pipe_count += 1
        else:
            fixed_lines.append(line)
    
    if double_pipe_count > 0:
        changes.append(f"  - Fixed {double_pipe_count}x double pipes")
    
    content = '\n'.join(fixed_lines)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [FIXED]:")
        for change in changes:
            print(change)
    else:
        print(f"  [OK] No changes needed")
    
    return len(changes) > 0

if __name__ == "__main__":
    char_dir = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
    
    # Only process main character files (not spell lists or temps)
    character_files = [
        "Brevin.md",
        "Eglath_Bearkiller.md",
        "Torgga_Brawnanvil.md",
        "Vandross_Ephrates.md",
        "Zephyr_Sparkwhistle.md"
    ]
    
    total_fixed = 0
    for filename in character_files:
        file_path = char_dir / filename
        if file_path.exists():
            if fix_character_file(file_path):
                total_fixed += 1
        else:
            print(f"\n⚠ File not found: {filename}")
    
    print(f"\n{'='*50}")
    print(f"Summary: Fixed {total_fixed} of {len(character_files)} files")
    print(f"{'='*50}")
