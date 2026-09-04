#!/usr/bin/env python3
"""
Smart Crossword Board - Phase 1 4x4 NFC Test Board Generator
Generates KiCad 10 Schematic (.kicad_sch) and PCB Layout (.kicad_pcb).
Hardware Specs:
- Matrix: 4x4 planar spiral coils (19.0mm pitch, 17.5mm outer diameter, 7 turns, 0.25mm trace/space)
- Tuning: L ~ 1.26 uH, C ~ 100 pF C0G, R_damp = 3.3 ohm (Q ~ 20-30)
- Switching: CD74HC4067 16-channel analog MUX
- Connectors: J1 Host Header 2x10, J2 NFC Transceiver Header 1x10, J3 SMA RF test port
- Stackup: 4-layer (F.Cu coils & parts, In1.Cu GND with coil cutouts, In2.Cu 3.3V & digital, B.Cu return & GND)
"""

import os
import re
import math
import uuid
import pcbnew

PROJECT_DIR = "/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4"
SCH_PATH = os.path.join(PROJECT_DIR, "test_grid_4x4.kicad_sch")
PCB_PATH = os.path.join(PROJECT_DIR, "test_grid_4x4.kicad_pcb")
PRO_PATH = os.path.join(PROJECT_DIR, "test_grid_4x4.kicad_pro")

def gen_uuid():
    return str(uuid.uuid4())

def extract_symbol(sym_file, sym_name):
    with open(sym_file) as f:
        content = f.read()
    target = f'(symbol "{sym_name}"'
    idx = content.find(target)
    if idx == -1:
        raise ValueError(f'Symbol {sym_name} not found in {sym_file}')
    depth = 0
    start = idx
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[start:i+1]
    raise ValueError(f'Closing paren not found for {sym_name}')

def get_symbol_pin_offsets(sym_str):
    pattern = re.compile(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\).*?\(name\s+\"([^\"]*)\".*?\(number\s+\"([^\"]*)\"', re.DOTALL)
    pin_map = {}
    for m in pattern.finditer(sym_str):
        x, y, rot, name, num = m.groups()
        pin_map[num] = (float(x), -float(y), name)
    return pin_map

# ==============================================================================
# SCHEMATIC GENERATION
# ==============================================================================
def build_schematic():
    print("Building schematic...")
    root_uuid = gen_uuid()

    sym_l = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'L')
    sym_c = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'C')
    sym_r = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'R')
    sym_mux = extract_symbol('/usr/share/kicad/symbols/74xx.kicad_sym', 'CD74HC4067M')
    sym_j1 = extract_symbol('/usr/share/kicad/symbols/Connector_Generic.kicad_sym', 'Conn_02x10_Odd_Even')
    sym_j2 = extract_symbol('/usr/share/kicad/symbols/Connector_Generic.kicad_sym', 'Conn_01x10')
    sym_sma = extract_symbol('/usr/share/kicad/symbols/Connector.kicad_sym', 'Conn_Coaxial')
    sym_hole = extract_symbol('/usr/share/kicad/symbols/Mechanical.kicad_sym', 'MountingHole_Pad')
    sym_3v3 = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', '+3V3')
    sym_gnd = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', 'GND')
    sym_flg = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', 'PWR_FLAG')

    pins_mux = get_symbol_pin_offsets(sym_mux)
    pins_j1 = get_symbol_pin_offsets(sym_j1)
    pins_j2 = get_symbol_pin_offsets(sym_j2)
    pins_sma = get_symbol_pin_offsets(sym_sma)
    pins_hole = get_symbol_pin_offsets(sym_hole)

    def rename_sym(sym_str, old_name, new_name):
        return sym_str.replace(f'(symbol "{old_name}"', f'(symbol "{new_name}"', 1)

    lib_symbols_list = [
        rename_sym(sym_l, 'L', 'Device:L'),
        rename_sym(sym_c, 'C', 'Device:C'),
        rename_sym(sym_r, 'R', 'Device:R'),
        rename_sym(sym_mux, 'CD74HC4067M', '74xx:CD74HC4067M'),
        rename_sym(sym_j1, 'Conn_02x10_Odd_Even', 'Connector_Generic:Conn_02x10_Odd_Even'),
        rename_sym(sym_j2, 'Conn_01x10', 'Connector_Generic:Conn_01x10'),
        rename_sym(sym_sma, 'Conn_Coaxial', 'Connector:Conn_Coaxial'),
        rename_sym(sym_hole, 'MountingHole_Pad', 'Mechanical:MountingHole_Pad'),
        rename_sym(sym_3v3, '+3V3', 'power:+3V3'),
        rename_sym(sym_gnd, 'GND', 'power:GND'),
        rename_sym(sym_flg, 'PWR_FLAG', 'power:PWR_FLAG')
    ]

    symbols_code = []
    wires_code = []
    labels_code = []

    def add_label(net, x, y, rot=0):
        labels_code.append(f'''\t(label "{net}"
\t\t(at {x:.3f} {y:.3f} {rot})
\t\t(effects (font (size 1.27 1.27)) (justify left))
\t\t(uuid "{gen_uuid()}")
\t)''')

    def add_wire(x1, y1, x2, y2):
        wires_code.append(f'''\t(wire
\t\t(pts (xy {x1:.3f} {y1:.3f}) (xy {x2:.3f} {y2:.3f}))
\t\t(stroke (width 0) (type default))
\t\t(uuid "{gen_uuid()}")
\t)''')

    def connect_pin_to_net(sym_x, sym_y, pin_offsets, pin_num, net_name, dx_wire, dy_wire, label_rot):
        dx, dy, _ = pin_offsets[str(pin_num)]
        px, py = sym_x + dx, sym_y + dy
        wx, wy = px + dx_wire, py + dy_wire
        add_wire(px, py, wx, wy)
        add_label(net_name, wx, wy, label_rot)

    # 1. Place U1 (CD74HC4067M)
    u1_x, u1_y = 120.0, 100.0
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "74xx:CD74HC4067M")
\t\t(at {u1_x:.3f} {u1_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "U1" (at {u1_x-8.89:.3f} {u1_y-22.86:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "CD74HC4067M" (at {u1_x+1.27:.3f} {u1_y-22.86:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm" (at {u1_x:.3f} {u1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "http://www.ti.com/lit/ds/symlink/cd74hc4067.pdf" (at {u1_x:.3f} {u1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 25)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "U1") (unit 1))))
\t)''')

    connect_pin_to_net(u1_x, u1_y, pins_mux, 1, "RF_SIG", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 24, "+3.3V", 0, -5.08, 90)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 12, "GND", 0, 5.08, 270)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 10, "MUX_S0", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 11, "MUX_S1", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 14, "MUX_S2", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 13, "MUX_S3", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 15, "MUX_EN", -5.08, 0, 180)

    mux_pins_order = [9, 8, 7, 6, 5, 4, 3, 2, 23, 22, 21, 20, 19, 18, 17, 16]
    for ch_idx, pin_num in enumerate(mux_pins_order):
        connect_pin_to_net(u1_x, u1_y, pins_mux, pin_num, f"RF_CH{ch_idx}", 5.08, 0, 0)

    # 2. 16 LC resonant tanks
    tank_base_x = 200.0
    tank_base_y = 30.0
    for k in range(16):
        cell_id = k + 1
        ty = tank_base_y + k * 17.78

        # R_k (3.3 ohm)
        rx, ry = tank_base_x, ty
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at {rx:.3f} {ry:.3f} 90)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "R{cell_id}" (at {rx:.3f} {ry-2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "3.3" (at {rx:.3f} {ry+2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "R{cell_id}") (unit 1))))
\t)''')
        add_wire(rx - 3.81, ry, rx - 7.62, ry)
        add_label(f"RF_CH{k}", rx - 7.62, ry, 180)

        # C_k (100pF C0G)
        cx, cy = rx - 5.08, ry + 7.62
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.3f} {cy:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "C{cell_id}" (at {cx+2.54:.3f} {cy-1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "100pF" (at {cx+2.54:.3f} {cy+1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C{cell_id}") (unit 1))))
\t)''')
        # Connect C pin 1 to RF_CHk
        add_wire(cx, cy - 3.81, cx, ry)
        add_wire(cx, ry, rx - 3.81, ry)
        add_wire(cx, cy + 3.81, cx, cy + 6.35)
        add_label("GND", cx, cy + 6.35, 270)

        # L_k (1.26uH Planar Coil)
        lx, ly = rx + 17.78, ry
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:L")
\t\t(at {lx:.3f} {ly:.3f} 90)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "L{cell_id}" (at {lx:.3f} {ly-2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "1.26uH" (at {lx:.3f} {ly+2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "NFC_Coil_17.5x17.5mm" (at {lx:.3f} {ly:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {lx:.3f} {ly:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "L{cell_id}") (unit 1))))
\t)''')
        add_wire(rx + 3.81, ry, lx - 3.81, ry)
        add_label(f"RF_COIL_{cell_id}", rx + 3.81, ry, 0)
        add_wire(lx + 3.81, ly, lx + 7.62, ly)
        add_label("GND", lx + 7.62, ly, 0)

    # 3. Decoupling Capacitors C17, C18
    for c_ref, c_val, c_fp, cx, cy in [
        ("C17", "0.1uF", "Capacitor_SMD:C_0603_1608Metric", 100.0, 45.0),
        ("C18", "10uF", "Capacitor_SMD:C_0805_2012Metric", 112.0, 45.0)
    ]:
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.3f} {cy:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "{c_ref}" (at {cx+2.54:.3f} {cy-1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "{c_val}" (at {cx+2.54:.3f} {cy+1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "{c_fp}" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{c_ref}") (unit 1))))
\t)''')
        add_wire(cx, cy - 3.81, cx, cy - 6.35)
        add_label("+3.3V", cx, cy - 6.35, 90)
        add_wire(cx, cy + 3.81, cx, cy + 6.35)
        add_label("GND", cx, cy + 6.35, 270)

    # R17 (10k pullup on MUX_EN)
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at 85.0 45.0 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "R17" (at 87.54 43.73 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "10k" (at 87.54 46.27 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 85.0 45.0 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at 85.0 45.0 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "R17") (unit 1))))
\t)''')
    add_wire(85.0, 45.0 - 3.81, 85.0, 45.0 - 6.35)
    add_label("+3.3V", 85.0, 45.0 - 6.35, 90)
    add_wire(85.0, 45.0 + 3.81, 85.0, 45.0 + 6.35)
    add_label("MUX_EN", 85.0, 45.0 + 6.35, 270)

    # R18..R21 (100k pulldowns on S0..S3)
    for idx, s_name in enumerate(["MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3"]):
        r_num = 18 + idx
        rx, ry = 45.0 + idx * 10.0, 45.0
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at {rx:.3f} {ry:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "R{r_num}" (at {rx+2.54:.3f} {ry-1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "100k" (at {rx+2.54:.3f} {ry+1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "R{r_num}") (unit 1))))
\t)''')
        add_wire(rx, ry - 3.81, rx, ry - 6.35)
        add_label(s_name, rx, ry - 6.35, 90)
        add_wire(rx, ry + 3.81, rx, ry + 6.35)
        add_label("GND", rx, ry + 6.35, 270)

    # 4. Host Header J1 (2x10)
    j1_x, j1_y = 50.0, 110.0
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector_Generic:Conn_02x10_Odd_Even")
\t\t(at {j1_x:.3f} {j1_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "J1" (at {j1_x+1.27:.3f} {j1_y-15.24:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Host_Header_2x10" (at {j1_x+1.27:.3f} {j1_y+15.24:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at {j1_x:.3f} {j1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {j1_x:.3f} {j1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 21)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "J1") (unit 1))))
\t)''')

    j1_net_map = {
        1: "+3.3V", 2: "+3.3V",
        3: "MUX_S0", 4: "SPI_SCK",
        5: "MUX_S1", 6: "SPI_MISO",
        7: "MUX_S2", 8: "SPI_MOSI",
        9: "MUX_S3", 10: "SPI_CS",
        11: "MUX_EN", 12: "NFC_IRQ",
        13: "I2C_SDA", 14: "NFC_RST",
        15: "I2C_SCL", 16: "GPIO_AUX",
        17: "GND", 18: "GND",
        19: "GND", 20: "GND"
    }
    for p_num, net in j1_net_map.items():
        dx, dy, _ = pins_j1[str(p_num)]
        px, py = j1_x + dx, j1_y + dy
        if dx < 0:
            add_wire(px, py, px - 5.08, py)
            add_label(net, px - 5.08, py, 180)
        else:
            add_wire(px, py, px + 5.08, py)
            add_label(net, px + 5.08, py, 0)

    # 5. NFC Transceiver Header J2 (1x10)
    j2_x, j2_y = 50.0, 160.0
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector_Generic:Conn_01x10")
\t\t(at {j2_x:.3f} {j2_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "J2" (at {j2_x-2.54:.3f} {j2_y-15.24:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "NFC_Module_Header" (at {j2_x-2.54:.3f} {j2_y+15.24:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical" (at {j2_x:.3f} {j2_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {j2_x:.3f} {j2_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 11)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "J2") (unit 1))))
\t)''')

    j2_net_map = {
        1: "RF_SIG", 2: "GND",
        3: "+3.3V",  4: "GND",
        5: "SPI_SCK", 6: "SPI_MISO",
        7: "SPI_MOSI", 8: "SPI_CS",
        9: "NFC_IRQ", 10: "NFC_RST"
    }
    for p_num, net in j2_net_map.items():
        dx, dy, _ = pins_j2[str(p_num)]
        px, py = j2_x + dx, j2_y + dy
        add_wire(px, py, px - 5.08, py)
        add_label(net, px - 5.08, py, 180)

    # 6. Coaxial RF Connector J3
    j3_x, j3_y = 50.0, 195.0
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector:Conn_Coaxial")
\t\t(at {j3_x:.3f} {j3_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "J3" (at {j3_x:.3f} {j3_y-5.08:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "SMA_RF_TEST" (at {j3_x:.3f} {j3_y+5.08:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134_Vertical" (at {j3_x:.3f} {j3_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {j3_x:.3f} {j3_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "J3") (unit 1))))
\t)''')
    connect_pin_to_net(j3_x, j3_y, pins_sma, 1, "RF_SIG", -5.08, 0, 180)
    connect_pin_to_net(j3_x, j3_y, pins_sma, 2, "GND", 0, 5.08, 270)

    # 7. Mounting holes H1..H4
    for idx, (hx, hy) in enumerate([(30.0, 220.0), (50.0, 220.0), (70.0, 220.0), (90.0, 220.0)]):
        h_ref = f"H{idx+1}"
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Mechanical:MountingHole_Pad")
\t\t(at {hx:.3f} {hy:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "{h_ref}" (at {hx:.3f} {hy-3.81:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "MountingHole_M3" (at {hx:.3f} {hy+3.81:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "MountingHole:MountingHole_3.2mm_M3_Pad_Via" (at {hx:.3f} {hy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {hx:.3f} {hy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{h_ref}") (unit 1))))
\t)''')
        connect_pin_to_net(hx, hy, pins_hole, 1, "GND", 0, 5.08, 270)

    # 8. Power Flags
    for idx, (net_name, px, py) in enumerate([("+3.3V", 25.0, 80.0), ("GND", 25.0, 85.0)]):
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "power:PWR_FLAG")
\t\t(at {px:.3f} {py:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{gen_uuid()}")
\t\t(property "Reference" "#FLG{idx+1}" (at {px:.3f} {py-1.905:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "PWR_FLAG" (at {px:.3f} {py+1.905:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at {px:.3f} {py:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {px:.3f} {py:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "#FLG{idx+1}") (unit 1))))
\t)''')
        add_wire(px, py, px - 5.08, py)
        add_label(net_name, px - 5.08, py, 180)

    sch_output = f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A3")
\t(title_block
\t\t(title "Smart Crossword Board - 4x4 NFC Test Grid")
\t\t(date "2026-09-04")
\t\t(rev "1.0")
\t\t(company "Smart Crossword Project")
\t\t(comment 1 "13.56 MHz LC Matrix Test Board (CD74HC4067 16-ch Switch)")
\t\t(comment 2 "L=1.26uH (7-turn spiral, 19mm pitch), C=100pF C0G, R=3.3R")
\t\t(comment 3 "Max Wood Overlay: 2.0mm - 2.5mm")
\t)
\t(lib_symbols
{chr(10).join(lib_symbols_list)}
\t)
{chr(10).join(symbols_code)}
{chr(10).join(wires_code)}
{chr(10).join(labels_code)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
'''
    with open(SCH_PATH, 'w') as f:
        f.write(sch_output)
    print(f"Schematic written to {SCH_PATH}")

# ==============================================================================
# PCB LAYOUT GENERATION
# ==============================================================================
def build_pcb():
    print("Building PCB layout...")
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # Define Nets
    net_dict = {}
    def get_or_create_net(name):
        if name in net_dict:
            return net_dict[name]
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        net_dict[name] = net
        return net

    net_gnd = get_or_create_net("GND")
    net_vcc = get_or_create_net("+3.3V")
    net_rf_sig = get_or_create_net("RF_SIG")
    net_mux_en = get_or_create_net("MUX_EN")
    net_s0 = get_or_create_net("MUX_S0")
    net_s1 = get_or_create_net("MUX_S1")
    net_s2 = get_or_create_net("MUX_S2")
    net_s3 = get_or_create_net("MUX_S3")
    net_sck = get_or_create_net("SPI_SCK")
    net_miso = get_or_create_net("SPI_MISO")
    net_mosi = get_or_create_net("SPI_MOSI")
    net_cs = get_or_create_net("SPI_CS")
    net_irq = get_or_create_net("NFC_IRQ")
    net_rst = get_or_create_net("NFC_RST")
    net_sda = get_or_create_net("I2C_SDA")
    net_scl = get_or_create_net("I2C_SCL")
    net_aux = get_or_create_net("GPIO_AUX")

    ch_nets = [get_or_create_net(f"RF_CH{k}") for k in range(16)]
    coil_nets = [get_or_create_net(f"RF_COIL_{k+1}") for k in range(16)]

    # 1. Board Outline (100mm x 100mm)
    outline_pts = [
        (0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)
    ]
    for i in range(len(outline_pts)):
        p1 = pcbnew.VECTOR2I_MM(outline_pts[i][0], outline_pts[i][1])
        p2 = pcbnew.VECTOR2I_MM(outline_pts[(i+1)%4][0], outline_pts[(i+1)%4][1])
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(p1)
        seg.SetEnd(p2)
        seg.SetWidth(int(0.15 * 1e6))
        board.Add(seg)

    # 2. 4x M3 Mounting Holes
    hole_locs = [(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]
    for idx, (hx, hy) in enumerate(hole_locs):
        fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        for pad in fp_h.Pads():
            pad.SetNet(net_gnd)
        board.Add(fp_h)

    # 3. U1 (CD74HC4067M SOIC-24)
    fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
    fp_u1.SetReference("U1")
    fp_u1.SetValue("CD74HC4067M")
    u1_pos = (50.0, 11.0)
    fp_u1.SetPosition(pcbnew.VECTOR2I_MM(u1_pos[0], u1_pos[1]))

    u1_pad_nets = {
        "1": net_rf_sig,
        "2": ch_nets[7], "3": ch_nets[6], "4": ch_nets[5], "5": ch_nets[4],
        "6": ch_nets[3], "7": ch_nets[2], "8": ch_nets[1], "9": ch_nets[0],
        "10": net_s0, "11": net_s1, "12": net_gnd,
        "13": net_s3, "14": net_s2, "15": net_mux_en,
        "16": ch_nets[15], "17": ch_nets[14], "18": ch_nets[13], "19": ch_nets[12],
        "20": ch_nets[11], "21": ch_nets[10], "22": ch_nets[9], "23": ch_nets[8],
        "24": net_vcc
    }
    for pad in fp_u1.Pads():
        p_num = pad.GetNumber()
        if p_num in u1_pad_nets:
            pad.SetNet(u1_pad_nets[p_num])
    board.Add(fp_u1)

    # 4. Connectors
    # J1: Host Header (2x10) at (20.0, 10.0)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(20.0, 10.0))
    j1_pad_nets = {
        "1": net_vcc, "2": net_vcc,
        "3": net_s0,  "4": net_sck,
        "5": net_s1,  "6": net_miso,
        "7": net_s2,  "8": net_mosi,
        "9": net_s3,  "10": net_cs,
        "11": net_mux_en, "12": net_irq,
        "13": net_sda, "14": net_rst,
        "15": net_scl, "16": net_aux,
        "17": net_gnd, "18": net_gnd,
        "19": net_gnd, "20": net_gnd
    }
    for pad in fp_j1.Pads():
        p_num = pad.GetNumber()
        if p_num in j1_pad_nets:
            pad.SetNet(j1_pad_nets[p_num])
    board.Add(fp_j1)

    # J2: NFC Module Header (1x10) at (80.0, 10.0)
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_Module_Header")
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(80.0, 10.0))
    j2_pad_nets = {
        "1": net_rf_sig, "2": net_gnd,
        "3": net_vcc,    "4": net_gnd,
        "5": net_sck,    "6": net_miso,
        "7": net_mosi,   "8": net_cs,
        "9": net_irq,    "10": net_rst
    }
    for pad in fp_j2.Pads():
        p_num = pad.GetNumber()
        if p_num in j2_pad_nets:
            pad.SetNet(j2_pad_nets[p_num])
    board.Add(fp_j2)

    # J3: SMA RF Test Port at (64.0, 7.5)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("SMA_RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(64.0, 7.5))
    for pad in fp_j3.Pads():
        if pad.GetNumber() == "1":
            pad.SetNet(net_rf_sig)
        else:
            pad.SetNet(net_gnd)
    board.Add(fp_j3)

    # 5. Decoupling & Pull-up/down Components
    # C17 (0.1uF 0603) near U1 VCC (pin 24)
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(45.0, 5.0))
    for pad in fp_c17.Pads():
        pad.SetNet(net_vcc if pad.GetNumber() == "1" else net_gnd)
    board.Add(fp_c17)

    # C18 (10uF 0805)
    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(40.0, 5.0))
    for pad in fp_c18.Pads():
        pad.SetNet(net_vcc if pad.GetNumber() == "1" else net_gnd)
    board.Add(fp_c18)

    # R17 (10k 0603 pullup on EN)
    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(55.0, 5.0))
    for pad in fp_r17.Pads():
        pad.SetNet(net_vcc if pad.GetNumber() == "1" else net_mux_en)
    board.Add(fp_r17)

    # R18..R21 (100k 0603 pulldowns on S0..S3)
    s_nets = [net_s0, net_s1, net_s2, net_s3]
    for idx, s_net in enumerate(s_nets):
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{18+idx}")
        fp_r.SetValue("100k")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(46.0 + idx * 3.0, 18.0))
        for pad in fp_r.Pads():
            pad.SetNet(s_net if pad.GetNumber() == "1" else net_gnd)
        board.Add(fp_r)

    # 6. Tuning Capacitors C1..C16 (100pF 0603) and Damping Resistors R1..R16 (3.3R 0603)
    # Left Bank: Channels 0 to 7 (between J1 and U1)
    # Right Bank: Channels 8 to 15 (between U1 and J2)
    left_positions = [
        (33.0, 5.0), (36.0, 5.0), (33.0, 8.5), (36.0, 8.5),
        (33.0, 12.0), (36.0, 12.0), (33.0, 15.5), (36.0, 15.5)
    ]
    right_positions = [
        (58.0, 14.5), (61.5, 14.5), (65.0, 14.5), (68.5, 14.5),
        (58.0, 18.0), (61.5, 18.0), (65.0, 18.0), (68.5, 18.0)
    ]

    for k in range(16):
        cell_id = k + 1
        pos = left_positions[k] if k < 8 else right_positions[k - 8]
        cx, cy = pos[0], pos[1]
        rx, ry = pos[0] + 1.6, pos[1]

        # C_k
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, cy))
        for pad in fp_c.Pads():
            pad.SetNet(ch_nets[k] if pad.GetNumber() == "1" else net_gnd)
        board.Add(fp_c)

        # R_k
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(rx, ry))
        for pad in fp_r.Pads():
            pad.SetNet(ch_nets[k] if pad.GetNumber() == "1" else coil_nets[k])
        board.Add(fp_r)

    # 7. 4x4 Planar Spiral Coils L1..L16
    col_x = [21.5, 40.5, 59.5, 78.5]
    row_y = [32.0, 51.0, 70.0, 89.0]
    cell_letters = ["A", "B", "C", "D"]

    coil_coords = []
    for r_idx in range(4):
        for c_idx in range(4):
            k = r_idx * 4 + c_idx
            cell_id = k + 1
            xc = col_x[c_idx]
            yc = row_y[r_idx]
            coil_coords.append((xc, yc))
            cell_name = f"{cell_letters[c_idx]}{r_idx+1}"

            fp_l = pcbnew.FOOTPRINT(board)
            fp_l.SetReference(f"L{cell_id}")
            fp_l.SetValue("1.26uH")
            fp_l.AddNetTiePadGroup('1, 2')
            fp_l.SetPosition(pcbnew.VECTOR2I_MM(xc, yc))

            # Pad 1 (SMD on F.Cu at top-left)
            p1 = pcbnew.PAD(fp_l)
            p1.SetNumber("1")
            p1.SetName("1")
            p1.SetShape(pcbnew.PAD_SHAPE_RECT)
            p1.SetSize(pcbnew.VECTOR2I_MM(0.8, 0.8))
            p1.SetPosition(pcbnew.VECTOR2I_MM(-8.625, -8.625))
            p1.SetLayer(pcbnew.F_Cu)
            p1.SetNet(coil_nets[k])
            fp_l.Add(p1)

            # Pad 2 (PTH at center inner end)
            p2 = pcbnew.PAD(fp_l)
            p2.SetNumber("2")
            p2.SetName("2")
            p2.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            p2.SetSize(pcbnew.VECTOR2I_MM(0.6, 0.6))
            p2.SetDrillSize(pcbnew.VECTOR2I_MM(0.3, 0.3))
            p2.SetPosition(pcbnew.VECTOR2I_MM(-5.125, -5.125))
            p2.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            p2.SetLayerSet(p2.PTHMask())
            p2.SetNet(net_gnd)
            fp_l.Add(p2)

            # 7-Turn Spiral Traces on F_Cu
            turns = 7
            d_out = 17.5
            trace_w = 0.25
            space = 0.25
            pitch = trace_w + space
            r0 = d_out / 2.0 - trace_w / 2.0

            x = -r0
            y = -r0
            pts = [(x, y)]
            for turn in range(turns):
                x_right = r0 - turn * pitch
                y_bot   = r0 - turn * pitch
                x_left_next = -r0 + (turn + 1) * pitch
                y_top_next  = -r0 + (turn + 1) * pitch
                pts.append((x_right, y))
                y = y_bot
                pts.append((x_right, y))
                x = x_left_next
                pts.append((x, y))
                y = y_top_next
                pts.append((x, y))

            for seg_i in range(len(pts) - 1):
                seg = pcbnew.PCB_SHAPE(fp_l)
                seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
                seg.SetLayer(pcbnew.F_Cu)
                seg.SetStart(pcbnew.VECTOR2I_MM(pts[seg_i][0], pts[seg_i][1]))
                seg.SetEnd(pcbnew.VECTOR2I_MM(pts[seg_i+1][0], pts[seg_i+1][1]))
                seg.SetWidth(int(trace_w * 1e6))
                fp_l.Add(seg)

            # 19mm x 19mm Cell Boundary on F_SilkS
            s19 = 19.0 / 2.0
            cell_box = [
                ((-s19, -s19), (s19, -s19)), ((s19, -s19), (s19, s19)),
                ((s19, s19), (-s19, s19)), ((-s19, s19), (-s19, -s19))
            ]
            for pA, pB in cell_box:
                line = pcbnew.PCB_SHAPE(fp_l)
                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                line.SetLayer(pcbnew.F_SilkS)
                line.SetStart(pcbnew.VECTOR2I_MM(pA[0], pA[1]))
                line.SetEnd(pcbnew.VECTOR2I_MM(pB[0], pB[1]))
                line.SetWidth(int(0.12 * 1e6))
                fp_l.Add(line)

            # Cell text label inside coil
            txt = pcbnew.PCB_TEXT(fp_l)
            txt.SetText(f"{cell_name} (I{k})")
            txt.SetLayer(pcbnew.F_SilkS)
            txt.SetPosition(pcbnew.VECTOR2I_MM(0, 0))
            txt.SetTextSize(pcbnew.VECTOR2I_MM(1.2, 1.2))
            fp_l.Add(txt)

            board.Add(fp_l)

            # B.Cu Return Trace from coil center via (Pad 2) outward to ground
            ret_trk = pcbnew.PCB_TRACK(board)
            ret_trk.SetStart(pcbnew.VECTOR2I_MM(xc - 5.125, yc - 5.125))
            ret_trk.SetEnd(pcbnew.VECTOR2I_MM(xc - 9.0, yc - 5.125))
            ret_trk.SetWidth(int(0.35 * 1e6))
            ret_trk.SetLayer(pcbnew.B_Cu)
            ret_trk.SetNet(net_gnd)
            board.Add(ret_trk)

            # Feed Trace from R_k to Coil Pad 1
            feed_trk = pcbnew.PCB_TRACK(board)
            r_pos = left_positions[k] if k < 8 else right_positions[k - 8]
            feed_trk.SetStart(pcbnew.VECTOR2I_MM(r_pos[0] + 1.6, r_pos[1]))
            feed_trk.SetEnd(pcbnew.VECTOR2I_MM(xc - 8.625, yc - 8.625))
            feed_trk.SetWidth(int(0.25 * 1e6))
            feed_trk.SetLayer(pcbnew.F_Cu)
            feed_trk.SetNet(coil_nets[k])
            board.Add(feed_trk)

    # 8. RF_SIG Microstrip (J2 & J3 to U1 COM)
    # J2 pin 1 at (75.5, 10.0) -> U1 COM at (43.0, 7.5)
    rf_trk1 = pcbnew.PCB_TRACK(board)
    rf_trk1.SetStart(pcbnew.VECTOR2I_MM(74.0, 10.0))
    rf_trk1.SetEnd(pcbnew.VECTOR2I_MM(64.0, 7.5))
    rf_trk1.SetWidth(int(0.5 * 1e6))
    rf_trk1.SetLayer(pcbnew.F_Cu)
    rf_trk1.SetNet(net_rf_sig)
    board.Add(rf_trk1)

    rf_trk2 = pcbnew.PCB_TRACK(board)
    rf_trk2.SetStart(pcbnew.VECTOR2I_MM(64.0, 7.5))
    rf_trk2.SetEnd(pcbnew.VECTOR2I_MM(44.0, 7.5))
    rf_trk2.SetWidth(int(0.5 * 1e6))
    rf_trk2.SetLayer(pcbnew.F_Cu)
    rf_trk2.SetNet(net_rf_sig)
    board.Add(rf_trk2)

    # 9. In1.Cu Ground Plane with 16 Coil Cutouts
    zone_gnd_in1 = pcbnew.ZONE(board)
    zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
    zone_gnd_in1.SetNet(net_gnd)
    poly_in1 = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_in1.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_in1.SetClosed(True)
    zone_gnd_in1.AddPolygon(poly_in1)
    board.Add(zone_gnd_in1)

    # 16 Anti-copper Keepout Cutouts on In1.Cu (18.5mm x 18.5mm under each coil)
    cut_half = 18.5 / 2.0
    for xc, yc in coil_coords:
        cutout = pcbnew.ZONE(board)
        cutout.SetLayer(pcbnew.In1_Cu)
        cutout.SetIsRuleArea(True)
        cutout.SetDoNotAllowZoneFills(True)
        cut_poly = pcbnew.SHAPE_LINE_CHAIN()
        for cdx, cdy in [(-cut_half, -cut_half), (cut_half, -cut_half),
                         (cut_half, cut_half), (-cut_half, cut_half)]:
            cut_poly.Append(pcbnew.VECTOR2I_MM(xc + cdx, yc + cdy))
        cut_poly.SetClosed(True)
        cutout.AddPolygon(cut_poly)
        board.Add(cutout)

    # 10. In2.Cu Power Rail and Digital Control Routing
    zone_vcc_in2 = pcbnew.ZONE(board)
    zone_vcc_in2.SetLayer(pcbnew.In2_Cu)
    zone_vcc_in2.SetNet(net_vcc)
    poly_in2 = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(10.0, 2.0), (90.0, 2.0), (90.0, 20.0), (10.0, 20.0)]:
        poly_in2.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_in2.SetClosed(True)
    zone_vcc_in2.AddPolygon(poly_in2)
    board.Add(zone_vcc_in2)

    # 11. B.Cu Bottom Ground Shield Plane
    zone_bcu = pcbnew.ZONE(board)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNet(net_gnd)
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    board.Add(zone_bcu)

    # 12. Silkscreen Markings & Titles on F_SilkS
    def add_board_text(text, x, y, size=1.5):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
        board.Add(txt)

    add_board_text("SMART CROSSWORD BOARD - 4x4 NFC TEST MATRIX", 50.0, 2.5, 1.4)
    add_board_text("REV 1.0 | 13.56 MHz LC RESONANT", 50.0, 21.0, 1.0)
    add_board_text("L=1.26uH (7T) | C=100pF C0G | R=3.3R | Q~25", 50.0, 97.0, 1.1)

    # Column markers (A, B, C, D)
    for idx, cx in enumerate(col_x):
        add_board_text(cell_letters[idx], cx, 21.5, 1.6)

    # Row markers (1, 2, 3, 4)
    for idx, ry in enumerate(row_y):
        add_board_text(str(idx + 1), 9.0, ry, 1.6)

    board.Save(PCB_PATH)
    print(f"PCB successfully generated and saved to {PCB_PATH}")

if __name__ == '__main__':
    build_schematic()
    build_pcb()
