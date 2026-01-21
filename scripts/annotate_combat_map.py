#!/usr/bin/env python3
"""
Annotate a battle map image with combatant positions.
Supports dynamic position updates and movement trails.

Usage:
    python annotate_combat_map.py <image_path> <output_path> [--positions <json_file>] [--update] [--show-trails]

Examples:
    # Initial annotation
    python annotate_combat_map.py map.png map_annotated.png --positions positions.json
    
    # Update positions (reads from positions file and updates same image)
    python annotate_combat_map.py map.png map_annotated.png --positions positions.json --update
    
    # Show movement trails
    python annotate_combat_map.py map.png map_annotated.png --positions positions.json --show-trails
"""

import sys
import json
import copy
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow library not installed. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def load_positions(json_file=None):
    """Load combatant positions from JSON file or use defaults"""
    if json_file and Path(json_file).exists():
        with open(json_file, 'r') as f:
            return json.load(f)
    
    # Default positions for T17 combat
    return {
        "grid_size": 5,  # 5 feet per square
        "map_width_squares": 20,
        "map_height_squares": 25,
        "combatants": {
            "brevin": {"x": 1, "y": 19, "color": "blue", "label": "B"},
            "vandross": {"x": 3, "y": 19, "color": "blue", "label": "V"},
            "torgga": {"x": 5, "y": 19, "color": "blue", "label": "T"},
            "eglath": {"x": 7, "y": 19, "color": "blue", "label": "E"},
            "zephyr": {"x": 9, "y": 19, "color": "blue", "label": "Z"},
            "malinia": {"x": 9, "y": 11, "color": "red", "label": "M", "elevated": True},
            "gemmule_1": {"x": 6, "y": 12, "color": "orange", "label": "G1"},
            "gemmule_2": {"x": 13, "y": 12, "color": "orange", "label": "G2"},
            "gemmule_3": {"x": 6, "y": 14, "color": "orange", "label": "G3"},
            "gemmule_4": {"x": 13, "y": 14, "color": "orange", "label": "G4"},
        },
        "terrain": {
            "statue": {"x": 9, "y": 12, "width": 2, "height": 3, "color": "gray"},
            "rubble_north": {"x": 0, "y": 0, "width": 20, "height": 2, "color": "darkgray"},
            "rubble_west": {"x": 0, "y": 0, "width": 2, "height": 25, "color": "darkgray"},
        }
    }


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
        "white": (255, 255, 255),
        "black": (0, 0, 0),
    }
    return colors.get(color_name.lower(), (255, 255, 255))


def calculate_pixel_position(square_x, square_y, img_width, img_height, grid_width, grid_height, calibration=None):
    """Calculate pixel position from grid coordinates using calibration if available"""
    if calibration:
        # Use calibrated grid bounds
        grid_tl = calibration.get("grid_tl", (0, 0))
        grid_br = calibration.get("grid_br", (img_width, img_height))
        pixels_per_square_x = calibration.get("pixels_per_square_x", img_width / grid_width)
        pixels_per_square_y = calibration.get("pixels_per_square_y", img_height / grid_height)
        
        # Calculate position relative to calibrated grid
        pixel_x = int(grid_tl[0] + (square_x * pixels_per_square_x) + (pixels_per_square_x / 2))
        pixel_y = int(grid_tl[1] + (square_y * pixels_per_square_y) + (pixels_per_square_y / 2))
    else:
        # Fallback: assume full image is grid (may not be accurate)
        pixels_per_square_x = img_width / grid_width
        pixels_per_square_y = img_height / grid_height
        
        # Calculate center of square
        pixel_x = int(square_x * pixels_per_square_x + pixels_per_square_x / 2)
        pixel_y = int(square_y * pixels_per_square_y + pixels_per_square_y / 2)
    
    return pixel_x, pixel_y


def load_position_history(positions_file):
    """Load position history from JSON file (tracks movement over time)"""
    history_file = Path(positions_file).parent / f"{Path(positions_file).stem}_history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            return json.load(f)
    return {}


def save_position_history(positions_file, combatant_id, old_pos, new_pos):
    """Save position change to history file"""
    history_file = Path(positions_file).parent / f"{Path(positions_file).stem}_history.json"
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = {}
    
    if combatant_id not in history:
        history[combatant_id] = []
    
    history[combatant_id].append({
        "timestamp": datetime.now().isoformat(),
        "from": {"x": old_pos["x"], "y": old_pos["y"]},
        "to": {"x": new_pos["x"], "y": new_pos["y"]}
    })
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)


def annotate_map(image_path, output_path, positions_data=None, show_trails=False, update_mode=False, positions_file=None):
    """Annotate map image with combatant positions"""
    # Load original image (or use output as source if updating)
    source_image = output_path if update_mode and Path(output_path).exists() else image_path
    
    try:
        img = Image.open(source_image)
        # If updating, we want to preserve the base map, so convert carefully
        if img.mode == 'RGBA':
            # Create white background for RGBA images
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = background
        else:
            img = img.convert("RGB")  # Ensure RGB mode
    except Exception as e:
        print(f"ERROR: Could not open image: {e}", file=sys.stderr)
        return False
    
    # Load positions
    if positions_data is None:
        positions_data = load_positions()
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    grid_width = positions_data.get("map_width_squares", 20)
    grid_height = positions_data.get("map_height_squares", 25)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw terrain first (so combatants appear on top)
    terrain = positions_data.get("terrain", {})
    for terrain_name, terrain_data in terrain.items():
        x = terrain_data["x"]
        y = terrain_data["y"]
        width = terrain_data.get("width", 1)
        height = terrain_data.get("height", 1)
        color = get_color(terrain_data.get("color", "gray"))
        
        # Calculate pixel positions for rectangle
        pixels_per_square_x = img_width / grid_width
        pixels_per_square_y = img_height / grid_height
        
        top_left_x = int(x * pixels_per_square_x)
        top_left_y = int(y * pixels_per_square_y)
        bottom_right_x = int((x + width) * pixels_per_square_x)
        bottom_right_y = int((y + height) * pixels_per_square_y)
        
        # Draw semi-transparent rectangle
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [top_left_x, top_left_y, bottom_right_x, bottom_right_y],
            fill=(*color, 128)  # 50% opacity
        )
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
    
    # Get combatants data first (needed for trails)
    combatants = positions_data.get("combatants", {})
    
    # Draw movement trails if requested
    if show_trails and positions_file:
        history = load_position_history(positions_file)
        
        if history:
            for combatant_id, movement_history in history.items():
                if combatant_id not in combatants:
                    continue
                
                color = get_color(combatants[combatant_id].get("color", "gray"))
                trail_color = (*color, 60)  # 25% opacity for trails
                
                # Draw trail from position history
                for i, move in enumerate(movement_history):
                    from_pos = move["from"]
                    to_pos = move["to"]
                    
                    from_px, from_py = calculate_pixel_position(
                        from_pos["x"], from_pos["y"], img_width, img_height, grid_width, grid_height
                    )
                    to_px, to_py = calculate_pixel_position(
                        to_pos["x"], to_pos["y"], img_width, img_height, grid_width, grid_height
                    )
                    
                    # Draw line for movement path
                    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.line(
                        [from_px, from_py, to_px, to_py],
                        fill=trail_color,
                        width=2
                    )
                    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(img)
    
    # Draw combatants
    for combatant_id, combatant_data in combatants.items():
        square_x = combatant_data["x"]
        square_y = combatant_data["y"]
        color = get_color(combatant_data.get("color", "white"))
        label = combatant_data.get("label", combatant_id[0].upper())
        is_elevated = combatant_data.get("elevated", False)
        
        # Calculate pixel position
        pixel_x, pixel_y = calculate_pixel_position(
            square_x, square_y, img_width, img_height, grid_width, grid_height
        )
        
        # Draw circle for combatant
        radius = 15 if is_elevated else 12
        outline_width = 3 if is_elevated else 2
        
        # Draw outer circle (outline)
        draw.ellipse(
            [pixel_x - radius, pixel_y - radius, pixel_x + radius, pixel_y + radius],
            outline=(0, 0, 0),
            width=outline_width
        )
        
        # Draw filled circle
        draw.ellipse(
            [pixel_x - radius + 2, pixel_y - radius + 2, 
             pixel_x + radius - 2, pixel_y + radius - 2],
            fill=color
        )
        
        # Draw label
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = pixel_x - text_width // 2
        text_y = pixel_y - text_height // 2
        
        # Draw text with outline for visibility
        draw.text((text_x - 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x + 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y - 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y + 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)
        
        # Add elevation indicator
        if is_elevated:
            draw.text((pixel_x + radius + 5, pixel_y - 8), "↑20ft", fill=(255, 0, 0), font=small_font)
    
    # Get combat status if available
    combat_status = positions_data.get("combat_status", None)
    current_turn_id = None
    if combat_status:
        current_turn = combat_status.get("current_turn", {})
        current_turn_id = current_turn.get("creature_id") if current_turn else None
    
    # Calculate legend height based on combat status
    legend_height = 120  # Base legend height
    if combat_status:
        # Add space for HP tracker and initiative order
        combatants = combat_status.get("combatants", {})
        legend_height += 20  # "HP TRACKER:" header
        legend_height += len(combatants) * 16  # HP lines
        legend_height += 20  # "INITIATIVE:" header
        initiative_order = combat_status.get("initiative_order", [])
        if not initiative_order:
            # Build initiative order from combatants if not provided
            combatants_list = list(combatants.items())
            initiative_order = [cid for cid, _ in sorted(combatants_list, 
                key=lambda x: combat_status.get("combatants", {}).get(x[0], {}).get("initiative", 0), 
                reverse=True)]
        legend_height += len(initiative_order) * 16  # Initiative lines
        legend_height += 10  # Spacing
    
    # Add legend
    legend_y = 10
    legend_x = img_width - 200  # Make wider for combat info
    draw.rectangle(
        [legend_x - 5, legend_y - 5, legend_x + 195, legend_y + legend_height],
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
    legend_y += 18
    
    draw.rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("darkgray"))
    draw.text((legend_x + 15, legend_y - 2), "Rubble", fill=(0, 0, 0), font=small_font)
    legend_y += 25
    
    # Add HP Tracker if combat status available
    if combat_status:
        combatants = combat_status.get("combatants", {})
        draw.text((legend_x, legend_y), "HP TRACKER:", fill=(0, 0, 0), font=font)
        legend_y += 18
        
        # Map position combatant IDs to combat status IDs
        id_mapping = {
            "brevin": "brevin",
            "vandross": "vandross_ephrates",
            "torgga": "torgga_brawnanvil",
            "eglath": "eglath_bearkiller",
            "zephyr": "zephyr_sparkwhistle",
            "malinia": "malinia",
            "gemmule_1": "gemmule_1",
            "gemmule_2": "gemmule_2",
            "gemmule_3": "gemmule_3",
            "gemmule_4": "gemmule_4",
        }
        
        # Display HP for each combatant
        for pos_id, combat_id in id_mapping.items():
            if pos_id in positions_data.get("combatants", {}) and combat_id in combatants:
                c_data = combatants[combat_id]
                name = c_data.get("name", pos_id)
                hp = c_data.get("hp", "?/?")
                is_alive = c_data.get("is_alive", True)
                
                hp_color = (0, 0, 0) if is_alive else (128, 128, 128)
                draw.text((legend_x + 5, legend_y), f"{name}: {hp}", fill=hp_color, font=small_font)
                legend_y += 16
        
        legend_y += 5
        
        # Add Initiative Order
        draw.text((legend_x, legend_y), "INITIATIVE:", fill=(0, 0, 0), font=font)
        legend_y += 18
        
        # Build initiative order
        initiative_order = combat_status.get("initiative_order", [])
        if not initiative_order:
            # Build from combatants sorted by initiative
            combatants_list = [(cid, c_data) for cid, c_data in combatants.items()]
            combatants_list.sort(key=lambda x: x[1].get("initiative", 0), reverse=True)
            initiative_order = [cid for cid, _ in combatants_list]
        
        # Display initiative order
        for i, cid in enumerate(initiative_order):
            if cid in combatants:
                c_data = combatants[cid]
                name = c_data.get("name", cid)
                initiative = c_data.get("initiative", 0)
                is_current = (cid == current_turn_id)
                
                # Highlight current turn
                if is_current:
                    draw.rectangle(
                        [legend_x - 3, legend_y - 2, legend_x + 185, legend_y + 14],
                        fill=(255, 255, 0, 180),  # Yellow highlight
                        outline=(255, 200, 0),
                        width=2
                    )
                
                turn_indicator = "➤" if is_current else f"{i+1}."
                text_color = (255, 0, 0) if is_current else (0, 0, 0)
                draw.text((legend_x, legend_y), f"{turn_indicator} {name} ({initiative})", 
                         fill=text_color, font=small_font)
                legend_y += 16
    
    # Save annotated image
    try:
        img.save(output_path)
        print(f"SUCCESS: Annotated map saved to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: Could not save image: {e}", file=sys.stderr)
        return False


def update_combatant_position(positions_file, combatant_id, new_x, new_y):
    """Update a single combatant's position in the positions JSON file"""
    if not Path(positions_file).exists():
        print(f"ERROR: Positions file not found: {positions_file}", file=sys.stderr)
        return False
    
    with open(positions_file, 'r') as f:
        positions_data = json.load(f)
    
    if "combatants" not in positions_data:
        positions_data["combatants"] = {}
    
    if combatant_id not in positions_data["combatants"]:
        print(f"WARNING: Combatant {combatant_id} not found in positions file", file=sys.stderr)
        return False
    
    # Save old position for history
    old_pos = {
        "x": positions_data["combatants"][combatant_id].get("x", 0),
        "y": positions_data["combatants"][combatant_id].get("y", 0)
    }
    
    # Update position
    positions_data["combatants"][combatant_id]["x"] = new_x
    positions_data["combatants"][combatant_id]["y"] = new_y
    
    # Save updated positions
    with open(positions_file, 'w') as f:
        json.dump(positions_data, f, indent=2)
    
    # Save to history
    new_pos = {"x": new_x, "y": new_y}
    save_position_history(positions_file, combatant_id, old_pos, new_pos)
    
    print(f"Updated {combatant_id} position: ({old_pos['x']}, {old_pos['y']}) → ({new_x}, {new_y})")
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python annotate_combat_map.py <image_path> <output_path> [OPTIONS]")
        print("\nOptions:")
        print("  --positions <json_file>    Positions JSON file (default: uses defaults)")
        print("  --update                   Update positions on existing annotated image")
        print("  --show-trails              Show movement trails from history")
        print("\nExamples:")
        print("  python annotate_combat_map.py map.png map_annotated.png")
        print("  python annotate_combat_map.py map.png map_annotated.png --positions positions.json")
        print("  python annotate_combat_map.py map.png map_annotated.png --positions positions.json --update")
        print("  python annotate_combat_map.py map.png map_annotated.png --positions positions.json --show-trails")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2]
    
    positions_file = None
    update_mode = False
    show_trails = False
    
    # Parse arguments
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--positions":
            if i + 1 < len(sys.argv):
                positions_file = sys.argv[i + 1]
                i += 2
            else:
                print("ERROR: --positions requires a JSON file path", file=sys.stderr)
                sys.exit(1)
        elif arg == "--update":
            update_mode = True
            i += 1
        elif arg == "--show-trails":
            show_trails = True
            i += 1
        else:
            print(f"ERROR: Unknown argument: {arg}", file=sys.stderr)
            sys.exit(1)
    
    if not Path(image_path).exists() and not update_mode:
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    positions_data = None
    if positions_file:
        if Path(positions_file).exists():
            with open(positions_file, 'r') as f:
                positions_data = json.load(f)
        else:
            print(f"WARNING: Positions file not found, using defaults", file=sys.stderr)
    
    # Pass positions_file to annotate_map for history loading
    if not isinstance(positions_file, str):
        positions_file = None
    
    success = annotate_map(image_path, output_path, positions_data, show_trails, update_mode, positions_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
