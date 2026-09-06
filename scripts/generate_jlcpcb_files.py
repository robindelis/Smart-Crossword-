#!/usr/bin/env python3
"""
Generate JLCPCB-compatible BOM and CPL (Pick-and-Place) files
from KiCad PCB pos export and project BOM definitions.
"""

import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
KICAD_DIR = os.path.join(PROJECT_ROOT, "hardware", "kicad", "test_grid_4x4")
JLCPCB_DIR = os.path.join(KICAD_DIR, "jlcpcb")
CPL_RAW = os.path.join(KICAD_DIR, "cpl_raw.csv")

os.makedirs(JLCPCB_DIR, exist_ok=True)

# Define BOM mapping for SMD components populated by JLCPCB SMT Assembly
SMD_BOM = [
    {
        "Comment": "100pF 50V C0G 5%",
        "Designator": "C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16",
        "Footprint": "C_0603_1608Metric",
        "LCSC Part #": "C14405",
        "Quantity": 16,
    },
    {
        "Comment": "3.3Ω 1% 1/10W",
        "Designator": "R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R16",
        "Footprint": "R_0603_1608Metric",
        "LCSC Part #": "C22971",
        "Quantity": 16,
    },
    {
        "Comment": "0.1uF 50V X7R 10%",
        "Designator": "C17",
        "Footprint": "C_0603_1608Metric",
        "LCSC Part #": "C14663",
        "Quantity": 1,
    },
    {
        "Comment": "10uF 10V X5R 10%",
        "Designator": "C18",
        "Footprint": "C_0805_2012Metric",
        "LCSC Part #": "C15850",
        "Quantity": 1,
    },
    {
        "Comment": "CD74HC4067SM96 16-Ch MUX",
        "Designator": "U1",
        "Footprint": "SOIC-24W_7.5x15.4mm_P1.27mm",
        "LCSC Part #": "C7406",
        "Quantity": 1,
    },
]

# Excluded from SMT (hand-soldered through-hole parts):
# J1: 2x10 Pin Header 2.54mm
# J2: 1x10 Pin Header 2.54mm
# J3: SMA Edge/Vertical Connector

def generate_bom():
    bom_file = os.path.join(JLCPCB_DIR, "bom_jlcpcb.csv")
    with open(bom_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for item in SMD_BOM:
            writer.writerow([
                item["Comment"],
                item["Designator"],
                item["Footprint"],
                item["LCSC Part #"]
            ])
    print(f"Generated JLCPCB BOM: {bom_file}")

def generate_cpl():
    cpl_file = os.path.join(JLCPCB_DIR, "cpl_jlcpcb.csv")
    
    # Allowed SMD references for JLCPCB SMT
    smd_refs = set()
    for item in SMD_BOM:
        for ref in item["Designator"].split(", "):
            smd_refs.add(ref.strip())
            
    with open(CPL_RAW, "r", encoding="utf-8") as f_in, open(cpl_file, "w", newline="", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        
        for row in reader:
            ref = row["Ref"].strip('"')
            if ref not in smd_refs:
                continue
            
            # JLCPCB expects "Top" or "Bottom"
            layer = "Top" if row["Side"].lower() in ["top", "front"] else "Bottom"
            x = f"{float(row['PosX']):.3f}"
            y = f"{float(row['PosY']):.3f}"
            rot = f"{float(row['Rot']):.1f}"
            
            writer.writerow([ref, x, y, layer, rot])
            
    print(f"Generated JLCPCB CPL: {cpl_file}")

if __name__ == "__main__":
    generate_bom()
    generate_cpl()
