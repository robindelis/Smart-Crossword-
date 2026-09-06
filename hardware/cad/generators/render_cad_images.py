#!/usr/bin/env python3
"""
render_cad_images.py - Automated High-Resolution 3D Screenshot Renderer for CAD Models

Renders transparent PNG images of the 4x4 prototype CAD models using OpenSCAD & Pillow:
1. base_enclosure_3d.png: Base chassis tray showing PCB cavity, standoffs, and port cutouts.
2. top_grid_plate_3d.png: Top faceplate showing 4x4 tile retention ribs and wiring window.
3. nfc_tile_prototype_3d.png: NFC Scrabble tile prototype with embossed letter and coin cavity.
4. assembly_4x4_prototype_3d.png: Master 3D assembly (Base + PCB + Top Grid + 16 Letter Tiles).
"""

import os
import sys
import subprocess
from PIL import Image

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CAD_OUTPUT_DIR = os.path.join(ROOT_DIR, "hardware", "cad", "output")
SCRIPTS_TMP = "/tmp/openscad_renders"
os.makedirs(SCRIPTS_TMP, exist_ok=True)
os.makedirs(CAD_OUTPUT_DIR, exist_ok=True)


def make_transparent(input_png, output_png, bg_tol=8):
    """Replaces solid background color with transparent alpha channel."""
    img = Image.open(input_png).convert("RGBA")
    data = img.load()
    w, h = img.size
    bg = data[0, 0][:3]
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            if abs(r - bg[0]) < bg_tol and abs(g - bg[1]) < bg_tol and abs(b - bg[2]) < bg_tol:
                data[x, y] = (255, 255, 255, 0)
                
    img.save(output_png, "PNG")


def render_model(scad_code, raw_png_name, final_png_name, img_size="1600,1200", camera=None):
    """Executes OpenSCAD CLI to render a scene and converts to transparent PNG."""
    scad_file = os.path.join(SCRIPTS_TMP, f"{raw_png_name}.scad")
    raw_png = os.path.join(SCRIPTS_TMP, f"{raw_png_name}.png")
    final_png = os.path.join(CAD_OUTPUT_DIR, final_png_name)
    
    with open(scad_file, "w") as f:
        f.write(scad_code)
        
    cmd = [
        "openscad",
        "-o", raw_png,
        "--autocenter",
        "--viewall",
        f"--imgsize={img_size}",
        "--colorscheme=Tomorrow Night",
        scad_file
    ]
    if camera:
        cmd.extend(["--camera", camera])
        
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error rendering {raw_png_name}: {res.stderr}")
        return False
        
    make_transparent(raw_png, final_png)
    file_size = os.path.getsize(final_png) // 1024
    print(f"  [+] Generated {final_png_name} ({file_size} KB)")
    return True


def main():
    print("=================================================================")
    print(" Rendering 3D CAD Screenshots for Obsidian Canvas & Docs")
    print("=================================================================")
    
    base_stl = os.path.join(CAD_OUTPUT_DIR, "base_enclosure.stl")
    top_stl = os.path.join(CAD_OUTPUT_DIR, "top_grid_plate.stl")
    tile_stl = os.path.join(CAD_OUTPUT_DIR, "nfc_tile_prototype.stl")
    plug_stl = os.path.join(CAD_OUTPUT_DIR, "nfc_tile_plug.stl")
    
    # 1. Base Enclosure Tray
    scad_base = f"""
    color([0.28, 0.30, 0.35])
        import("{base_stl}");
    """
    print("\n[1/4] Rendering Base Enclosure Tray...")
    render_model(scad_base, "raw_base", "base_enclosure_3d.png")
    
    # 2. Top Grid Faceplate
    scad_top = f"""
    color([0.92, 0.89, 0.83])
        import("{top_stl}");
    """
    print("\n[2/4] Rendering Top Grid Faceplate...")
    render_model(scad_top, "raw_top", "top_grid_plate_3d.png")
    
    # 3. NFC Scrabble Letter Tile Prototype (Showing top relief & bottom cavity)
    scad_tile = f"""
    // Primary tile showing embossed letter 'A' and score '1'
    translate([-12, 0, 0])
        color([0.88, 0.76, 0.58])
            import("{tile_stl}");

    // Inverted tile showing coin tag cavity on underside
    translate([12, 0, 4.8])
        rotate([180, 0, 0])
            color([0.88, 0.76, 0.58])
                import("{tile_stl}");

    // Bottom retention plug disc
    translate([12, 22, 0])
        color([0.75, 0.65, 0.50])
            import("{plug_stl}");
    """
    print("\n[3/4] Rendering NFC Scrabble Letter Tile Prototype...")
    render_model(scad_tile, "raw_tile", "nfc_tile_prototype_3d.png")
    
    # 4. Final Assembly (Base + PCB + Top Grid + 16 Letter Tiles)
    scad_assembly = f"""
    // Base enclosure in dark slate
    color([0.22, 0.24, 0.28])
        import("{base_stl}");

    // PCB mockup in solder-mask green
    color([0.15, 0.48, 0.28])
        translate([2.75, 2.75, 6.0])
        cube([100, 100, 1.6]);

    // Top Grid Plate in warm ivory
    color([0.92, 0.89, 0.83])
        translate([0, 0, 7.6])
        import("{top_stl}");

    // 16 Letter Tiles positioned in 4x4 grid pockets
    col_x = [24.25, 43.25, 62.25, 81.25];
    row_y = [35.75, 54.75, 73.75, 92.75];

    for (cx = col_x) {{
        for (cy = row_y) {{
            translate([cx, cy, 7.6 + 1.5])
                color([0.88, 0.76, 0.58])
                    import("{tile_stl}");
        }}
    }}
    """
    print("\n[4/4] Rendering Master 4x4 3D Assembly...")
    render_model(scad_assembly, "raw_assembly", "assembly_4x4_prototype_3d.png")
    
    print("\n=================================================================")
    print(" All CAD screenshots rendered and saved to hardware/cad/output/")
    print("=================================================================")


if __name__ == "__main__":
    main()
