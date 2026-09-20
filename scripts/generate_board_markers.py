#!/usr/bin/env python3
"""
Generate Printable ArUco Fiducial Markers for Smart Crossword Board Vision Calibration.

Generates 4 corner markers (Dictionary: DICT_4X4_50):
- ID 0: Top-Left (TL)
- ID 1: Top-Right (TR)
- ID 2: Bottom-Right (BR)
- ID 3: Bottom-Left (BL)

Outputs high-resolution PNGs and a combined 4-corner printable sheet to hardware/vision/markers/.
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np

def get_aruco_dict():
    """Get the 4x4 ArUco dictionary across OpenCV versions."""
    if hasattr(cv2.aruco, 'getPredefinedDictionary'):
        return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    elif hasattr(cv2.aruco, 'Dictionary_get'):
        return cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    else:
        raise RuntimeError("ArUco dictionary not found in cv2.aruco")

def generate_marker(aruco_dict, marker_id, size_px=400, border_bits=1):
    """Generate a single ArUco marker image with border."""
    if hasattr(cv2.aruco, 'generateImageMarker'):
        marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size_px, borderBits=border_bits)
    elif hasattr(cv2.aruco, 'drawMarker'):
        marker_img = np.zeros((size_px, size_px), dtype=np.uint8)
        cv2.aruco.drawMarker(aruco_dict, marker_id, size_px, marker_img, border_bits)
    else:
        raise RuntimeError("cv2.aruco has no generateImageMarker or drawMarker")
    return marker_img

def create_labeled_marker(marker_img, label, marker_id, total_size=600):
    """Embed marker inside a white canvas with human-readable text."""
    canvas = np.full((total_size, total_size), 255, dtype=np.uint8)
    m_h, m_w = marker_img.shape
    y_offset = 60
    x_offset = (total_size - m_w) // 2
    canvas[y_offset:y_offset + m_h, x_offset:x_offset + m_w] = marker_img
    
    # Text label
    text = f"{label} (ID: {marker_id})"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (total_size - text_size[0]) // 2
    text_y = total_size - 40
    cv2.putText(canvas, text, (text_x, text_y), font, font_scale, 0, thickness, cv2.LINE_AA)
    
    # Outer thin border for cutting guide
    cv2.rectangle(canvas, (10, 10), (total_size - 10, total_size - 10), 200, 1)
    return canvas

def generate_all_markers(output_dir="hardware/vision/markers"):
    """Generate individual and combined marker sheets."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    aruco_dict = get_aruco_dict()
    corners = [
        ("Top-Left", 0),
        ("Top-Right", 1),
        ("Bottom-Right", 2),
        ("Bottom-Left", 3)
    ]
    
    labeled_cards = []
    for label, mid in corners:
        m_img = generate_marker(aruco_dict, mid, size_px=400)
        card = create_labeled_marker(m_img, label, mid, total_size=600)
        fname = out_path / f"marker_{mid}_{label.lower().replace('-', '_')}.png"
        cv2.imwrite(str(fname), card)
        print(f"Generated: {fname}")
        labeled_cards.append(card)
        
    # Generate combined 2x2 printable sheet (1200x1200)
    sheet = np.full((1200, 1200), 255, dtype=np.uint8)
    sheet[0:600, 0:600] = labeled_cards[0]       # Top-Left (ID 0)
    sheet[0:600, 600:1200] = labeled_cards[1]     # Top-Right (ID 1)
    sheet[600:1200, 600:1200] = labeled_cards[2] # Bottom-Right (ID 2)
    sheet[600:1200, 0:600] = labeled_cards[3]    # Bottom-Left (ID 3)
    
    # Center cutting guides
    cv2.line(sheet, (600, 0), (600, 1200), 180, 1, cv2.LINE_AA)
    cv2.line(sheet, (0, 600), (1200, 600), 180, 1, cv2.LINE_AA)
    
    sheet_fname = out_path / "printable_4corner_markers.png"
    cv2.imwrite(str(sheet_fname), sheet)
    print(f"\nGenerated combined printable sheet: {sheet_fname}")
    return sheet_fname

if __name__ == "__main__":
    generate_all_markers()
