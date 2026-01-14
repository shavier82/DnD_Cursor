"""Parse D&D Beyond character sheet PDFs and combine with Google Sheets data"""

import requests
import sys
import io
from pathlib import Path
import json
import re

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 not installed. Run: pip install PyPDF2")
    sys.exit(1)

# Character PDF URLs
PDF_URLS = {
    "Eglath_Bearkiller": "https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157266647.pdf",
    "Vandross_Ephrates": "https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157455174.pdf",
    "Torgga_Brawnanvil": "https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_157333848.pdf",
    "Brevin": "https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_95127852.pdf",
    "Zephyr_Sparkwhistle": "https://www.dndbeyond.com/sheet-pdfs/ShavierT1982_158781310.pdf",
}

def download_pdf(url):
    """Download PDF from URL"""
    print(f"  Downloading {url}...")
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)

def extract_text_from_pdf(pdf_stream):
    """Extract text from PDF"""
    reader = PyPDF2.PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def parse_ability_score(text, ability_name):
    """Extract ability score and modifier from text"""
    # Look for patterns like "STRENGTH 16 +3" or "STR 16 +3"
    patterns = [
        rf"{ability_name}[\s\n]+(\d+)[\s\n]+([+-]\d+)",
        rf"{ability_name[:3]}[\s\n]+(\d+)[\s\n]+([+-]\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return score
    
    return 10  # Default

def parse_character_pdf(text, char_name):
    """Parse character data from PDF text"""
    print(f"  Parsing {char_name}...")
    
    # Extract ability scores
    ability_scores = {
        "strength": parse_ability_score(text, "STRENGTH"),
        "dexterity": parse_ability_score(text, "DEXTERITY"),
        "constitution": parse_ability_score(text, "CONSTITUTION"),
        "intelligence": parse_ability_score(text, "INTELLIGENCE"),
        "wisdom": parse_ability_score(text, "WISDOM"),
        "charisma": parse_ability_score(text, "CHARISMA"),
    }
    
    # Extract race
    race = "Unknown"
    race_match = re.search(r"RACE\s+([A-Za-z\s]+)", text, re.IGNORECASE)
    if race_match:
        race = race_match.group(1).strip()
    
    # Extract background
    background = ""
    bg_match = re.search(r"BACKGROUND\s+([A-Za-z\s]+)", text, re.IGNORECASE)
    if bg_match:
        background = bg_match.group(1).strip()
    
    # Extract alignment
    alignment = ""
    align_match = re.search(r"ALIGNMENT\s+([A-Za-z\s]+)", text, re.IGNORECASE)
    if align_match:
        alignment = align_match.group(1).strip()
    
    # Extract speed
    speed = 30
    speed_match = re.search(r"SPEED\s+(\d+)", text, re.IGNORECASE)
    if speed_match:
        speed = int(speed_match.group(1))
    
    # Extract initiative bonus
    init_bonus = (ability_scores["dexterity"] - 10) // 2
    init_match = re.search(r"INITIATIVE\s+([+-]\d+)", text, re.IGNORECASE)
    if init_match:
        init_bonus = int(init_match.group(1))
    
    # Extract saving throw proficiencies
    saving_throws = []
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        pattern = rf"{ability[:3].upper()}.*?SAVING THROWS.*?([+-]\d+)"
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            saving_throws.append(ability)
    
    # Extract skill proficiencies
    skills = []
    skill_names = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    for skill in skill_names:
        if re.search(rf"●\s*{skill}", text, re.IGNORECASE):
            skills.append(skill)
    
    # Extract languages
    languages = []
    lang_match = re.search(r"LANGUAGES\s+([A-Za-z,\s]+)", text, re.IGNORECASE)
    if lang_match:
        lang_text = lang_match.group(1).strip()
        languages = [lang.strip() for lang in lang_text.split(',') if lang.strip()]
    
    # Extract features (simplified - just grab feature names)
    features = []
    # This would need more sophisticated parsing based on PDF structure
    
    return {
        "ability_scores": ability_scores,
        "race": race,
        "background": background,
        "alignment": alignment,
        "speed": speed,
        "initiative_bonus": init_bonus,
        "saving_throw_proficiencies": saving_throws,
        "skill_proficiencies": skills,
        "languages": languages,
        "features": features,
    }

def main():
    print("=" * 80)
    print("D&D BEYOND PDF PARSER")
    print("=" * 80)
    print()
    
    output_dir = Path("C:/DnD/Campaigns/Phandelver/character_data_from_pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parsed_data = {}
    
    for char_name, url in PDF_URLS.items():
        try:
            print(f"\n[{char_name}]")
            
            # Download PDF
            pdf_stream = download_pdf(url)
            
            # Extract text
            text = extract_text_from_pdf(pdf_stream)
            
            # Parse character data
            char_data = parse_character_pdf(text, char_name)
            
            # Save to file
            output_file = output_dir / f"{char_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=2)
            
            parsed_data[char_name] = char_data
            
            print(f"  ✓ Saved to {output_file}")
            print(f"    Ability Scores: STR {char_data['ability_scores']['strength']}, "
                  f"DEX {char_data['ability_scores']['dexterity']}, "
                  f"CON {char_data['ability_scores']['constitution']}")
            print(f"    Race: {char_data['race']}")
            print(f"    Skills: {len(char_data['skill_proficiencies'])} proficiencies")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 80)
    print(f"✓ Parsed {len(parsed_data)} character PDFs")
    print(f"✓ Saved to: {output_dir}")
    print()
    print("Next: Run export script to combine with Google Sheets data")
    print("  python scripts\\export_campaign_to_obsidian.py")
    print("=" * 80)

if __name__ == "__main__":
    main()




