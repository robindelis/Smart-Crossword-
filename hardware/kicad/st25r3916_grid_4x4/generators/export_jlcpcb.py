#!/usr/bin/env python3
"""
JLCPCB SMT Deliverables Generator (BOM & CPL)
Parses st25r3916_grid_4x4.kicad_pcb and outputs:
- hardware/kicad/st25r3916_grid_4x4/jlcpcb/bom.csv (with verified LCSC Part Numbers)
- hardware/kicad/st25r3916_grid_4x4/jlcpcb/cpl.csv (SMT Pick and Place coordinates)
"""
import pcbnew
import os
import sys
import csv

def generate_jlcpcb_files(board_path=None):
    if board_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        board_path = os.path.join(base_dir, 'st25r3916_grid_4x4.kicad_pcb')
    else:
        base_dir = os.path.dirname(os.path.abspath(board_path))

    board = pcbnew.LoadBoard(board_path)

    lcsc_map = {
        # Resistors
        '1.5R': 'C22790',
        # Capacitors
        '100pF': 'C14663',
        '22pF': 'C1653',
        '12pF': 'C1648',
        '10pF': 'C1642',
        '18pF': 'C1651',
        '150pF': 'C1598',
        '180pF': 'C1600',
        '10nF': 'C57112',
        '0.1uF': 'C14664',
        '100nF': 'C14664',
        '1uF': 'C15849',
        '2.2uF': 'C23630',
        '10uF': 'C19702',
        # Inductor
        '470nH': 'C1045',
        # ICs
        'CD74HC4067M': 'C109598',
        'ST25R3916B-AQFT': 'C2943312',
        # Crystal
        '27.12MHz': 'C383929',
    }

    fps = board.Footprints()
    cpl_rows = []
    bom_dict = {}

    for i in range(len(fps)):
        fp = fps[i]
        ref = fp.GetReference()
        val = fp.GetValue()
        fpid = fp.GetFPID().GetLibItemName()

        # Filter out virtual planar coils (L1-L16) and non-SMT mounting holes (H1-H4)
        if ref.startswith('L') and ref != 'L17':
            continue
        if ref.startswith('H'):
            continue

        pos = fp.GetPosition()
        x = pos.x / 1e6
        y = pos.y / 1e6
        rot = fp.GetOrientationDegrees() % 360
        layer = 'Top' if fp.GetLayerName() == 'F.Cu' else 'Bottom'

        cpl_rows.append((ref, f'{x:.3f}', f'{y:.3f}', layer, f'{rot:.1f}'))

        # Match LCSC Part #
        lcsc = lcsc_map.get(val, '')
        if not lcsc:
            for k, v in lcsc_map.items():
                if k in val:
                    lcsc = v
                    break

        key = (val, str(fpid), lcsc)
        if key not in bom_dict:
            bom_dict[key] = []
        bom_dict[key].append(ref)

    out_dir = os.path.join(base_dir, 'jlcpcb')
    os.makedirs(out_dir, exist_ok=True)

    cpl_path = os.path.join(out_dir, 'cpl.csv')
    with open(cpl_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for row in sorted(cpl_rows, key=lambda r: (r[0][:2], int(r[0][2:]) if r[0][2:].isdigit() else 0, r[0])):
            writer.writerow(row)
    print(f'Wrote {len(cpl_rows)} SMT components to {cpl_path}')

    bom_path = os.path.join(out_dir, 'bom.csv')
    with open(bom_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Quantity'])
        for (val, fpid, lcsc), refs in sorted(bom_dict.items(), key=lambda item: item[0][0]):
            sorted_refs = sorted(refs, key=lambda r: (r[:2], int(r[2:]) if r[2:].isdigit() else 0, r))
            writer.writerow([val, ','.join(sorted_refs), fpid, lcsc, len(sorted_refs)])
    print(f'Wrote BOM to {bom_path}')

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    generate_jlcpcb_files(target)
