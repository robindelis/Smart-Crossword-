# Phase 1: 4x4 Prototype CAD Models & 3D Printing Guide

## 1. Overview
This directory contains the 3D mechanical CAD design for the Smart Crossword Board 4x4 test vehicle. It houses the 100mm × 100mm 4-layer KiCad PCB, provides senior-ergonomic tile retention, exposes bench test wiring headers, and includes 3D-printable prototype NFC Scrabble tiles.

All models are generated parametrically via headless FreeCAD automation (`generators/generate_4x4_enclosure.py`).

---

## 2. Components & Specifications

### A. Base Enclosure Tray (`output/base_enclosure.*`)
* **Outer Footprint**: 105.5 mm × 105.5 mm × 8.6 mm (3.0mm rounded corners).
* **PCB Pocket**: 100.5 mm × 100.5 mm with 4x M3 corner standoffs (3.5mm height) providing bottom clearance for through-hole connector pins.
* **Screw Mounting**: 4x M3 through-holes at 90.0mm center-to-center pitch, with flush counterbores on the underside.
* **Connector Access**:
  * North wall slot for J1 (2x10 Host ribbon / DuPont jumper cables).
  * North wall slot for J2 (1x10 NFC transceiver breakout header).
  * East wall slot for J3 (SMA RF test port for coaxial cable).
* **Base Stability**: 4x recessed circular pockets for 8.0mm non-slip rubber bumper pads.

### B. Top Playing Faceplate (`output/top_grid_plate.*`)
* **Grid Layout**: 4x4 matrix of raised divider ribs (1.2mm rib height, 0.6mm thickness).
* **Tile Pockets**: 16 pockets sized 18.4 mm × 18.4 mm (+0.4mm drop-in clearance).
* **RF Floor Thickness**: **1.5 mm solid floor** directly above the 16 antenna coils ($\le 1.6\text{mm}$ RF invariant).
* **Wiring Window**: Top-access opening (85mm × 19mm) exposing headers J1, J2, and J3 for fast bench probing without disassembly.
* **Alignment**: Integrated bottom registration rim that mates snugly into the base enclosure lip.

### C. Prototype NFC Scrabble Letter Tile (`output/nfc_tile_prototype.*`)
* **Dimensions**: 18.0 mm × 18.0 mm × 4.8 mm.
* **Internal Tag Cavity**: 15.5 mm diameter × 1.0 mm deep bottom cavity housing standard NTAG213/NTAG215 coin tags or wet inlays.
* **Retention Plug**: Includes snap/press-fit bottom disc (`output/nfc_tile_plug.stl`).
* **Tactile Top**: 0.4mm embossed letter "A" and subscript score "1", with 0.6mm filleted top edges.

### D. Complete Assembly (`output/assembly_4x4_prototype.*`)
* Master 3D assembly including Base Tray, 100x100mm PCB mockup, Top Grid Plate, and 16 letter tiles in `.FCStd` and `.step` format.

---

## 3. 3D Printing Guide (FDM PLA / PETG)

| Setting | Recommended Value | Notes |
| :--- | :--- | :--- |
| **Material** | PLA or PETG | Classical PLA is rigid and prints with tight tolerances. |
| **Nozzle Size** | 0.4 mm | Standard nozzle. |
| **Layer Height** | 0.20 mm | 1.5mm RF floor equals exactly 7–8 solid layers. |
| **Infill** | 20% Gyroid or Grid | Provides rigid support under finger pressure. |
| **Perimeters** | 3 to 4 walls | Ensures solid screw bosses and rib walls. |
| **Supports** | None required | All features designed with 3D-printing overhang rules. |
| **Build Plate** | Textured PEI | Gives a warm, non-glare surface finish on the base. |

---

## 4. Hardware Assembly Bill of Materials (BOM)

| Item | Quantity | Description |
| :--- | :--- | :--- |
| **M3 × 12mm Screws** | 4 | Button head or socket head cap screws (DIN 912 / ISO 7380). |
| **M3 Hex Nuts** | 4 | Standard M3 hex nuts (or M3 threaded brass heat-set inserts). |
| **Rubber Bumper Feet** | 4 | 8mm × 1.5mm self-adhesive silicone/rubber pads (3M Bumpon). |
| **NFC Coin Tags** | 16 | NTAG213 or NTAG215 15mm–18mm circular tags. |

---

## 5. How to View & Regenerate Models

### Viewing in FreeCAD GUI
1. Launch FreeCAD from your application menu or run:
   ```bash
   freecad hardware/cad/output/assembly_4x4_prototype.FCStd
   ```
2. Press **0** (Isometric View) or **V, B** (Fit All) to inspect the 3D assembly.

### Regenerating CAD Models via CLI
Run the headless Python generator:
```bash
PYTHONPATH=/usr/lib/freecad/lib:/usr/lib/freecad/Ext python3 hardware/cad/generators/generate_4x4_enclosure.py
```
All `.FCStd`, `.step`, and `.stl` files in `output/` will be updated and validated automatically.
