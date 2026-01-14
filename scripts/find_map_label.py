#!/usr/bin/env python3
"""
Find a label on a map image using OCR
"""
import sys
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    import json
except ImportError as e:
    print(f"ERROR: Missing libraries: {e}", file=sys.stderr)
    sys.exit(1)

def find_label_in_image(image_path, label_text):
    """Find label text in image and return coordinates"""
    try:
        # Open image
        img = Image.open(image_path)
        
        # Run OCR to get data with bounding boxes
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Search for the label text
        found_positions = []
        text_found = ""
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                text_found += text + " "
            if label_text.lower() in text.lower() or text.lower() == label_text.lower():
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                conf = ocr_data['conf'][i]
                
                # Get center coordinates
                center_x = x + (w / 2)
                center_y = y + (h / 2)
                
                found_positions.append({
                    'text': text,
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(center_x),
                    'center_y': int(center_y),
                    'confidence': float(conf) if conf != -1 else 0
                })
        
        return found_positions, text_found[:200]  # Return first 200 chars of detected text
        
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python find_map_label.py <image_path> <label_text>", file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    label_text = sys.argv[2]
    
    if not Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    positions, text_sample = find_label_in_image(image_path, label_text)
    
    if positions:
        # Return JSON with found positions
        result = {
            'found': True,
            'label': label_text,
            'positions': positions,
            'text_sample': text_sample
        }
        print(json.dumps(result, indent=2))
    else:
        result = {
            'found': False,
            'label': label_text,
            'error': text_sample if not positions else None,
            'text_sample': text_sample if text_sample else 'No text detected'
        }
        print(json.dumps(result, indent=2))


















