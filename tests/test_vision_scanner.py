#!/usr/bin/env python3
"""
Unit and Integration Tests for Smart Crossword Board Vision Scanner Suite.

Tests:
1. ArUco Marker Generation and Dictionary Loading.
2. Letter Template Loading and 4-Orientation Coverage.
3. Perspective Rectification via Corner Markers.
4. Tile Occupancy Detection & Character OCR.
5. Specular Glare Detection and Quantification.
6. Processing Latency Ceiling Compliance (<600ms).
"""

import json
from pathlib import Path
import cv2
import numpy as np
import pytest

from scripts.generate_board_markers import get_aruco_dict, generate_marker
from scripts.bench_vision_scanner import CrosswordVisionScanner

@pytest.fixture(scope="module")
def scanner():
    return CrosswordVisionScanner(grid_size=4)

def test_aruco_dictionary_and_markers():
    """Verify ArUco dictionary loads and generates valid binary markers."""
    aruco_dict = get_aruco_dict()
    assert aruco_dict is not None
    
    for mid in range(4):
        marker_img = generate_marker(aruco_dict, mid, size_px=200)
        assert marker_img.shape == (200, 200)
        assert marker_img.dtype == np.uint8
        # Outer border must be black (0)
        assert np.mean(marker_img[0, :]) == 0.0

def test_letter_templates_loaded(scanner):
    """Verify all 26 letters in 4 orientations (104 total) are loaded."""
    assert len(scanner.templates) == 104
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for rot in [0, 90, 180, 270]:
            assert (char, rot) in scanner.templates
            templ = scanner.templates[(char, rot)]
            assert templ.shape == (64, 64)
            assert np.sum(templ == 255) > 100  # contains ink pixels

def test_rectification_on_perspective_board(scanner):
    """Verify 4 corner ArUco markers are detected and warped to orthogonal square."""
    img_path = Path("tests/data/vision/synthetic_4x4_perspective.png")
    assert img_path.exists(), "Synthetic test image must exist"
    
    image = cv2.imread(str(img_path))
    corners = scanner.detect_aruco_corners(image)
    assert corners is not None
    assert len(corners) == 4
    
    warped, M = scanner.rectify_board(image, target_size=1000)
    assert warped is not None
    assert warped.shape == (1000, 1000, 3)
    assert M is not None

def test_character_recognition_accuracy(scanner):
    """Verify 100% letter recognition on perspective-warped synthetic 4x4 board."""
    img_path = Path("tests/data/vision/synthetic_4x4_perspective.png")
    result = scanner.run_on_image(img_path, headless=True)
    
    assert result is not None
    assert result["grid_size"] == 4
    assert result["latency_ms"] < 600.0, f"Latency {result['latency_ms']}ms exceeded 600ms ceiling"
    
    # Expected: Row 1 = WORD, Row 2 = CART
    expected_tiles = {
        (1, 0): "W", (1, 1): "O", (1, 2): "R", (1, 3): "D",
        (2, 0): "C", (2, 1): "A", (2, 2): "R", (2, 3): "T"
    }
    
    detected_tiles = {(t["row"], t["col"]): t["letter"] for t in result["tiles"]}
    
    assert len(detected_tiles) == 8, f"Expected 8 tiles, got {len(detected_tiles)}"
    for (r, c), expected_char in expected_tiles.items():
        assert (r, c) in detected_tiles, f"Tile at ({r},{c}) was not detected"
        assert detected_tiles[(r, c)] == expected_char, \
            f"At ({r},{c}): expected {expected_char}, got {detected_tiles[(r, c)]}"

def test_specular_glare_quantification(scanner):
    """Verify specular glare hot spots are accurately flagged and quantified."""
    glare_path = Path("tests/data/vision/synthetic_4x4_glare.png")
    assert glare_path.exists()
    
    result = scanner.run_on_image(glare_path, headless=True)
    assert result is not None
    
    # Check that cells under the simulated center glare spot have high glare ratios
    tiles_by_pos = {(t["row"], t["col"]): t for t in result["tiles"]}
    
    # Center tiles (1,1), (1,2) should have noticeable glare (> 0.05)
    assert tiles_by_pos[(1, 1)]["glare_ratio"] > 0.05
    assert tiles_by_pos[(1, 2)]["glare_ratio"] > 0.15
    
    # Edge tile (1,0) should have near-zero glare
    assert tiles_by_pos[(1, 0)]["glare_ratio"] < 0.02
