# KiCad Learning Guide for EasyEDA Users

Transitioning from EasyEDA (Standard or Pro) to KiCad 8/9/10 involves moving from a browser-first, cloud-managed EDA tool to a high-precision, open-source desktop engineering suite with full programmatic control.

This guide explains the architectural and workflow differences, using the **Smart Crossword Board ST25R3916B 4x4 NFC Matrix** PCB as a concrete, real-world case study.

---

## 1. Core Architectural Differences

| Feature | EasyEDA (Standard / Pro) | KiCad (v8, v9, v10) |
| :--- | :--- | :--- |
| **Storage & Project Model** | Cloud database with proprietary JSON export. Single monolithic design file or web project. | Plain text files with S-expression syntax (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`). Fully version-controllable via Git. |
| **Library Management** | Integrated LCSC / EasyEDA cloud library. Symbol, footprint, and 3D model are bundled together. | Decoupled model: Symbols (`.kicad_sym`) and Footprints (`.pretty` directories of `.kicad_mod`) are independent. |
| **Routing & DRC Engine** | Server-side or client-side web GL router. Tolerant DRC; allows minor overlap unless strictly flagged. | High-precision geometry kernel with Push-and-Shove router. Strict DRC; exact tolerances down to nanometers (internal nm integer units). |
| **Scriptability** | JavaScript extension API running inside browser sandbox. Limited batch execution. | Native C++ core with complete Python 3 SWIG bindings (`pcbnew`) and headless CLI (`kicad-cli`). |

---

## 2. Decoupled Symbols and Footprints

In EasyEDA, placing a component (e.g., from LCSC) places the exact physical footprint linked to the part number immediately.

In KiCad:
1. **Schematic (`.kicad_sch`)**: You place an electrical symbol (e.g., `Device:R` or `Device:C`).
2. **Footprint Assignment**: You assign a footprint (e.g., `Resistor_SMD:R_0603_1608Metric`).
3. **Netlist Sync**: You update the PCB from schematic (`Tools -> Update PCB from Schematic` or `F8`).

### Why this matters for engineering:
- You can tune component footprints (e.g., expanding pad hand-soldering margins or switching from 0603 to 0805) without altering schematic connections.
- Parameterized design generators can create thousands of pads and tracks algorithmically without touching the GUI.

---

## 3. Planar Coils and Net Ties (Solving Short-Circuit DRCs)

In RF and NFC design, a planar spiral coil is physically a continuous copper track on the PCB, but electrically it bridges two distinct schematic nets:
- **Net 1**: The driven RF signal (`RF_CH0` or `RF_COIL_1`)
- **Net 2**: Ground (`GND`)

### The EasyEDA Approach
EasyEDA allows drawing copper tracks between two pads of different nets if you disable DRC checking or mark them as "Short". However, this often results in broken polygon pours or accidental shorts during auto-routing.

### The KiCad Standard Approach: Net Ties
In KiCad, you define a **Net Tie** footprint:
1. In the footprint definition (`.kicad_mod`), set `(net_tie_pad_groups "1, 2")`.
2. In Python scripting:
   ```python
   fp.AddNetTiePadGroup("1, 2")
   ```
3. When the DRC engine encounters pad 1 and pad 2 connected together by copper, it recognizes the explicit Net Tie rule and does **not** flag a short-circuit violation.
4. The rest of the board continues to enforce strict net-to-net clearance rules everywhere else.

---

## 4. Multi-Layer Stackup and RF Ground Cutouts

For the 4-layer Smart Crossword Board:
- **Layer 1 (`F.Cu`)**: Top components, planar antenna coils, tuning capacitor tanks, multiplexer, and transceiver IC.
- **Layer 2 (`In1.Cu`)**: Solid ground plane (`GND`) with **Rule Area cutouts**.
- **Layer 3 (`In2.Cu`)**: Monotonic SPI digital bus + power routing.
- **Layer 4 (`B.Cu`)**: Bottom ground shield plane + multiplexer address select routing.

### Preventing Eddy Current Loss in In1.Cu
If a solid copper ground plane sits directly under a 13.56 MHz antenna coil, the alternating magnetic field induces circular eddy currents in the plane. These eddy currents generate a counter-magnetic field (Lenz's Law), drastically reducing antenna inductance ($L$) and dropping the quality factor ($Q$).

To prevent this:
1. Create a **Keepout / Rule Area Zone** directly underneath each antenna coil on `In1.Cu`.
2. Configure the zone to allow tracks and vias if necessary, but strictly **disallow copper zone fills**:
   ```python
   cutout = pcbnew.ZONE(board)
   cutout.SetLayer(pcbnew.In1_Cu)
   cutout.SetIsRuleArea(True)
   cutout.SetDoNotAllowZoneFills(True)
   cutout.SetDoNotAllowTracks(False)
   cutout.SetDoNotAllowVias(False)
   ```
3. This creates a copper-free window under the 19mm coil while maintaining solid ground return paths around the periphery.

---

## 5. Python Automation with `pcbnew`

EasyEDA requires manual point-and-click placement or JavaScript plugins. KiCad includes a complete Python environment (`pcbnew`).

### Basic Script Structure
```python
import pcbnew

# 1. Initialize empty board
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)

# 2. Add Net
net_gnd = pcbnew.NETINFO_ITEM(board, "/GND")
board.Add(net_gnd)

# 3. Place Footprint
fp = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp.SetReference("R1")
fp.SetPosition(pcbnew.VECTOR2I_MM(20.0, 30.0))
board.Add(fp)

# 4. Route Track
track = pcbnew.PCB_TRACK(board)
track.SetLayer(pcbnew.F_Cu)
track.SetStart(pcbnew.VECTOR2I_MM(20.0, 30.0))
track.SetEnd(pcbnew.VECTOR2I_MM(25.0, 30.0))
track.SetWidth(int(0.20 * 1e6)) # Internal units are nanometers
track.SetNet(net_gnd)
board.Add(track)

# 5. Save Board
board.Save("output.kicad_pcb")
```

### Critical Python 3.14 Iterator Gotcha
In Python 3.14+, iterating over SWIG-wrapped KiCad collections (like `board.Tracks()` or `board.Footprints()`) using a standard `for x in board.Tracks():` loop throws an `AttributeError: 'SwigPyIterator' object has no attribute 'next'`.

**The Invariant Solution**: Always index the collection explicitly:
```python
tracks = board.Tracks()
for i in range(len(tracks)):
    t = tracks[i]
    # process track
```

---

## 6. Manufacturing Deliverables for JLCPCB

EasyEDA offers a single button: "Generate Fabrication Data (Gerber) / SMT". In KiCad, you generate standard industry files using `kicad-cli` or custom Python scripts.

### 1. Gerbers and Drill Files
Use the headless command-line interface:
```bash
# Export Gerbers
kicad-cli pcb export gerbers \
  -o gerbers/ \
  --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask \
  board.kicad_pcb

# Export Excellon Drill Files
kicad-cli pcb export drill \
  -o gerbers/ \
  --format excellon \
  --excellon-units mm \
  --excellon-zeros-format decimal \
  board.kicad_pcb
```

### 2. BOM (Bill of Materials)
JLCPCB requires a CSV with columns: `Comment,Designator,Footprint,LCSC Part #,Quantity`.
- Group components by value and footprint.
- Include explicit LCSC part numbers (e.g. `C2943312` for ST25R3916B-AQFT, `C109598` for CD74HC4067M) so JLCPCB SMT parts matching is 100% automated.

### 3. CPL (Component Placement List / Pick & Place)
JLCPCB requires: `Designator,Mid X,Mid Y,Layer,Rotation`.
- **Coordinate Origin**: JLCPCB requires coordinates matching the board origin. Ensure $Y$ coordinates match top-left or specified origin.
- **Rotation Differences**: KiCad component rotation conventions occasionally differ by 90° or 180° from JLCPCB reel orientations. Preview the board in JLCPCB's online DFM 3D viewer before placing an order to confirm diode and IC Pin 1 orientations.

---

## Summary Checklist for EasyEDA Migrators
1. **Never edit files in word processors**: Use `.kicad_sch` and `.kicad_pcb` with KiCad tools or Git.
2. **Run DRC regularly**: KiCad catches millimeter fractions that web tools forgive.
3. **Use Net Ties** whenever deliberately connecting two different RF or ground nets on copper.
4. **Automate repetitive matrices**: Use Python scripts to generate arrays of coils and tuning networks with 0 layout drift.
