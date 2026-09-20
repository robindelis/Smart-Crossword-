# Bench Vision Testing Guide

This guide explains how to run the Computer Vision scanner on your bench setup using your connected **Logitech Brio 100** webcam (or smartphone) and wooden Scrabble tiles, with zero hardware purchases required.

---

## 1. Quick Start: Test with Logitech Brio 100

Your Logitech Brio 100 is connected at video device index `2`.

### Step 1: Activate Environment & Run Live Scanner
In your terminal, run:
```bash
# Run with Logitech Brio 100 (4x4 test mode)
/home/robin/miniconda3/envs/gesturecv/bin/python scripts/bench_vision_scanner.py --camera 2 --grid 4

# Or for full 15x15 Scrabble board:
/home/robin/miniconda3/envs/gesturecv/bin/python scripts/bench_vision_scanner.py --camera 2 --grid 15
```

If you prefer your built-in laptop camera, pass `--camera 0`.

---

## 2. Setting Up Board Markers

To automatically lock perspective and eliminate distortion from camera tilt:
1. Open [`hardware/vision/markers/printable_4corner_markers.png`](file:///home/robin/Smart-Crossword-Board/hardware/vision/markers/printable_4corner_markers.png).
2. Either print the sheet or display each marker on your smartphone/tablet.
3. Place the 4 markers at the 4 corners of your board or test grid:
   * **Top-Left (TL)**: Marker ID 0
   * **Top-Right (TR)**: Marker ID 1
   * **Bottom-Right (BR)**: Marker ID 2
   * **Bottom-Left (BL)**: Marker ID 3
4. Point the camera at the board. The green polygon will lock to the board and rectify it into a perfectly flat square on the right panel.

---

## 3. Keyboard Controls

When the scanner window is focused:

| Key | Action | Purpose |
| :--- | :--- | :--- |
| **`s`** | **Save Snapshot & State** | Saves the raw frame and recognized board JSON state to `data/vision_snapshots/`. |
| **`c`** | **Calibrate / Reset** | Resets tracking corners or allows manual 4-corner click calibration. |
| **`q`** | **Quit** | Exits the scanner. |

---

## 4. Bench Testing Glare & Lighting

One of the biggest real-world challenges with vision is **specular reflection (glare)** from varnished wooden tiles:

1. **Check Glare Readout**:
   * The top bar of the board panel displays **`Glare: X.X%`**.
   * If hot spots from your room lights or desk lamp wash out tile letters, tiles with $>5\%$ glare will show a red warning icon (`!`).
2. **Bench Testing Cross-Polarization**:
   * To see why cross-polarization eliminates glare:
     1. Place a pair of polarized sunglasses (or polarizing film) directly in front of the camera lens.
     2. Shine a desk lamp with another polarizing filter on the board.
     3. Rotate the lens filter by 90°.
     4. Watch the glossy hot spots completely vanish from the tile faces while the black letters remain crisp!

---

## 5. Offline / Headless Testing

You can also run the scanner against any saved image without opening a GUI window:
```bash
/home/robin/miniconda3/envs/gesturecv/bin/python scripts/bench_vision_scanner.py \
  --image tests/data/vision/synthetic_4x4_perspective.png \
  --grid 4 \
  --headless \
  --export output.json
```

---

## 6. Automated Unit Tests

Run the automated test suite anytime to verify marker detection, letter OCR, and glare tracking:
```bash
/home/robin/miniconda3/envs/gesturecv/bin/pytest tests/test_vision_scanner.py -v
```
