#!/usr/bin/env python3
"""
Accurate schematic generator for test_grid_4x4.kicad_sch
"""
import uuid
import re

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
    # Returns dict: pin_num -> (dx, dy) where dy is already inverted for KiCad canvas (+Y down)
    pattern = re.compile(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\).*?\(name\s+\"([^\"]*)\".*?\(number\s+\"([^\"]*)\"', re.DOTALL)
    pin_map = {}
    for m in pattern.finditer(sym_str):
        x, y, rot, name, num = m.groups()
        # In KiCad symbol definitions, +Y is up, but on schematic sheet +Y is down!
        pin_map[num] = (float(x), -float(y), name)
    return pin_map

def main():
    root_uuid = gen_uuid()
    
    # Load required symbol definitions
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

    # Get exact pin offsets
    pins_mux = get_symbol_pin_offsets(sym_mux)
    pins_j1 = get_symbol_pin_offsets(sym_j1)
    pins_j2 = get_symbol_pin_offsets(sym_j2)
    pins_sma = get_symbol_pin_offsets(sym_sma)
    pins_c = get_symbol_pin_offsets(sym_c)
    pins_r = get_symbol_pin_offsets(sym_r)
    pins_l = get_symbol_pin_offsets(sym_l)
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
        rename_sym(sym_gnd, 'GND', 'power:GND')
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
    u1_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "74xx:CD74HC4067M")
\t\t(at {u1_x:.3f} {u1_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{u1_uuid}")
\t\t(property "Reference" "U1" (at {u1_x-8.89:.3f} {u1_y-22.86:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "CD74HC4067M" (at {u1_x+1.27:.3f} {u1_y-22.86:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm" (at {u1_x:.3f} {u1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "http://www.ti.com/lit/ds/symlink/cd74hc4067.pdf" (at {u1_x:.3f} {u1_y:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 25)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "U1") (unit 1))))
\t)''')

    # Connect U1 pins
    connect_pin_to_net(u1_x, u1_y, pins_mux, 1, "RF_SIG", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 24, "+3.3V", 0, -5.08, 90)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 12, "GND", 0, 5.08, 270)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 10, "MUX_S0", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 11, "MUX_S1", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 14, "MUX_S2", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 13, "MUX_S3", -5.08, 0, 180)
    connect_pin_to_net(u1_x, u1_y, pins_mux, 15, "MUX_EN", -5.08, 0, 180)

    # Channels I0..I15
    mux_pins_order = [9, 8, 7, 6, 5, 4, 3, 2, 23, 22, 21, 20, 19, 18, 17, 16]
    for ch_idx, pin_num in enumerate(mux_pins_order):
        connect_pin_to_net(u1_x, u1_y, pins_mux, pin_num, f"RF_CH{ch_idx}", 5.08, 0, 0)

    # 2. 16 LC resonant tanks: C1..C16, R1..R16, L1..L16
    tank_base_x = 200.0
    tank_base_y = 30.0
    cell_to_mux_ch = {
        1: 0,   5: 1,   9: 2,  13: 3,   # Col A: A1, A2, A3, A4 -> CH0, CH1, CH2, CH3
        2: 4,   6: 5,  10: 6,  14: 7,   # Col B: B1, B2, B3, B4 -> CH4, CH5, CH6, CH7
        3: 11,  7: 10, 11: 9,  15: 8,   # Col C: C1, C2, C3, C4 -> CH11, CH10, CH9, CH8
        4: 15,  8: 14, 12: 13, 16: 12,  # Col D: D1, D2, D3, D4 -> CH15, CH14, CH13, CH12
    }
    for k in range(16):
        cell_id = k + 1
        mux_ch = cell_to_mux_ch[cell_id]
        ty = tank_base_y + k * 17.78

        # R_k (3.3 ohm)
        rx, ry = tank_base_x, ty
        r_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at {rx:.3f} {ry:.3f} 90)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{r_uuid}")
\t\t(property "Reference" "R{cell_id}" (at {rx:.3f} {ry-2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "3.3" (at {rx:.3f} {ry+2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {rx:.3f} {ry:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "R{cell_id}") (unit 1))))
\t)''')
        # At rot 90:
        # pin 1: (ry + y_pin, rx + x_pin) -> (-3.81, 0) -> (rx - 3.81, ry)
        # pin 2: (rx + 3.81, ry)
        add_wire(rx - 3.81, ry, rx - 7.62, ry)
        add_label(f"RF_CH{mux_ch}", rx - 7.62, ry, 180)

        # C_k (100pF C0G)
        cx, cy = rx - 5.08, ry + 7.62
        c_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.3f} {cy:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c_uuid}")
\t\t(property "Reference" "C{cell_id}" (at {cx+2.54:.3f} {cy-1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "100pF" (at {cx+2.54:.3f} {cy+1.27:.3f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {cx:.3f} {cy:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C{cell_id}") (unit 1))))
\t)''')
        # C pin 1 is at cy - 3.81, pin 2 is at cy + 3.81
        add_wire(cx, cy - 3.81, cx, ry)
        add_wire(cx, ry, rx - 3.81, ry)
        add_wire(cx, cy + 3.81, cx, cy + 6.35)
        add_label("GND", cx, cy + 6.35, 270)

        # L_k (1.26uH Planar Coil)
        lx, ly = rx + 17.78, ry
        l_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:L")
\t\t(at {lx:.3f} {ly:.3f} 90)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{l_uuid}")
\t\t(property "Reference" "L{cell_id}" (at {lx:.3f} {ly-2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "1.26uH" (at {lx:.3f} {ly+2.54:.3f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "NFC_Coil_17.5x17.5mm" (at {lx:.3f} {ly:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "~" (at {lx:.3f} {ly:.3f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "L{cell_id}") (unit 1))))
\t)''')
        # At rot 90: pin 1 is at lx - 3.81, ly; pin 2 is at lx + 3.81, ly
        add_wire(rx + 3.81, ry, lx - 3.81, ry)
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
    j1_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector_Generic:Conn_02x10_Odd_Even")
\t\t(at {j1_x:.3f} {j1_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{j1_uuid}")
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
        7: "MUX_S3", 8: "SPI_MOSI",
        9: "MUX_S2", 10: "SPI_CS",
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
    j2_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector_Generic:Conn_01x10")
\t\t(at {j2_x:.3f} {j2_y:.3f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{j2_uuid}")
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

    # Assemble complete kicad_sch
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
    sch_path = '/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4/test_grid_4x4.kicad_sch'
    with open(sch_path, 'w') as f:
        f.write(sch_output)
    print("Successfully generated test_grid_4x4.kicad_sch")

if __name__ == '__main__':
    main()
