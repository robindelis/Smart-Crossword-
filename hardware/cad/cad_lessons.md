# Living Memory: CAD & 3D Printing Automation Lessons

This document records technical invariants, mechanical design rules, OpenCASCADE/FreeCAD automation behaviors, and 3D printing tolerances discovered during development of the Smart Crossword Board.

m backing that holds tiles tightly in place so an in-progress ga---

## 1. FreeCAD Headless Automation Invariants

* **LESSON-CAD-001 (Headless Python Environment)**:
  * Running `freecadcmd -c "<multi-line>"` can terminate unexpectedly in headless console mode when complex scripts or argument flags are passed.
  * *Reliable Mitigation*: Execute standard Python with FreeCAD module paths:
    ```bash
    PYTHONPATH=/usr/lib/freecad/lib:/usr/lib/freecad/Ext python3 <script.py>
    ```
    This directly loads the OpenCASCADE B-Rep engine (`FreeCAD`, `Part`, `Mesh`, `MeshPart`) without GUI overhead, Wayland/X11 dependencies, or interactive prompt crashes.

* **LESSON-CAD-002 (B-Rep Constructive Solid Geometry over GUI Sketches)**:
  * Headless FreeCAD scripts that rely on the `PartDesign` workbench and parametric sketches frequently suffer from topological naming instability when parameters change.
  * *Reliable Mitigation*: Use direct CSG (Constructive Solid Geometry) with `Part.makeBox()`, `Part.makeCylinder()`, `Part.makeFillet()`, `shape.fuse()`, and `shape.cut()`. This guarantees 100% deterministic, idempotent geometry generation across parameter ranges.

* **LESSON-CAD-003 (Shape Integrity & Manifold Verification)**:
  * Incomplete boolean operations or coplanar coincident faces can create non-manifold geometry that slices poorly in 3D slicers.
  * *Rule*: Always execute `shape.isValid()` and verify that no self-intersecting shells exist before committing or exporting models. When cutting holes, extend cutting cylinders slightly past the boundary faces (e.g. `z_offset = -0.5`, `height = target_height + 1.0`) to avoid zero-thickness degenerate boundaries.

* **LESSON-CAD-004 (High-Resolution STL Tessellation)**:
  * Default STL export via basic mesh conversion can produce visible facets on cylindrical screw holes and rounded corners.
  * *Mitigation*: Use OpenCASCADE deflection-based meshing (`MeshPart.meshFromShape(shape, LinearDeflection=0.05, AngularDeflection=0.1745)`) to generate smooth, watertight 3D print meshes.

---

## 2. 3D Printing & Mechanical Tolerances (FDM PLA / PETG)

* **LESSON-CAD-005 (PCB Cavity Fitment Clearance)**:
  * Standard 1.6mm FR4 PCBs have manufacturing cutting tolerances ($\pm 0.1\text{mm}$) and FDM perimeters expand outward by ~0.15mm–0.2mm per side.
  * *Tolerance Invariant*: Design the PCB seating cavity with **+0.5mm total clearance** (100.5mm x 100.5mm for a 100.0mm x 100.0mm board). This ensures drop-in fitment without hand-filing.

* **LESSON-CAD-006 (Tile Pocket Sizing for Senior Ergonomics)**:
  * Standard wooden Scrabble tiles measure $19.0\text{mm} \times 19.0\text{mm} \times 4.8\text{mm}$.
  * If the tile pocket is $< 19.3\text{mm}$, friction and corner radius buildup cause tiles to jam when inserted at slight angles by older players.
  * *Ergonomic Invariant*: Set pocket size to **$19.4\text{mm} \times 19.4\text{mm}$** (+0.4mm clearance). Rib height is set to **$1.2\text{mm}$** (retains tiles firmly during board rotation without blocking visual letters or fingernail grip).

* **LESSON-CAD-007 (RF Floor Thickness)**:
  * 13.56 MHz RFID magnetic near-field coupling decreases rapidly with vertical separation ($H \propto 1/z^3$).
  * *Electrical Invariant*: The solid plastic floor between the PCB antenna array and the bottom of the letter tiles MUST NOT exceed **$1.6\text{mm}$** (8 layers at 0.2mm layer height). A 1.5mm floor provides robust structural integrity against finger tapping while maintaining excellent tag read sensitivity.

* **LESSON-CAD-008 (M3 Mounting Hardware Clearance)**:
  * Holes modeled at exactly 3.0mm in CAD will print undersized (~2.8mm) due to nozzle hole shrinking.
  * *Rule*: For free-slip clearance holes, model at **$\varnothing 3.2\text{mm}$**. For direct plastic thread-forming holes, model at **$\varnothing 2.85\text{mm}$**. Standoff height below the PCB must be at least **$3.5\text{mm}$** to clear through-hole pins from J1 and J2 headers.

* **LESSON-CAD-009 (Pure Headless vs GUI Module Dependencies)**:
  * In FreeCAD, modules such as `Draft` and `PartDesign` depend internally on `PySide6` / Qt GUI bindings, which may fail in standard headless server or CLI Python environments with `ModuleNotFoundError: No module named 'PySide6'`.
  * *Rule*: For headless CI/CD and CLI automation scripts, use `FreeCAD`, `Part`, `Mesh`, and `MeshPart` exclusively. These C++ core modules interact directly with OpenCASCADE and have zero Qt or window-system dependencies.

* **LESSON-CAD-010 (STEP Export Entity Invariant)**:
  * Calling `Part.export([shape], path)` with a raw `Part.Shape` instance outputs only an empty STEP protocol header (~1.7 KB) with zero geometry definitions.
  * *Rule*: Always pass FreeCAD Document Feature objects (`doc.addObject('Part::Feature', ...)`) into `Part.export([obj], path)`. This writes full STEP boundary representations with valid solid topology.

* **LESSON-CAD-011 (Coil Pitch vs Tile Retention Rib Spacing)**:
  * Traditional cardboard Scrabble boards have tiles touching edge-to-edge on 19.0mm squares. With physical 3D-printed or molded retention ribs, the rib thickness (0.6mm–1.0mm) must be accounted for.
  * For the 4x4 prototype, the 19.0mm coil pitch is matched 1:1 by 18.0mm tiles in 18.4mm pockets with 0.6mm divider ribs ($18.4 + 0.6 = 19.0\text{mm}$).
  * For full-sized 19.0mm Scrabble tiles, either corner alignment cross-pins are used, or the grid pitch is expanded to 20.0mm (which remains well within the 17.5mm coil's expanded magnetic field).

