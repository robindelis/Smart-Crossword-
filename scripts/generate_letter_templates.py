#!/usr/bin/env python3
"""
Generate Normalized Scrabble Letter Templates for Bench Vision OCR.

Renders normalized 64x64 binary character templates for all 26 uppercase letters (A-Z)
using a clean bold sans-serif font (matching tournament Scrabble tiles).
Also pre-computes 4 rotational orientations: 0°, 90°, 180°, 270°.

Saved in hardware/vision/templates/<letter>_<rot>.png
"""

import os
import string
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def find_system_font():
    """Find a clean bold sans-serif font on the system."""
    candidates = [
        "/usr/share/fonts/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def generate_letter_image(char, font_path, size=64):
    """Render a single character centered in a size x size binary image."""
    img = Image.new("L", (size, size), color=255)
    draw = ImageDraw.Draw(img)
    
    # Target character height is ~65% of tile size
    font_size = int(size * 0.70)
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    
    # Get bounding box for precise centering
    bbox = draw.textbbox((0, 0), char, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]
    
    draw.text((x, y), char, fill=0, font=font)
    
    # Convert to numpy binary array
    np_img = np.array(img, dtype=np.uint8)
    # Ensure strict binary (0 = character, 255 = background)
    _, binary = cv2.threshold(np_img, 128, 255, cv2.THRESH_BINARY)
    return binary

def generate_all_templates(output_dir="hardware/vision/templates"):
    """Generate all letter templates in 4 orientations."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    font_path = find_system_font()
    print(f"Using font: {font_path}")
    
    rotations = [
        (0, cv2.ROTATE_90_CLOCKWISE),      # Placeholder for 0 deg
        (90, cv2.ROTATE_90_CLOCKWISE),
        (180, cv2.ROTATE_180),
        (270, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ]
    
    total_generated = 0
    for char in string.ascii_uppercase:
        base_img = generate_letter_image(char, font_path, size=64)
        
        for deg, rot_code in rotations:
            if deg == 0:
                rot_img = base_img.copy()
            else:
                rot_img = cv2.rotate(base_img, rot_code)
                
            fname = out_path / f"{char}_{deg}.png"
            cv2.imwrite(str(fname), rot_img)
            total_generated += 1
            
    print(f"Generated {total_generated} letter templates in {output_dir}")
    return total_generated

if __name__ == "__main__":
    generate_all_templates()
