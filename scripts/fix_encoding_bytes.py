"""Fix UTF-8 encoding issues at byte level."""
import sys

def fix_file_bytes(file_path):
    """Replace garbled UTF-8 bytes with ASCII."""
    # Read file as bytes
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Replace garbled UTF-8 sequences
    # âœ" is UTF-8 checkmark (✓ = E2 9C 93) read as latin-1
    content = content.replace(b'\xc3\xa2\xc2\x9c\xc2\x93', b'Yes')  # âœ"
    content = content.replace(b'\xe2\x9c\x93', b'Yes')  # ✓ actual UTF-8
    
    # â€" is UTF-8 em dash (— = E2 80 94) read as latin-1
    content = content.replace(b'\xc3\xa2\xc2\x80\xc2\x94', b'-')  # â€"
    content = content.replace(b'\xe2\x80\x94', b'-')  # — actual UTF-8
    content = content.replace(b'\xe2\x80\x93', b'-')  # – en dash
    
    # Fix double pipes (but this is ASCII so simpler)
    lines = content.split(b'\n')
    fixed_lines = []
    for line in lines:
        if line.startswith(b'||'):
            fixed_lines.append(line[1:])
        else:
            fixed_lines.append(line)
    content = b'\n'.join(fixed_lines)
    
    # Write back
    with open(file_path, 'wb') as f:
        f.write(content)
    
    print(f"Fixed encoding (bytes) in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_file_bytes(sys.argv[1])
