#!/usr/bin/env python3
"""
Generate Realistic Synthetic Crossword Boards with ArUco Markers & Wooden Tiles.

Used for automated verification, CI testing, and offline vision bench testing.
Supports:
- 4x4 test grid or 15x15 tournament board
- Simulated wood grain texture and grid ribs
- Placed wooden tiles with letters and scores
- 4 ArUco corner fiducials (IDs 0, 1, 2, 3)
- Perspective distortion and camera angle projection
- Optional specular glare hotspot simulation
"""

import json
import math
import os
import random
import string
from pathlib import Path
import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from scripts.generate_board_markers import get_aruco_dict, generate_marker

def create_wood_texture(width, height, base_color=(195, 160, 120), grain_intensity=25):
    """Generate procedural wood grain texture."""
    np.random.seed(42)
    # Start with base color
    texture = np.ones((height, width, 3), dtype=np.uint8) * np.array(base_color, dtype=np.uint8)
    
    # Add horizontal/vertical grain bands
    y_coords = np.arange(height)
    grain = np.sin(y_coords / 4.0) * grain_intensity + np.random.normal(0, grain_intensity * 0.4, height)
    grain = grain.astype(np.int16)
    
    for c in range(3):
        col = texture[:, :, c].astype(np.int16) + grain[:, None]
        texture[:, :, c] = np.clip(col, 0, 255).astype(np.uint8)
        
    # Gaussian blur to soften wood grain
    texture = cv2.GaussianBlur(texture, (5, 5), 0)
    return texture

def render_synthetic_board(grid_size=4, tiles_dict=None, board_px=1000, margin_px=150, font_path="/usr/share/fonts/noto/NotoSans-Bold.ttf"):
    """
    Render top-down synthetic board with corner ArUco markers.
    
    grid_size: 4 or 15
    tiles_dict: {(r, c): 'A', ...}
    board_px: size of active grid in pixels
    margin_px: outer wooden margin containing ArUco markers
    """
    if tiles_dict is None:
        # Default 4x4 pattern: "WORD" on row 1, "TEST" on row 2
        if grid_size == 4:
            tiles_dict = {
                (1, 0): 'W', (1, 1): 'O', (1, 2): 'R', (1, 3): 'D',
                (2, 0): 'C', (2, 1): 'A', (2, 2): 'R', (2, 3): 'T'
            }
        else:
            tiles_dict = {
                (7, 4): 'S', (7, 5): 'M', (7, 6): 'A', (7, 7): 'R', (7, 8): 'T',
                (5, 7): 'F', (6, 7): 'I', (7, 7): 'R', (8, 7): 'S', (9, 7): 'T'
            }

    total_size = board_px + 2 * margin_px
    canvas = create_wood_texture(total_size, total_size, base_color=(175, 140, 95))
    
    cell_px = board_px // grid_size
    grid_x0 = margin_px
    grid_y0 = margin_px
    
    # Draw grid background (lighter recessed wood)
    grid_roi = create_wood_texture(board_px, board_px, base_color=(205, 175, 130))
    canvas[grid_y0:grid_y0 + board_px, grid_x0:grid_x0 + board_px] = grid_roi
    
    # Draw grid lines / ribs
    rib_color = (110, 80, 50)
    for i in range(grid_size + 1):
        # Vertical ribs
        x = grid_x0 + i * cell_px
        cv2.line(canvas, (x, grid_y0), (x, grid_y0 + board_px), rib_color, 3)
        # Horizontal ribs
        y = grid_y0 + i * cell_px
        cv2.line(canvas, (grid_x0, y), (grid_x0 + board_px, y), rib_color, 3)
        
    # Draw 4 Corner ArUco Markers inside the outer bezel
    aruco_dict = get_aruco_dict()
    marker_size = int(margin_px * 0.75)
    pad = (margin_px - marker_size) // 2
    
    # Marker positions (TL=0, TR=1, BR=2, BL=3)
    corners = [
        (0, pad, pad),                                      # Top-Left (ID 0)
        (1, total_size - pad - marker_size, pad),           # Top-Right (ID 1)
        (2, total_size - pad - marker_size, total_size - pad - marker_size), # Bottom-Right (ID 2)
        (3, pad, total_size - pad - marker_size)            # Bottom-Left (ID 3)
    ]
    
    for mid, mx, my in corners:
        m_img = generate_marker(aruco_dict, mid, size_px=marker_size)
        m_bgr = cv2.cvtColor(m_img, cv2.COLOR_GRAY2BGR)
        # White paper border around marker
        cv2.rectangle(canvas, (mx - 4, my - 4), (mx + marker_size + 4, my + marker_size + 4), (245, 245, 245), -1)
        canvas[my:my + marker_size, mx:mx + marker_size] = m_bgr
        
    # Scrabble point scores
    scores = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
        'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
        'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10
    }
    
    font_main = ImageFont.truetype(font_path, int(cell_px * 0.55)) if os.path.exists(font_path) else ImageFont.load_default()
    font_sub = ImageFont.truetype(font_path, int(cell_px * 0.18)) if os.path.exists(font_path) else ImageFont.load_default()
    
    # Render placed wooden tiles
    tile_inset = int(cell_px * 0.08)
    tile_w = cell_px - 2 * tile_inset
    
    for (r, c), letter in tiles_dict.items():
        if r >= grid_size or c >= grid_size:
            continue
        cx0 = grid_x0 + c * cell_px + tile_inset
        cy0 = grid_y0 + r * cell_px + tile_inset
        
        # Tile drop shadow
        cv2.rectangle(canvas, (cx0 + 3, cy0 + 3), (cx0 + tile_w + 3, cy0 + tile_w + 3), (90, 70, 45), -1)
        
        # Wooden tile body
        tile_wood = create_wood_texture(tile_w, tile_w, base_color=(235, 205, 155), grain_intensity=15)
        # Soft beveled tile edge
        cv2.rectangle(tile_wood, (0, 0), (tile_w - 1, tile_w - 1), (180, 150, 105), 1)
        canvas[cy0:cy0 + tile_w, cx0:cx0 + tile_w] = tile_wood
        
        # Draw letter with PIL
        pil_canvas = Image.fromarray(canvas)
        draw = ImageDraw.Draw(pil_canvas)
        
        # Center letter
        bbox = draw.textbbox((0, 0), letter, font=font_main)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        lx = cx0 + (tile_w - lw) // 2 - bbox[0]
        ly = cy0 + (tile_w - lh) // 2 - bbox[1] - int(tile_w * 0.05)
        draw.text((lx, ly), letter, fill=(20, 20, 20), font=font_main)
        
        # Subscript point score
        score_val = str(scores.get(letter, ""))
        if score_val:
            s_bbox = draw.textbbox((0, 0), score_val, font=font_sub)
            sx = cx0 + tile_w - (s_bbox[2] - s_bbox[0]) - int(tile_w * 0.12)
            sy = cy0 + tile_w - (s_bbox[3] - s_bbox[1]) - int(tile_w * 0.12)
            draw.text((sx, sy), score_val, fill=(35, 35, 35), font=font_sub)
            
        canvas = np.array(pil_canvas)

    return canvas, tiles_dict

def apply_perspective_and_lighting(image, angle_deg=18.0, add_glare=False):
    """Simulate a camera viewing the board from an angle and distance."""
    h, w = image.shape[:2]
    
    # Destination points with perspective keystone
    shift_x = int(w * 0.12)
    shift_y = int(h * 0.08)
    
    pts_src = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ])
    
    pts_dst = np.float32([
        [shift_x, shift_y],             # Top-Left pinched inward & down
        [w - shift_x, shift_y],         # Top-Right pinched inward & down
        [w - int(shift_x * 0.2), h - int(shift_y * 0.2)], # Bottom-Right
        [int(shift_x * 0.2), h - int(shift_y * 0.2)]      # Bottom-Left
    ])
    
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(image, M, (w, h), borderValue=(30, 30, 30))
    
    if add_glare:
        # Add simulated specular reflection hot spot near center
        glare_mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(glare_mask, (w // 2 + 50, h // 2 - 40), 120, 1.0, -1)
        glare_mask = cv2.GaussianBlur(glare_mask, (101, 101), 0)
        
        warped_float = warped.astype(np.float32)
        for c in range(3):
            warped_float[:, :, c] += glare_mask * 180.0
        warped = np.clip(warped_float, 0, 255).astype(np.uint8)
        
    return warped

def generate_test_board_suite(output_dir="tests/data/vision"):
    """Generate standard synthetic test cases."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Orthogonal 4x4 board
    board_4x4, tiles_4x4 = render_synthetic_board(grid_size=4)
    cv2.imwrite(str(out_path / "synthetic_4x4_ortho.png"), board_4x4)
    with open(out_path / "synthetic_4x4_ground_truth.json", "w") as f:
        json.dump({f"{r},{c}": l for (r, c), l in tiles_4x4.items()}, f, indent=2)
        
    # 2. Perspective-warped 4x4 board (realistic camera view)
    board_4x4_persp = apply_perspective_and_lighting(board_4x4, add_glare=False)
    cv2.imwrite(str(out_path / "synthetic_4x4_perspective.png"), board_4x4_persp)
    
    # 3. Perspective-warped with Specular Glare (for glare testing)
    board_4x4_glare = apply_perspective_and_lighting(board_4x4, add_glare=True)
    cv2.imwrite(str(out_path / "synthetic_4x4_glare.png"), board_4x4_glare)
    
    # 4. Orthogonal 15x15 board
    board_15x15, tiles_15x15 = render_synthetic_board(grid_size=15, board_px=1200, margin_px=120)
    cv2.imwrite(str(out_path / "synthetic_15x15_ortho.png"), board_15x15)
    with open(out_path / "synthetic_15x15_ground_truth.json", "w") as f:
        json.dump({f"{r},{c}": l for (r, c), l in tiles_15x15.items()}, f, indent=2)

    print(f"Generated synthetic test suite in {output_dir}")
    return out_path

if __name__ == "__main__":
    generate_test_board_suite()
