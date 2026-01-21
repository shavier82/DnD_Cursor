#!/usr/bin/env python3
"""
Create a basic battlemap with grid and combatant positions.
Simple coordinate-based system.
"""

import sys
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def get_color(color_name):
    """Convert color name to RGB tuple"""
    colors = {
        "blue": (0, 100, 255),
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "purple": (128, 0, 128),
        "gray": (128, 128, 128),
        "darkgray": (64, 64, 64),
        "lightgray": (200, 200, 200),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
    }
    return colors.get(color_name.lower(), (255, 255, 255))


def create_battlemap(positions_file, output_path, grid_size_pixels=50):
    """Create a battlemap from positions JSON"""
    # Load positions
    with open(positions_file, 'r') as f:
        data = json.load(f)
    
    grid_width = data.get("map_width_squares", 20)
    grid_height = data.get("map_height_squares", 25)
    
    # Calculate image size
    img_width = grid_width * grid_size_pixels
    img_height = grid_height * grid_size_pixels
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw grid
    grid_color = get_color("lightgray")
    for x in range(0, img_width, grid_size_pixels):
        draw.line([(x, 0), (x, img_height)], fill=grid_color, width=1)
    for y in range(0, img_height, grid_size_pixels):
        draw.line([(0, y), (img_width, y)], fill=grid_color, width=1)
    
    # Draw terrain
    terrain = data.get("terrain", {})
    for terrain_name, terrain_data in terrain.items():
        x = terrain_data["x"] * grid_size_pixels
        y = terrain_data["y"] * grid_size_pixels
        width = terrain_data.get("width", 1) * grid_size_pixels
        height = terrain_data.get("height", 1) * grid_size_pixels
        color = get_color(terrain_data.get("color", "gray"))
        
        draw.rectangle([x, y, x + width, y + height], fill=color, outline=(0, 0, 0), width=2)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw combatants
    combatants = data.get("combatants", {})
    defeated = data.get("defeated", [])  # List of defeated combatant IDs
    
    for combatant_id, combatant_data in combatants.items():
        # Skip defeated combatants
        if combatant_id in defeated:
            continue
        square_x = combatant_data["x"]
        square_y = combatant_data["y"]
        color = get_color(combatant_data.get("color", "white"))
        label = combatant_data.get("label", combatant_id[0].upper())
        is_elevated = combatant_data.get("elevated", False)
        
        # Calculate pixel position (center of square)
        pixel_x = int((square_x * grid_size_pixels) + (grid_size_pixels / 2))
        pixel_y = int((square_y * grid_size_pixels) + (grid_size_pixels / 2))
        
        # Draw circle
        radius = 18 if is_elevated else 15
        outline_width = 3 if is_elevated else 2
        
        # Outer circle (outline)
        draw.ellipse(
            [pixel_x - radius, pixel_y - radius, pixel_x + radius, pixel_y + radius],
            outline=(0, 0, 0),
            width=outline_width
        )
        
        # Filled circle
        draw.ellipse(
            [pixel_x - radius + 2, pixel_y - radius + 2,
             pixel_x + radius - 2, pixel_y + radius - 2],
            fill=color
        )
        
        # Label
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = pixel_x - text_width // 2
        text_y = pixel_y - text_height // 2
        
        # Text with outline
        draw.text((text_x - 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x + 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y - 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y + 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)
        
        # Elevation indicator
        if is_elevated:
            draw.text((pixel_x + radius + 3, pixel_y - 8), "↑20ft", fill=(255, 0, 0), font=small_font)
    
    # Add legend
    legend_x = img_width - 140
    legend_y = 10
    draw.rectangle(
        [legend_x - 5, legend_y - 5, legend_x + 135, legend_y + 100],
        fill=(255, 255, 255, 240),
        outline=(0, 0, 0),
        width=2
    )
    
    draw.text((legend_x, legend_y), "LEGEND:", fill=(0, 0, 0), font=font)
    legend_y += 20
    
    # Party
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("blue"))
    draw.text((legend_x + 15, legend_y - 2), "Party", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    # Enemies
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("red"))
    draw.text((legend_x + 15, legend_y - 2), "Malinia", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("orange"))
    draw.text((legend_x + 15, legend_y - 2), "Gemmules", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    # Terrain
    draw.rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("gray"))
    draw.text((legend_x + 15, legend_y - 2), "Statue", fill=(0, 0, 0), font=small_font)
    
    # Save
    img.save(output_path)
    print(f"Battlemap created: {output_path}")
    print(f"Size: {grid_width}x{grid_height} squares ({img_width}x{img_height} pixels)")
    print(f"Grid: {grid_size_pixels} pixels per square (5 feet)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python create_battlemap.py <positions_json> <output_image> [grid_size_pixels]")
        print("\nExample:")
        print("  python create_battlemap.py combat_positions_t17.json battlemap.png")
        print("  python create_battlemap.py combat_positions_t17.json battlemap.png 60")
        sys.exit(1)
    
    positions_file = sys.argv[1]
    output_path = sys.argv[2]
    grid_size = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    if not Path(positions_file).exists():
        print(f"ERROR: Positions file not found: {positions_file}", file=sys.stderr)
        sys.exit(1)
    
    create_battlemap(positions_file, output_path, grid_size)


if __name__ == "__main__":
    main()
