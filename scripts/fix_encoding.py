"""Fix UTF-8 encoding issues in character files."""
import sys
from pathlib import Path

def fix_file_encoding(file_path):
    """Replace Unicode characters with ASCII-safe alternatives."""
    # Read as latin-1 to preserve the garbled bytes
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # Replace garbled UTF-8 sequences (what you see when UTF-8 is read as latin-1)
    content = content.replace('â\x9c\x93', 'Yes')  # ✓ checkmark garbled
    content = content.replace('â\x80\x94', '-')    # — em dash garbled
    content = content.replace('â\x80\x93', '-')    # – en dash garbled
    
    # Also replace actual UTF-8 characters just in case
    # Re-encode to UTF-8 and decode properly
    try:
        # Try to fix by encoding back to bytes and decoding as UTF-8
        bytes_content = content.encode('latin-1')
        content = bytes_content.decode('utf-8', errors='ignore')
        content = content.replace('✓', 'Yes')
        content = content.replace('—', '-')
        content = content.replace('–', '-')
    except:
        pass  # If decoding fails, keep the replaced version
    
    # Fix double pipes at start of lines
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if line.startswith('||'):
            fixed_lines.append(line[1:])  # Remove first pipe
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Write back with UTF-8 encoding
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed encoding in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_file_encoding(sys.argv[1])
    else:
        # Fix all character files
        char_dir = Path(r"C:\Users\ksist\Documents\Obsidian\DnD\Player Characters")
        for md_file in char_dir.glob("*.md"):
            fix_file_encoding(md_file)
