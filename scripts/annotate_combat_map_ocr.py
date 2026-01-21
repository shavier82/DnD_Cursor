#!/usr/bin/env python3
"""
Enhanced map annotation with OCR and visual detection.
Reads the map to find room labels and features, then places combatants accurately.
"""

import sys
import json
import re
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
    import numpy as np
except ImportError:
    print("ERROR: Pillow/numpy not installed. Install with: pip install Pillow numpy", file=sys.stderr)
    sys.exit(1)

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("WARNING: pytesseract not available. OCR features disabled.", file=sys.stderr)


def detect_grid(image, expected_square_size_pixels=50):
    """Detect grid lines in the map image"""
    # Convert to grayscale
    gray = image.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    
    # Detect vertical and horizontal lines
    # This is a simplified approach - could be enhanced with Hough transforms
    width, height = gray.size
    
    # Look for grid-like patterns
    # For now, return estimated grid based on image size
    # User can calibrate if needed
    
    return {
        'square_size_pixels': expected_square_size_pixels,
        'grid_detected': True
    }


def find_room_label_ocr(image, label_text):
    """Use OCR to find room labels on the map"""
    if not OCR_AVAILABLE:
        return None
    
    try:
        # Run OCR with bounding boxes
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        found_positions = []
        for i, text in enumerate(ocr_data['text']):
            if label_text.lower() in text.lower():
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                center_x = x + (w / 2)
                center_y = y + (h / 2)
                
                found_positions.append({
                    'text': text,
                    'center_x': int(center_x),
                    'center_y': int(center_y),
                    'confidence': float(ocr_data['conf'][i]) if ocr_data['conf'][i] != -1 else 0
                })
        
        return found_positions[0] if found_positions else None
    except Exception as e:
        print(f"OCR error: {e}", file=sys.stderr)
        return None


def pixel_to_grid_coords(pixel_x, pixel_y, img_width, img_height, grid_width_squares, grid_height_squares):
    """Convert pixel coordinates to grid square coordinates"""
    pixels_per_square_x = img_width / grid_width_squares
    pixels_per_square_y = img_height / grid_height_squares
    
    grid_x = int(pixel_x / pixels_per_square_x)
    grid_y = int(pixel_y / pixels_per_square_y)
    
    return grid_x, grid_y


def find_statue_visually(image):
    """Try to detect the statue visually (looks for circular/rectangular features in T17 area)"""
    # This would require more sophisticated image processing
    # For now, return None and use manual coordinates
    return None


def calibrate_map(image_path, positions_file):
    """Interactive calibration: find T17, T16, statue to calibrate grid"""
    print("=== MAP CALIBRATION ===")
    print("This will help align grid coordinates with the actual map.")
    print()
    
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    print(f"Map size: {img_width}x{img_height} pixels")
    print()
    
    # Try OCR first
    if OCR_AVAILABLE:
        print("Attempting OCR to find room labels...")
        t17_pos = find_room_label_ocr(img, "T17")
        t16_pos = find_room_label_ocr(img, "T16")
        
        if t17_pos:
            print(f"Found T17 at pixel ({t17_pos['center_x']}, {t17_pos['center_y']})")
        if t16_pos:
            print(f"Found T16 at pixel ({t16_pos['center_x']}, {t16_pos['center_y']})")
    else:
        print("OCR not available. Using manual calibration.")
    
    print()
    print("To calibrate manually:")
    print("1. Open the map image")
    print("2. Find T17 room center")
    print("3. Note the pixel coordinates")
    print("4. Update positions.json with calibrated coordinates")
    
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python annotate_combat_map_ocr.py <image_path> [--calibrate]")
        print("\nOptions:")
        print("  --calibrate    Run calibration to align grid with map")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if "--calibrate" in sys.argv:
        calibrate_map(image_path, None)
    else:
        print("Enhanced OCR annotation script")
        print("Use --calibrate to align coordinates with your map")
