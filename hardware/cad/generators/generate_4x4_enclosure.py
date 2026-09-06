#!/usr/bin/env python3
"""
generate_4x4_enclosure.py - Parametric FreeCAD Automation for Smart Crossword Board 4x4 Prototype

Automates the creation of 3D-printable enclosures and NFC letter tiles:
1. Base Enclosure Tray: Houses 100x100mm 4-layer PCB with M3 screw bosses and header cutouts.
2. Top Grid Faceplate: 4x4 raised retention ribs (1.2mm tall) with 1.5mm RF floor directly over antenna coils.
3. NFC Letter Tile: 18.0x18.0x4.8mm tile with internal cavity for 15-18mm NTAG213 coin tags.
4. Complete 3D Assembly: Base + PCB mockup + Top Grid + 16 Letter Tiles.

Exports: .FCStd (native FreeCAD), .step (CAD interchange), and .stl (3D printing).
"""

import os
import sys
import math

# Ensure FreeCAD library paths are loaded
for p in ['/usr/lib/freecad/lib', '/usr/lib/freecad/Ext']:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

import FreeCAD
import Part
import MeshPart

# ==============================================================================
# PARAMETRIC CONFIGURATION
# ==============================================================================

# PCB Specifications (from KiCad test_grid_4x4)
PCB_WIDTH = 100.0
PCB_LENGTH = 100.0
PCB_THICKNESS = 1.6
PCB_HOLES = [(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]

# 4x4 Coil Grid Centers on PCB (KiCad coordinates)
COIL_COLS_PCB = [21.5, 40.5, 59.5, 78.5]
COIL_ROWS_PCB = [33.0, 52.0, 71.0, 90.0]

# Enclosure Base Clearances & Sizing
PCB_CLEARANCE = 0.5            # 0.25mm per side around PCB
WALL_THICKNESS = 2.5           # Outer enclosure wall thickness
BOTTOM_FLOOR_THICKNESS = 2.5   # Base bottom thickness
STANDOFF_HEIGHT = 3.5          # Standoff height under PCB (clears THT header pins)
SCREW_DRILL_DIA = 3.0          # M3 self-tapping / clearance hole diameter
SCREW_CBore_DIA = 6.2          # M3 screw head counterbore diameter
SCREW_CBore_DEPTH = 1.6        # M3 screw head counterbore depth

# Top Playing Faceplate Sizing
TOP_FLOOR_THICKNESS = 1.5      # RF Invariant: <=1.6mm above antenna coils
RIB_HEIGHT = 1.2               # Raised divider rib height above playing surface
POCKET_WIDTH = 18.4            # Tile pocket width (+0.4mm clearance for 18mm tiles)
POCKET_DEPTH = 1.2             # Tile pocket depth
TOP_LIP_DEPTH = 1.0            # Registration rim mating into base cavity

# Letter Tile Prototype Sizing
TILE_WIDTH = 18.0              # Standard prototype tile width
TILE_HEIGHT = 4.8              # Standard Scrabble tile thickness
TAG_CAVITY_DIA = 15.5          # Diameter for standard NTAG213 coin tag
TAG_CAVITY_DEPTH = 1.0         # Depth for coin tag
TAG_PLUG_THICKNESS = 0.8       # Snap-in bottom retention disc

# Calculated Enclosure Dimensions
INNER_WIDTH = PCB_WIDTH + PCB_CLEARANCE
INNER_LENGTH = PCB_LENGTH + PCB_CLEARANCE
OUTER_WIDTH = INNER_WIDTH + 2.0 * WALL_THICKNESS
OUTER_LENGTH = INNER_LENGTH + 2.0 * WALL_THICKNESS
CAVITY_DEPTH = STANDOFF_HEIGHT + PCB_THICKNESS + TOP_LIP_DEPTH
BASE_TOTAL_HEIGHT = BOTTOM_FLOOR_THICKNESS + CAVITY_DEPTH

# PCB Origin in Enclosure Coordinate Frame
PCB_OFFSET_X = WALL_THICKNESS + PCB_CLEARANCE / 2.0
PCB_OFFSET_Y = WALL_THICKNESS + PCB_CLEARANCE / 2.0

# Output Paths
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))


def export_shape(obj, name, doc=None):
    """Exports document object as high-res STL and complete STEP file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    step_path = os.path.join(OUTPUT_DIR, f"{name}.step")
    stl_path = os.path.join(OUTPUT_DIR, f"{name}.stl")
    
    # Export STEP using document object
    Part.export([obj], step_path)
    
    # High-quality OpenCASCADE tessellation for 3D printing
    shape = obj.Shape
    mesh = MeshPart.meshFromShape(shape, LinearDeflection=0.05, AngularDeflection=0.1745)
    mesh.write(stl_path)
    
    # Save FCStd if document provided
    if doc is not None:
        fcstd_path = os.path.join(OUTPUT_DIR, f"{name}.FCStd")
        doc.saveAs(fcstd_path)
        step_size = os.path.getsize(step_path) // 1024
        print(f"  [+] Saved {name}: .FCStd, .step ({step_size}KB), .stl ({mesh.CountFacets} facets)")
    else:
        step_size = os.path.getsize(step_path) // 1024
        print(f"  [+] Exported {name}: .step ({step_size}KB), .stl ({mesh.CountFacets} facets)")


def build_base_enclosure():
    """Generates the base enclosure tray with M3 standoffs and connector cutouts."""
    doc = FreeCAD.newDocument("Base_Enclosure")
    
    # Outer solid envelope
    outer = Part.makeBox(OUTER_WIDTH, OUTER_LENGTH, BASE_TOTAL_HEIGHT)
    
    # Fillet outer vertical corners
    v_edges = [e for e in outer.Edges if abs(e.Length - BASE_TOTAL_HEIGHT) < 1e-3]
    outer = outer.makeFillet(3.0, v_edges)
    
    # Hollow out PCB inner cavity
    cavity = Part.makeBox(INNER_WIDTH, INNER_LENGTH, CAVITY_DEPTH + 1.0,
                          FreeCAD.Vector(PCB_OFFSET_X - PCB_CLEARANCE/2.0,
                                         PCB_OFFSET_Y - PCB_CLEARANCE/2.0,
                                         BOTTOM_FLOOR_THICKNESS))
    base = outer.cut(cavity)
    
    # 4 Corner PCB Mounting Bosses & Screw Holes
    for hx_pcb, hy_pcb in PCB_HOLES:
        hx = PCB_OFFSET_X + hx_pcb
        hy = PCB_OFFSET_Y + hy_pcb
        
        # Cylindrical standoff boss
        post = Part.makeCylinder(3.5, STANDOFF_HEIGHT,
                                 FreeCAD.Vector(hx, hy, BOTTOM_FLOOR_THICKNESS),
                                 FreeCAD.Vector(0, 0, 1))
        base = base.fuse(post)
        
        # M3 Screw through-hole
        screw_hole = Part.makeCylinder(SCREW_DRILL_DIA / 2.0, BASE_TOTAL_HEIGHT + 2.0,
                                       FreeCAD.Vector(hx, hy, -1.0),
                                       FreeCAD.Vector(0, 0, 1))
        base = base.cut(screw_hole)
        
        # Underside counterbore for flush screw head
        cbore = Part.makeCylinder(SCREW_CBore_DIA / 2.0, SCREW_CBore_DEPTH + 0.1,
                                  FreeCAD.Vector(hx, hy, -0.1),
                                  FreeCAD.Vector(0, 0, 1))
        base = base.cut(cbore)
        
    # Connector Port Openings
    standoff_z = BOTTOM_FLOOR_THICKNESS + STANDOFF_HEIGHT
    
    # J1 Host Controller ribbon cable cutout (North wall, PCB X=11.0, Y=5.0)
    j1_cut = Part.makeBox(22.0, WALL_THICKNESS + 2.0, BASE_TOTAL_HEIGHT,
                          FreeCAD.Vector(PCB_OFFSET_X + 1.0, -1.0, standoff_z))
    base = base.cut(j1_cut)
    
    # J2 NFC Transceiver header cutout (North wall, PCB X=66.0, Y=4.0)
    j2_cut = Part.makeBox(18.0, WALL_THICKNESS + 2.0, BASE_TOTAL_HEIGHT,
                          FreeCAD.Vector(PCB_OFFSET_X + 57.0, -1.0, standoff_z))
    base = base.cut(j2_cut)
    
    # J3 SMA RF Test Port cutout (East wall, PCB X=95.0, Y=14.0)
    j3_cut = Part.makeBox(WALL_THICKNESS + 2.0, 14.0, BASE_TOTAL_HEIGHT,
                          FreeCAD.Vector(OUTER_WIDTH - WALL_THICKNESS - 1.0,
                                         PCB_OFFSET_Y + 7.0, standoff_z))
    base = base.cut(j3_cut)
    
    # 4 Non-slip rubber bumper recesses on bottom surface
    for fx, fy in [(12.0, 12.0), (OUTER_WIDTH - 12.0, 12.0),
                   (12.0, OUTER_LENGTH - 12.0), (OUTER_WIDTH - 12.0, OUTER_LENGTH - 12.0)]:
        foot_pocket = Part.makeCylinder(4.0, 0.8, FreeCAD.Vector(fx, fy, -0.1), FreeCAD.Vector(0, 0, 1))
        base = base.cut(foot_pocket)
        
    assert base.isValid(), "Base enclosure geometry is invalid!"
    obj = doc.addObject("Part::Feature", "Base_Enclosure_Tray")
    obj.Shape = base
    doc.recompute()
    
    export_shape(obj, "base_enclosure", doc)
    return base


def build_top_grid_plate():
    """Generates the top playing faceplate with 4x4 tile retention ribs and connector access window."""
    doc = FreeCAD.newDocument("Top_Grid_Plate")
    
    total_top_height = TOP_FLOOR_THICKNESS + RIB_HEIGHT
    outer = Part.makeBox(OUTER_WIDTH, OUTER_LENGTH, total_top_height)
    
    # Fillet outer vertical corners
    v_edges = [e for e in outer.Edges if abs(e.Length - total_top_height) < 1e-3]
    outer = outer.makeFillet(3.0, v_edges)
    
    # Mating alignment rim on underside (registers into base cavity)
    rim_outer = Part.makeBox(INNER_WIDTH - 0.4, INNER_LENGTH - 0.4, TOP_LIP_DEPTH,
                             FreeCAD.Vector(PCB_OFFSET_X + 0.2 - PCB_CLEARANCE/2.0,
                                            PCB_OFFSET_Y + 0.2 - PCB_CLEARANCE/2.0,
                                            -TOP_LIP_DEPTH))
    rim_inner = Part.makeBox(INNER_WIDTH - 4.4, INNER_LENGTH - 4.4, TOP_LIP_DEPTH + 1.0,
                             FreeCAD.Vector(PCB_OFFSET_X + 2.2 - PCB_CLEARANCE/2.0,
                                            PCB_OFFSET_Y + 2.2 - PCB_CLEARANCE/2.0,
                                            -TOP_LIP_DEPTH - 0.5))
    rim = rim_outer.cut(rim_inner)
    plate = outer.fuse(rim)
    
    # North Area Connector Window (Access to J1, J2, J3 headers for DuPont wires & SMA probe)
    conn_window = Part.makeBox(OUTER_WIDTH - 20.0, 20.0, total_top_height + TOP_LIP_DEPTH + 2.0,
                               FreeCAD.Vector(10.0, 3.5, -TOP_LIP_DEPTH - 1.0))
    plate = plate.cut(conn_window)
    
    # 4 Corner M3 Screw Mounting Holes
    for hx_pcb, hy_pcb in PCB_HOLES:
        hx = PCB_OFFSET_X + hx_pcb
        hy = PCB_OFFSET_Y + hy_pcb
        
        # 3.4mm clearance hole
        screw_hole = Part.makeCylinder(1.7, total_top_height + TOP_LIP_DEPTH + 2.0,
                                       FreeCAD.Vector(hx, hy, -TOP_LIP_DEPTH - 1.0),
                                       FreeCAD.Vector(0, 0, 1))
        plate = plate.cut(screw_hole)
        
        # Counterbore on top surface so screw heads sit flush
        cbore = Part.makeCylinder(SCREW_CBore_DIA / 2.0, SCREW_CBore_DEPTH,
                                  FreeCAD.Vector(hx, hy, total_top_height - SCREW_CBore_DEPTH + 0.1),
                                  FreeCAD.Vector(0, 0, 1))
        plate = plate.cut(cbore)
        
    # 16 Tile Retention Pockets (4x4 Grid centered exactly above PCB antenna coils)
    for col_x in COIL_COLS_PCB:
        for row_y in COIL_ROWS_PCB:
            cx = PCB_OFFSET_X + col_x
            cy = PCB_OFFSET_Y + row_y
            pocket = Part.makeBox(POCKET_WIDTH, POCKET_WIDTH, POCKET_DEPTH + 0.5,
                                  FreeCAD.Vector(cx - POCKET_WIDTH / 2.0,
                                                 cy - POCKET_WIDTH / 2.0,
                                                 TOP_FLOOR_THICKNESS))
            plate = plate.cut(pocket)
            
    assert plate.isValid(), "Top grid plate geometry is invalid!"
    obj = doc.addObject("Part::Feature", "Top_Tile_Grid_Plate")
    obj.Shape = plate
    doc.recompute()
    
    export_shape(obj, "top_grid_plate", doc)
    return plate


def build_tile_prototype():
    """Generates a 3D-printable letter tile prototype with internal NTAG213 tag cavity and embossed letter 'A'."""
    doc = FreeCAD.newDocument("NFC_Tile_Prototype")
    
    # Main tile body
    tile = Part.makeBox(TILE_WIDTH, TILE_WIDTH, TILE_HEIGHT,
                         FreeCAD.Vector(-TILE_WIDTH / 2.0, -TILE_WIDTH / 2.0, 0))
    
    # Chamfer/Fillet top perimeter edges for tactile wood feel
    top_edges = [e for e in tile.Edges if abs(e.CenterOfMass.z - TILE_HEIGHT) < 1e-3]
    tile = tile.makeFillet(0.6, top_edges)
    
    # Internal Coin Tag Cavity on bottom face
    tag_cavity = Part.makeCylinder(TAG_CAVITY_DIA / 2.0, TAG_CAVITY_DEPTH,
                                   FreeCAD.Vector(0, 0, -0.1), FreeCAD.Vector(0, 0, 1))
    tile = tile.cut(tag_cavity)
    
    # Embossed Letter 'A' on top surface (0.4mm raised relief)
    emboss_h = 0.4
    bar_l = Part.makeBox(1.2, 8.0, emboss_h, FreeCAD.Vector(-3.5, -4.0, TILE_HEIGHT))
    bar_r = Part.makeBox(1.2, 8.0, emboss_h, FreeCAD.Vector(2.3, -4.0, TILE_HEIGHT))
    bar_t = Part.makeBox(7.0, 1.2, emboss_h, FreeCAD.Vector(-3.5, 2.8, TILE_HEIGHT))
    bar_m = Part.makeBox(7.0, 1.2, emboss_h, FreeCAD.Vector(-3.5, -0.6, TILE_HEIGHT))
    
    # Point Value Subscript '1'
    sub_1 = Part.makeBox(0.8, 3.0, emboss_h, FreeCAD.Vector(5.5, -6.0, TILE_HEIGHT))
    
    letter_a = bar_l.fuse(bar_r).fuse(bar_t).fuse(bar_m).fuse(sub_1)
    tile = tile.fuse(letter_a)
    
    assert tile.isValid(), "Tile prototype geometry is invalid!"
    obj = doc.addObject("Part::Feature", "NFC_Scrabble_Tile_A1")
    obj.Shape = tile
    
    # Also generate press-fit bottom plug disc
    plug = Part.makeCylinder((TAG_CAVITY_DIA - 0.2) / 2.0, TAG_PLUG_THICKNESS,
                             FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
    plug_obj = doc.addObject("Part::Feature", "Tile_Bottom_Plug")
    plug_obj.Shape = plug
    
    doc.recompute()
    
    export_shape(obj, "nfc_tile_prototype", doc)
    export_shape(plug_obj, "nfc_tile_plug", None)
    return tile


def build_complete_assembly(base_shape, top_shape, tile_shape):
    """Assembles all components into a full 3D prototype assembly document."""
    doc = FreeCAD.newDocument("Assembly_4x4_Prototype")
    
    # 1. Base Tray
    obj_base = doc.addObject("Part::Feature", "Base_Enclosure")
    obj_base.Shape = base_shape
    
    # 2. PCB Mockup (100x100x1.6mm green plate with mounting holes and coils)
    pcb_mockup = Part.makeBox(PCB_WIDTH, PCB_LENGTH, PCB_THICKNESS,
                              FreeCAD.Vector(PCB_OFFSET_X, PCB_OFFSET_Y,
                                             BOTTOM_FLOOR_THICKNESS + STANDOFF_HEIGHT))
    for hx, hy in PCB_HOLES:
        hole = Part.makeCylinder(1.6, PCB_THICKNESS + 2.0,
                                 FreeCAD.Vector(PCB_OFFSET_X + hx, PCB_OFFSET_Y + hy,
                                                BOTTOM_FLOOR_THICKNESS + STANDOFF_HEIGHT - 1.0),
                                 FreeCAD.Vector(0, 0, 1))
        pcb_mockup = pcb_mockup.cut(hole)
    obj_pcb = doc.addObject("Part::Feature", "PCB_Test_Grid_4x4")
    obj_pcb.Shape = pcb_mockup
    
    # 3. Top Playing Faceplate
    obj_top = doc.addObject("Part::Feature", "Top_Grid_Plate")
    top_z = BOTTOM_FLOOR_THICKNESS + STANDOFF_HEIGHT + PCB_THICKNESS
    top_translated = top_shape.copy()
    top_translated.translate(FreeCAD.Vector(0, 0, top_z))
    obj_top.Shape = top_translated
    
    # 4. 16 Letter Tiles placed in the grid pockets
    tile_z = top_z + TOP_FLOOR_THICKNESS
    for idx_c, col_x in enumerate(COIL_COLS_PCB):
        for idx_r, row_y in enumerate(COIL_ROWS_PCB):
            cx = PCB_OFFSET_X + col_x
            cy = PCB_OFFSET_Y + row_y
            tile_inst = tile_shape.copy()
            tile_inst.translate(FreeCAD.Vector(cx, cy, tile_z))
            tile_obj = doc.addObject("Part::Feature", f"Tile_{chr(65 + idx_r * 4 + idx_c)}")
            tile_obj.Shape = tile_inst
            
    doc.recompute()
    
    # Save assembly project and STEP
    assembly_fcstd = os.path.join(OUTPUT_DIR, "assembly_4x4_prototype.FCStd")
    assembly_step = os.path.join(OUTPUT_DIR, "assembly_4x4_prototype.step")
    doc.saveAs(assembly_fcstd)
    Part.export([obj_base, obj_pcb, obj_top], assembly_step)
    print(f"  [+] Complete Assembly saved: assembly_4x4_prototype.FCStd and .step")


def main():
    print("=================================================================")
    print(" Smart Crossword Board - 4x4 Prototype CAD Generator (FreeCAD)")
    print("=================================================================")
    print(f"Target Output Directory: {OUTPUT_DIR}")
    
    print("\n[Step 1/4] Building Base Enclosure Tray...")
    base_shape = build_base_enclosure()
    
    print("\n[Step 2/4] Building Top Grid Faceplate...")
    top_shape = build_top_grid_plate()
    
    print("\n[Step 3/4] Building NFC Scrabble Letter Tile Prototype...")
    tile_shape = build_tile_prototype()
    
    print("\n[Step 4/4] Building Complete 3D Assembly...")
    build_complete_assembly(base_shape, top_shape, tile_shape)
    
    print("\n=================================================================")
    print(" All CAD models successfully generated, validated, and exported!")
    print("=================================================================")


if __name__ == "__main__":
    main()
