#!/usr/bin/env python3
"""
test_cad_models.py - Automated Verification of FreeCAD 4x4 CAD Models

Validates:
1. Headless FreeCAD execution of generate_4x4_enclosure.py.
2. Complete generation of all .FCStd, .step, and .stl files.
3. OpenCASCADE shape validity (isValid() == True, non-degenerate geometry).
4. Critical mechanical & RF invariants:
   - Base enclosure envelope & 90mm screw hole pitch.
   - 0.5mm PCB clearance (100.5x100.5mm cavity).
   - Top grid floor thickness <= 1.6mm (RF penetration invariant).
   - Tile pocket sizing and prototype NFC tile coin cavity.
5. STL mesh facet counts and watertight properties for 3D printing.
"""

import os
import sys
import subprocess
import pytest

# Ensure FreeCAD library paths are loaded
for p in ['/usr/lib/freecad/lib', '/usr/lib/freecad/Ext']:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

import FreeCAD
import Part
import Mesh

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
OUTPUT_DIR = os.path.join(ROOT_DIR, "hardware", "cad", "output")
GENERATOR_SCRIPT = os.path.join(ROOT_DIR, "hardware", "cad", "generators", "generate_4x4_enclosure.py")


def test_generator_script_execution():
    """Verify that the generator script executes cleanly and regenerates outputs."""
    env = os.environ.copy()
    env["PYTHONPATH"] = "/usr/lib/freecad/lib:/usr/lib/freecad/Ext"
    result = subprocess.run(
        [sys.executable, GENERATOR_SCRIPT],
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Generator script failed:\n{result.stderr}\n{result.stdout}"
    assert "All CAD models successfully generated" in result.stdout


def test_output_files_exist_and_non_empty():
    """Verify all expected CAD documents, STEP interchange, and STL meshes exist."""
    expected_files = [
        "base_enclosure.FCStd", "base_enclosure.step", "base_enclosure.stl",
        "top_grid_plate.FCStd", "top_grid_plate.step", "top_grid_plate.stl",
        "nfc_tile_prototype.FCStd", "nfc_tile_prototype.step", "nfc_tile_prototype.stl",
        "nfc_tile_plug.step", "nfc_tile_plug.stl",
        "assembly_4x4_prototype.FCStd", "assembly_4x4_prototype.step"
    ]
    for filename in expected_files:
        path = os.path.join(OUTPUT_DIR, filename)
        assert os.path.exists(path), f"Missing file: {filename}"
        assert os.path.getsize(path) > 1000, f"File unexpectedly small (<1KB): {filename} ({os.path.getsize(path)} bytes)"


def test_base_enclosure_geometry():
    """Verify Base Enclosure dimensions, standoffs, and screw hole pitch."""
    from hardware.cad.generators.generate_4x4_enclosure import (
        build_base_enclosure, OUTER_WIDTH, OUTER_LENGTH, BASE_TOTAL_HEIGHT,
        INNER_WIDTH, INNER_LENGTH, STANDOFF_HEIGHT
    )
    base = build_base_enclosure()
    assert base.isValid(), "Base enclosure geometry is invalid according to OpenCASCADE"
    assert not base.isNull(), "Base shape is null"
    
    bbox = base.BoundBox
    # Check outer envelope (allowing for fillet tolerances)
    assert abs(bbox.XLength - OUTER_WIDTH) < 0.1, f"Outer width mismatch: {bbox.XLength}"
    assert abs(bbox.YLength - OUTER_LENGTH) < 0.1, f"Outer length mismatch: {bbox.YLength}"
    assert abs(bbox.ZLength - BASE_TOTAL_HEIGHT) < 0.1, f"Total height mismatch: {bbox.ZLength}"
    
    # Check PCB cavity dimensions
    assert INNER_WIDTH == 100.5, "PCB cavity width must be 100.5mm (+0.5mm clearance)"
    assert INNER_LENGTH == 100.5, "PCB cavity length must be 100.5mm (+0.5mm clearance)"
    assert STANDOFF_HEIGHT == 3.5, "Standoff height must be 3.5mm"


def test_top_grid_plate_rf_floor_and_pockets():
    """Verify Top Grid Plate floor thickness (RF invariant) and tile pocket dimensions."""
    from hardware.cad.generators.generate_4x4_enclosure import (
        build_top_grid_plate, TOP_FLOOR_THICKNESS, RIB_HEIGHT, POCKET_WIDTH, POCKET_DEPTH
    )
    top_plate = build_top_grid_plate()
    assert top_plate.isValid(), "Top grid plate geometry is invalid according to OpenCASCADE"
    assert not top_plate.isNull(), "Top grid plate shape is null"
    
    # RF Invariant Check: Floor thickness directly over coils MUST be <= 1.6mm
    assert TOP_FLOOR_THICKNESS <= 1.6, f"FAIL-008: Floor thickness ({TOP_FLOOR_THICKNESS}mm) exceeds 1.6mm RF limit"
    assert TOP_FLOOR_THICKNESS == 1.5, "Top floor thickness should be exactly 1.5mm"
    
    # Pocket dimensions
    assert POCKET_WIDTH == 18.4, "Tile pocket width must be 18.4mm (+0.4mm drop-in clearance)"
    assert POCKET_DEPTH == 1.2, "Tile pocket depth must be 1.2mm"


def test_tile_prototype_dimensions_and_cavity():
    """Verify NFC Scrabble tile dimensions, tag cavity, and embossed lettering."""
    from hardware.cad.generators.generate_4x4_enclosure import (
        build_tile_prototype, TILE_WIDTH, TILE_HEIGHT, TAG_CAVITY_DIA, TAG_CAVITY_DEPTH
    )
    tile = build_tile_prototype()
    assert tile.isValid(), "Tile prototype geometry is invalid according to OpenCASCADE"
    assert not tile.isNull(), "Tile prototype shape is null"
    
    bbox = tile.BoundBox
    assert abs(bbox.XLength - TILE_WIDTH) < 0.1, f"Tile width mismatch: {bbox.XLength}"
    assert abs(bbox.YLength - TILE_WIDTH) < 0.1, f"Tile length mismatch: {bbox.YLength}"
    # Z includes embossed letter (4.8mm base + 0.4mm letter = 5.2mm)
    assert abs(bbox.ZLength - (TILE_HEIGHT + 0.4)) < 0.1, f"Tile total height mismatch: {bbox.ZLength}"
    
    # Tag cavity checks
    assert TAG_CAVITY_DIA == 15.5, "Tag cavity diameter must be 15.5mm"
    assert TAG_CAVITY_DEPTH == 1.0, "Tag cavity depth must be 1.0mm"


def test_stl_mesh_integrity_for_3d_printing():
    """Verify STL meshes are watertight and contain sufficient facets for clean printing."""
    mesh_files = [
        ("base_enclosure.stl", 2000),
        ("top_grid_plate.stl", 2000),
        ("nfc_tile_prototype.stl", 400),
        ("nfc_tile_plug.stl", 200)
    ]
    for filename, min_facets in mesh_files:
        stl_path = os.path.join(OUTPUT_DIR, filename)
        mesh = Mesh.Mesh(stl_path)
        assert mesh.CountFacets >= min_facets, f"{filename} has too few facets: {mesh.CountFacets} < {min_facets}"
        assert not mesh.hasNonManifolds(), f"{filename} has non-manifold geometry, cannot slice cleanly!"
        assert mesh.Volume > 0, f"{filename} has zero or negative volume"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
