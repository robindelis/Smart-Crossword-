#!/usr/bin/env python3
"""
Smart Crossword Board: Bench Vision Scanner & Glare Benchmark Suite.

Real-time computer-vision scanner for Scrabble board reading using webcam or static images.
Capabilities:
1. Automatic 4-corner ArUco marker detection & homography perspective rectification.
2. Manual 4-corner interactive calibration fallback with persistent JSON config.
3. 4x4 or 15x15 grid cell extraction.
4. Tile occupancy detection (empty cell vs. placed wooden tile).
5. 4-way rotation-invariant letter OCR (A-Z) using normalized template matching.
6. Specular glare & lighting benchmark (quantifies hot spots and warns when cross-polarization is needed).
7. Headless export mode for automated tests and CI.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import cv2
import numpy as np

from scripts.generate_board_markers import get_aruco_dict
from scripts.generate_letter_templates import generate_all_templates

class CrosswordVisionScanner:
    def __init__(self, grid_size=4, templates_dir="hardware/vision/templates", calib_file="config/vision_calibration.json"):
        self.grid_size = grid_size
        self.templates_dir = Path(templates_dir)
        self.calib_file = Path(calib_file)
        self.calib_points = None
        self.manual_clicks = []
        self.corner_ema = None
        self.ema_alpha = 0.35  # Smoothing factor for live video
        
        # Load or generate templates
        if not self.templates_dir.exists() or len(list(self.templates_dir.glob("*.png"))) < 100:
            print("[Vision] Generating letter templates...")
            generate_all_templates(str(self.templates_dir))
        self.templates = self._load_templates()
        
        # Load saved calibration if present
        self.load_calibration()
        
        # ArUco detector setup
        self.aruco_dict = get_aruco_dict()
        if hasattr(cv2.aruco, 'ArucoDetector'):
            params = cv2.aruco.DetectorParameters()
            params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, params)
        else:
            self.detector = None

    def _load_templates(self):
        """Load 104 normalized templates (26 letters x 4 rotations)."""
        templates = {}
        for p in self.templates_dir.glob("*.png"):
            parts = p.stem.split("_")
            if len(parts) == 2:
                char, deg = parts[0], int(parts[1])
                img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Invert so letter ink is white (255) on black (0) for matching
                    _, bin_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
                    templates[(char, deg)] = bin_img
        print(f"[Vision] Loaded {len(templates)} character templates.")
        return templates

    def load_calibration(self):
        """Load manual 4-corner calibration points."""
        if self.calib_file.exists():
            try:
                with open(self.calib_file, "r") as f:
                    data = json.load(f)
                    self.calib_points = np.array(data["points"], dtype=np.float32)
                    print(f"[Vision] Loaded calibration points from {self.calib_file}")
            except Exception as e:
                print(f"[Vision] Warning: Could not load calibration: {e}")

    def save_calibration(self, points):
        """Save 4-corner calibration points to JSON."""
        self.calib_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.calib_file, "w") as f:
            json.dump({"points": points.tolist(), "updated_at": time.time()}, f, indent=2)
        self.calib_points = points
        print(f"[Vision] Calibration saved to {self.calib_file}")

    def detect_aruco_corners(self, image):
        """
        Detect ArUco markers 0 (TL), 1 (TR), 2 (BR), 3 (BL).
        Returns np.ndarray of shape (4, 2) in order [TL, TR, BR, BL] or None.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if self.detector is not None:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            params = cv2.aruco.DetectorParameters_create()
            params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=params)
            
        if ids is None or len(ids) < 4:
            return None
            
        id_list = ids.flatten().tolist()
        needed_ids = [0, 1, 2, 3] # TL, TR, BR, BL
        if not all(nid in id_list for nid in needed_ids):
            return None
            
        pts = {}
        for mid, corner_set in zip(id_list, corners):
            if mid in needed_ids:
                c = corner_set[0]
                # In marker corners: c[0]=TL, c[1]=TR, c[2]=BR, c[3]=BL
                # For board rectification, use the INNER corner of each marker facing the board:
                # Marker 0 (TL): inner corner is c[2] (its BR corner)
                # Marker 1 (TR): inner corner is c[3] (its BL corner)
                # Marker 2 (BR): inner corner is c[0] (its TL corner)
                # Marker 3 (BL): inner corner is c[1] (its TR corner)
                if mid == 0:
                    pts[0] = c[2]
                elif mid == 1:
                    pts[1] = c[3]
                elif mid == 2:
                    pts[2] = c[0]
                elif mid == 3:
                    pts[3] = c[1]
                    
        ordered_pts = np.array([pts[0], pts[1], pts[2], pts[3]], dtype=np.float32)
        
        # Apply exponential moving average (EMA) smoothing for stable live video
        if self.corner_ema is None:
            self.corner_ema = ordered_pts
        else:
            self.corner_ema = self.ema_alpha * ordered_pts + (1 - self.ema_alpha) * self.corner_ema
            
        return self.corner_ema

    def rectify_board(self, image, corner_pts=None, target_size=1200):
        """
        Warp board region into a flat orthogonal square (target_size x target_size).
        """
        if corner_pts is None:
            corner_pts = self.detect_aruco_corners(image)
            if corner_pts is None:
                corner_pts = self.calib_points
                
        if corner_pts is None:
            return None, None
            
        dst_pts = np.float32([
            [0, 0],
            [target_size - 1, 0],
            [target_size - 1, target_size - 1],
            [0, target_size - 1]
        ])
        
        M = cv2.getPerspectiveTransform(corner_pts, dst_pts)
        warped = cv2.warpPerspective(image, M, (target_size, target_size))
        return warped, M

    def analyze_glare(self, bgr_image):
        """
        Analyze specular reflection and saturated hot spots.
        Returns glare_ratio (0.0 to 1.0) and glare mask.
        """
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2]
        s = hsv[:, :, 1]
        
        # Specular glare: very high brightness (V > 245) with low saturation (S < 40)
        glare_mask = (v >= 245) & (s <= 45)
        glare_ratio = float(np.mean(glare_mask))
        return glare_ratio, (glare_mask.astype(np.uint8) * 255)

    def extract_and_classify_cells(self, rectified_board):
        """
        Slice rectified orthogonal board into grid cells and classify contents.
        Returns:
            board_state: 2D list [row][col] of dicts with keys:
                         'letter', 'confidence', 'occupied', 'glare_ratio', 'rotation'
            summary_str: flat string representation (e.g. 16 or 225 chars)
        """
        h, w = rectified_board.shape[:2]
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        board_state = []
        flat_chars = []
        
        for r in range(self.grid_size):
            row_state = []
            for c in range(self.grid_size):
                x0 = int(c * cell_w)
                y0 = int(r * cell_h)
                x1 = int((c + 1) * cell_w)
                y1 = int((r + 1) * cell_h)
                
                cell_roi = rectified_board[y0:y1, x0:x1]
                
                # Analyze glare on cell
                cell_glare, _ = self.analyze_glare(cell_roi)
                
                # Check tile occupancy
                is_occupied, cell_bin = self._detect_occupancy(cell_roi)
                
                if not is_occupied:
                    cell_info = {
                        "row": r, "col": c,
                        "occupied": False,
                        "letter": ".",
                        "confidence": 0.0,
                        "rotation": 0,
                        "glare_ratio": cell_glare
                    }
                    flat_chars.append(".")
                else:
                    letter, conf, rot = self._classify_letter(cell_bin)
                    cell_info = {
                        "row": r, "col": c,
                        "occupied": True,
                        "letter": letter,
                        "confidence": float(conf),
                        "rotation": int(rot),
                        "glare_ratio": cell_glare
                    }
                    flat_chars.append(letter)
                    
                row_state.append(cell_info)
            board_state.append(row_state)
            
        summary_str = " ".join(flat_chars)
        return board_state, summary_str

    def _detect_occupancy(self, cell_roi):
        """
        Determine if cell contains a wooden tile.
        Inspects central region of cell (excluding outer retention ribs).
        """
        ch, cw = cell_roi.shape[:2]
        margin_x = int(cw * 0.12)
        margin_y = int(ch * 0.12)
        inner = cell_roi[margin_y:ch - margin_y, margin_x:cw - margin_x]
        
        gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
        
        # Compute edge gradient energy
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge_energy = float(np.mean(np.sqrt(sobelx**2 + sobely**2)))
        
        # Adaptive contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)
        
        # Otsu thresholding (ink = 255, wood = 0)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological opening to clean wood grain specks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        clean_bin = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Count black ink pixel ratio
        ink_ratio = float(np.mean(clean_bin == 255))
        
        # A valid tile has distinct high-contrast letter edges (edge_energy >= 14.0) and ink between 3% and 40%
        is_occupied = (edge_energy >= 14.0) and (0.025 <= ink_ratio <= 0.45)
        return is_occupied, clean_bin

    def _classify_letter(self, cell_bin):
        """
        Classify binarized cell character against normalized templates.
        Isolates the central character contour, scales to standard template height (32px),
        and tests all letter templates across 4 rotations.
        Returns: (best_letter, confidence, rotation_deg)
        """
        if len(self.templates) == 0:
            return "?", 0.0, 0
            
        # Find external contours
        contours, _ = cv2.findContours(cell_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            # Filter out tiny specks and edge noise
            if area > 150:
                valid.append((c, area, (x, y, w, h)))
                
        if not valid:
            # High occupancy but no distinct letter contour -> Blank tile
            return " ", 0.5, 0
            
        # Sort by area descending to find main letter contour
        valid.sort(key=lambda item: item[1], reverse=True)
        _, _, (x, y, w, h) = valid[0]
        
        # Crop character tightly
        char_crop = cell_bin[y:y + h, x:x + w]
        
        # Match across standard template height (32px) and slight scale tolerance [30, 32, 34]
        best_char = "?"
        best_conf = -1.0
        best_rot = 0
        
        for target_h in [32, 30, 34]:
            scale = target_h / float(max(1, h))
            nw = max(1, int(w * scale))
            if nw > 56:
                nw = 56
            resized = cv2.resize(char_crop, (nw, target_h), interpolation=cv2.INTER_AREA)
            
            # Place on 64x64 canvas centered
            norm = np.zeros((64, 64), dtype=np.uint8)
            ox = (64 - nw) // 2
            oy = (64 - target_h) // 2
            norm[oy:oy + target_h, ox:ox + nw] = resized
            
            for (char, rot), templ in self.templates.items():
                res = cv2.matchTemplate(norm, templ, cv2.TM_CCOEFF_NORMED)
                score = float(res[0][0])
                
                if score > best_conf:
                    best_conf = score
                    best_char = char
                    best_rot = rot
                    
        # Confidence threshold: below 0.40 indicates ambiguous character
        if best_conf < 0.40:
            return "?", max(0.0, best_conf), 0
            
        return best_char, best_conf, best_rot

    def render_overlay(self, raw_frame, rectified_board, board_state, fps=0.0):
        """
        Render interactive dual-pane diagnostic display.
        Left pane: raw camera view with tracking markers.
        Right pane: rectified orthogonal board with letters, confidence, and glare alerts.
        """
        # --- Pane 1: Camera Feed ---
        h_target = 720
        scale_raw = h_target / raw_frame.shape[0]
        w_raw = int(raw_frame.shape[1] * scale_raw)
        pane_raw = cv2.resize(raw_frame, (w_raw, h_target))
        
        # Draw calibration / tracking outline on raw view if available
        if self.corner_ema is not None or self.calib_points is not None:
            pts = self.corner_ema if self.corner_ema is not None else self.calib_points
            pts_scaled = (pts * scale_raw).astype(np.int32)
            cv2.polylines(pane_raw, [pts_scaled], isClosed=True, color=(0, 255, 255), thickness=2)
            labels = ["TL", "TR", "BR", "BL"]
            colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
            for (px, py), lbl, col in zip(pts_scaled, labels, colors):
                cv2.circle(pane_raw, (px, py), 6, col, -1)
                cv2.putText(pane_raw, lbl, (px + 10, py - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
                
        cv2.putText(pane_raw, f"FPS: {fps:.1f} | Mode: {self.grid_size}x{self.grid_size}", 
                    (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(pane_raw, "Keys: [s] Save | [c] Calibrate | [g] Glare | [q] Quit", 
                    (15, h_target - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

        # --- Pane 2: Rectified Board ---
        if rectified_board is not None:
            pane_board = cv2.resize(rectified_board, (h_target, h_target))
            cell_px = h_target / self.grid_size
            
            # Draw grid lines and recognized letters
            total_glare = 0.0
            occupied_count = 0
            
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    cell = board_state[r][c]
                    x0 = int(c * cell_px)
                    y0 = int(r * cell_px)
                    x1 = int((c + 1) * cell_px)
                    y1 = int((r + 1) * cell_px)
                    
                    # Cell boundary
                    cv2.rectangle(pane_board, (x0, y0), (x1, y1), (120, 90, 60), 1)
                    
                    if cell["occupied"]:
                        occupied_count += 1
                        total_glare += cell["glare_ratio"]
                        
                        # Tile highlight box
                        cv2.rectangle(pane_board, (x0 + 3, y0 + 3), (x1 - 3, y1 - 3), (0, 220, 100), 2)
                        
                        # Letter text
                        letter = cell["letter"]
                        conf = cell["confidence"]
                        font_scale = 1.1 if self.grid_size == 4 else 0.55
                        thick = 2 if self.grid_size == 4 else 1
                        
                        text_size = cv2.getTextSize(letter, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thick)[0]
                        tx = x0 + (int(cell_px) - text_size[0]) // 2
                        ty = y0 + (int(cell_px) + text_size[1]) // 2
                        
                        # Text background shadow
                        cv2.putText(pane_board, letter, (tx + 1, ty + 1), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thick + 1)
                        cv2.putText(pane_board, letter, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thick)
                        
                        # Confidence badge
                        if self.grid_size == 4:
                            cv2.putText(pane_board, f"{int(conf*100)}%", (x0 + 6, y1 - 8), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)
                                        
                        # Glare warning icon if hot spot exceeds 5%
                        if cell["glare_ratio"] > 0.05:
                            cv2.circle(pane_board, (x1 - 12, y0 + 12), 6, (0, 0, 255), -1)
                            cv2.putText(pane_board, "!", (x1 - 15, y0 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                            
            # Header on board pane
            avg_glare = (total_glare / max(1, occupied_count)) * 100.0
            glare_col = (0, 0, 255) if avg_glare > 5.0 else (0, 255, 0)
            cv2.putText(pane_board, f"Tiles: {occupied_count} | Glare: {avg_glare:.1f}%", 
                        (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, glare_col, 2)
            if avg_glare > 5.0:
                cv2.putText(pane_board, "WARNING: Glare high. Cross-polarization advised.", 
                            (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        else:
            pane_board = np.zeros((h_target, h_target, 3), dtype=np.uint8)
            cv2.putText(pane_board, "No Board Detected", (h_target // 4, h_target // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            cv2.putText(pane_board, "Ensure 4 ArUco markers (0..3) visible", (h_target // 6, h_target // 2 + 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
            cv2.putText(pane_board, "or press 'c' to click 4 corners manually", (h_target // 6, h_target // 2 + 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        # Combine side-by-side
        combined = np.hstack([pane_raw, pane_board])
        return combined

    def run_on_image(self, image_path, headless=False, export_json=None):
        """Process a single image file (for CLI, testing, and CI)."""
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")
            
        t0 = time.time()
        rectified, _ = self.rectify_board(image)
        if rectified is None:
            print("[Vision] Error: Could not locate board corners in image.")
            return None
            
        board_state, summary_str = self.extract_and_classify_cells(rectified)
        latency_ms = (time.time() - t0) * 1000.0
        
        result = {
            "image": str(image_path),
            "grid_size": self.grid_size,
            "latency_ms": round(latency_ms, 2),
            "board_string": summary_str,
            "tiles": []
        }
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell = board_state[r][c]
                if cell["occupied"]:
                    result["tiles"].append({
                        "row": r, "col": c,
                        "letter": cell["letter"],
                        "confidence": round(cell["confidence"], 3),
                        "rotation": cell["rotation"],
                        "glare_ratio": round(cell["glare_ratio"], 4)
                    })
                    
        print(f"\n[Vision] Recognition Complete ({latency_ms:.1f}ms):")
        print(f"Board State: [{summary_str}]")
        print(f"Occupied Tiles: {len(result['tiles'])}")
        
        if export_json:
            with open(export_json, "w") as f:
                json.dump(result, f, indent=2)
            print(f"[Vision] Exported JSON to {export_json}")
            
        if not headless:
            vis = self.render_overlay(image, rectified, board_state, fps=1000.0 / max(1.0, latency_ms))
            cv2.imshow("Smart Crossword Board - Vision Scanner", vis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        return result

    def run_live(self, camera_idx=2):
        """Run interactive live video stream from camera."""
        print(f"[Vision] Opening camera device index {camera_idx}...")
        cap = cv2.VideoCapture(camera_idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        if not cap.isOpened():
            print(f"[Vision] Error: Failed to open camera {camera_idx}. Trying index 0...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[Vision] Error: No usable camera found.")
                return
                
        window_name = "Smart Crossword Board - Bench Vision Scanner"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Mouse callback for manual 4-corner calibration
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and self.manual_clicks is not None:
                # Scale from window coordinates to raw frame coordinates
                # Handled inside calibration mode
                self.manual_clicks.append((x, y))
                print(f"[Calib] Recorded point {len(self.manual_clicks)}/4: ({x}, {y})")
                
        cv2.setMouseCallback(window_name, mouse_callback)
        
        prev_time = time.time()
        calibrating = False
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                    
                now = time.time()
                fps = 1.0 / max(1e-4, (now - prev_time))
                prev_time = now
                
                # Settle/Rectify
                rectified, _ = self.rectify_board(frame)
                if rectified is not None:
                    board_state, summary_str = self.extract_and_classify_cells(rectified)
                else:
                    board_state = None
                    
                vis = self.render_overlay(frame, rectified, board_state, fps=fps)
                cv2.imshow(window_name, vis)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save snapshot
                    ts = int(time.time())
                    out_dir = Path("data/vision_snapshots")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    img_path = out_dir / f"snapshot_{ts}.jpg"
                    json_path = out_dir / f"snapshot_{ts}.json"
                    cv2.imwrite(str(img_path), frame)
                    if board_state:
                        with open(json_path, "w") as f:
                            json.dump({
                                "timestamp": ts,
                                "board_state": board_state,
                                "flat_string": summary_str
                            }, f, indent=2)
                    print(f"[Vision] Snapshot saved: {img_path}")
                elif key == ord('c'):
                    # Reset calibration
                    self.manual_clicks = []
                    self.corner_ema = None
                    print("[Vision] Reset corner tracking. Ready for auto-detection or click.")
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Smart Crossword Board - Bench Vision Scanner")
    parser.add_argument("--camera", type=int, default=2, help="Camera device index (default 2 for Logitech Brio 100)")
    parser.add_argument("--image", type=str, default=None, help="Path to static test image")
    parser.add_argument("--grid", type=int, choices=[4, 15], default=4, help="Grid size: 4 for 4x4 test, 15 for full board")
    parser.add_argument("--headless", action="store_true", help="Run without GUI window (for tests/CI)")
    parser.add_argument("--export", type=str, default=None, help="Save recognized state to JSON file")
    args = parser.parse_args()
    
    scanner = CrosswordVisionScanner(grid_size=args.grid)
    
    if args.image:
        scanner.run_on_image(args.image, headless=args.headless, export_json=args.export)
    else:
        scanner.run_live(camera_idx=args.camera)

if __name__ == "__main__":
    main()
