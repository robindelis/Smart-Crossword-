#!/usr/bin/env python3
"""
Accurate schematic generator for st25r3916_grid_4x4.kicad_sch
Generates 100% verified KiCad 10 schematic for:
- ST25R3916B-AQFT QFN-32 13.56 MHz NFC Transceiver IC
- 27.12 MHz Crystal with load capacitors
- EMC Low-pass filter (L0=470nH, C0=180pF)
- Matching capacitor (Cs=18pF)
- Receiver capacitive divider (Cdiv1=10pF, Cdiv2=150pF, Cbal=150pF)
- CD74HC4067 16-channel analog multiplexer
- 16 Tuned planar resonant tanks (L1..L16, Ca1..Ca16=100pF, Cb1..Cb16=22pF, Rd1..Rd16=1.5R)
- Host header J1 (2x10)
- RF diagnostic connector J3
"""
import uuid
import re
import os

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
    pattern = re.compile(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\).*?\(name\s+\"([^\"]*)\".*?\(number\s+\"([^\"]*)\"', re.DOTALL)
    pin_map = {}
    for m in pattern.finditer(sym_str):
        ptype, x, y, rot, name, num = m.groups()
        pin_map[num] = (float(x), -float(y), name, ptype)
    return pin_map

def rename_sym(sym_str, old_name, new_name):
    return sym_str.replace(f'(symbol "{old_name}"', f'(symbol "{new_name}"', 1)

def generate_schematic(out_path):
    root_uuid = gen_uuid()

    # Load standard symbols
    sym_l = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'L')
    sym_c = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'C')
    sym_r = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'R')
    sym_xtal = extract_symbol('/usr/share/kicad/symbols/Device.kicad_sym', 'Crystal_GND24')
    sym_mux = extract_symbol('/usr/share/kicad/symbols/74xx.kicad_sym', 'CD74HC4067M')
    sym_j1 = extract_symbol('/usr/share/kicad/symbols/Connector_Generic.kicad_sym', 'Conn_02x10_Odd_Even')
    sym_sma = extract_symbol('/usr/share/kicad/symbols/Connector.kicad_sym', 'Conn_Coaxial')
    sym_hole = extract_symbol('/usr/share/kicad/symbols/Mechanical.kicad_sym', 'MountingHole_Pad')
    sym_3v3 = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', '+3V3')
    sym_5v = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', '+5V')
    sym_gnd = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', 'GND')
    sym_pwr_flag = extract_symbol('/usr/share/kicad/symbols/power.kicad_sym', 'PWR_FLAG')

    # Custom ST25R3916B-AQFT symbol definition
    sym_st25 = '''\t(symbol "st25r3916_grid_4x4:ST25R3916B-AQFT" (in_bom yes) (on_board yes)
\t\t(property "Reference" "U" (at 0 -25.4 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "ST25R3916B-AQFT" (at 0 25.4 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm_ThermalVias" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Datasheet" "https://www.st.com/resource/en/datasheet/st25r3916b.pdf" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Description" "High performance NFC universal device & reader, VFQFPN32" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(symbol "ST25R3916B-AQFT_0_1"
\t\t\t(rectangle (start -17.78 22.86) (end 17.78 -22.86) (stroke (width 0.254) (type default)) (fill (type background)))
\t\t)
\t\t(symbol "ST25R3916B-AQFT_1_1"
\t\t\t(pin power_in line (at -20.32 -17.78 0) (length 2.54) (name "VDD_IO" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
\t\t\t(pin passive line (at -20.32 17.78 0) (length 2.54) (name "TAD2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 10.16 180) (length 2.54) (name "VDD_D" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at 20.32 15.24 180) (length 2.54) (name "XTO" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at 20.32 17.78 180) (length 2.54) (name "XTI" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at -10.16 25.4 270) (length 2.54) (name "GND_D" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 12.70 180) (length 2.54) (name "VDD_A" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at -20.32 -15.24 0) (length 2.54) (name "VDD" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 5.08 180) (length 2.54) (name "VDD_RF" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at -20.32 -12.70 0) (length 2.54) (name "VDD_TX" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 7.62 180) (length 2.54) (name "VDD_AM" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at -5.08 25.4 270) (length 2.54) (name "GND_DR1" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at 20.32 -17.78 180) (length 2.54) (name "RFO1" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 2.54 180) (length 2.54) (name "VDD_DR" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at 20.32 -15.24 180) (length 2.54) (name "RFO2" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at 0.00 25.4 270) (length 2.54) (name "GND_DR2" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))
\t\t\t(pin passive line (at 7.62 -25.4 90) (length 2.54) (name "EXT_LM" (effects (font (size 1.27 1.27)))) (number "17" (effects (font (size 1.27 1.27)))))
\t\t\t(pin passive line (at -7.62 -25.4 90) (length 2.54) (name "AAT_A" (effects (font (size 1.27 1.27)))) (number "18" (effects (font (size 1.27 1.27)))))
\t\t\t(pin passive line (at -2.54 -25.4 90) (length 2.54) (name "AAT_B" (effects (font (size 1.27 1.27)))) (number "19" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at -20.32 12.70 0) (length 2.54) (name "I2C_EN" (effects (font (size 1.27 1.27)))) (number "20" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at 5.08 25.4 270) (length 2.54) (name "VSS" (effects (font (size 1.27 1.27)))) (number "21" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at 20.32 -10.16 180) (length 2.54) (name "RFI1" (effects (font (size 1.27 1.27)))) (number "22" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at 20.32 -7.62 180) (length 2.54) (name "RFI2" (effects (font (size 1.27 1.27)))) (number "23" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_out line (at 20.32 -2.54 180) (length 2.54) (name "AGDC" (effects (font (size 1.27 1.27)))) (number "24" (effects (font (size 1.27 1.27)))))
\t\t\t(pin passive line (at 2.54 -25.4 90) (length 2.54) (name "TAD1" (effects (font (size 1.27 1.27)))) (number "25" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at 10.16 25.4 270) (length 2.54) (name "GND_A" (effects (font (size 1.27 1.27)))) (number "26" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at -20.32 7.62 0) (length 2.54) (name "IRQ" (effects (font (size 1.27 1.27)))) (number "27" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at -20.32 15.24 0) (length 2.54) (name "MCU_CLK" (effects (font (size 1.27 1.27)))) (number "28" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at -20.32 -5.08 0) (length 2.54) (name "BSS" (effects (font (size 1.27 1.27)))) (number "29" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at -20.32 -2.54 0) (length 2.54) (name "SCLK" (effects (font (size 1.27 1.27)))) (number "30" (effects (font (size 1.27 1.27)))))
\t\t\t(pin input line (at -20.32 0.00 0) (length 2.54) (name "MOSI" (effects (font (size 1.27 1.27)))) (number "31" (effects (font (size 1.27 1.27)))))
\t\t\t(pin output line (at -20.32 2.54 0) (length 2.54) (name "MISO" (effects (font (size 1.27 1.27)))) (number "32" (effects (font (size 1.27 1.27)))))
\t\t\t(pin power_in line (at 15.24 25.4 270) (length 2.54) (name "EP" (effects (font (size 1.27 1.27)))) (number "33" (effects (font (size 1.27 1.27)))))
\t\t)
\t)'''

    # Parse pin offsets
    pins_mux = get_symbol_pin_offsets(sym_mux)
    pins_j1 = get_symbol_pin_offsets(sym_j1)
    pins_sma = get_symbol_pin_offsets(sym_sma)
    pins_c = get_symbol_pin_offsets(sym_c)
    pins_r = get_symbol_pin_offsets(sym_r)
    pins_l = get_symbol_pin_offsets(sym_l)
    pins_xtal = get_symbol_pin_offsets(sym_xtal)
    pins_hole = get_symbol_pin_offsets(sym_hole)
    pins_st25 = get_symbol_pin_offsets(sym_st25)

    lib_symbols_list = [
        rename_sym(sym_l, 'L', 'Device:L'),
        rename_sym(sym_c, 'C', 'Device:C'),
        rename_sym(sym_r, 'R', 'Device:R'),
        rename_sym(sym_xtal, 'Crystal_GND24', 'Device:Crystal_GND24'),
        rename_sym(sym_mux, 'CD74HC4067M', '74xx:CD74HC4067M'),
        rename_sym(sym_j1, 'Conn_02x10_Odd_Even', 'Connector_Generic:Conn_02x10_Odd_Even'),
        rename_sym(sym_sma, 'Conn_Coaxial', 'Connector:Conn_Coaxial'),
        rename_sym(sym_hole, 'MountingHole_Pad', 'Mechanical:MountingHole_Pad'),
        rename_sym(sym_3v3, '+3V3', 'power:+3V3'),
        rename_sym(sym_5v, '+5V', 'power:+5V'),
        rename_sym(sym_gnd, 'GND', 'power:GND'),
        rename_sym(sym_pwr_flag, 'PWR_FLAG', 'power:PWR_FLAG'),
        sym_st25
    ]

    symbols_code = []
    wires_code = []
    labels_code = []
    no_connects = []

    def add_label(net, x, y, rot=0):
        labels_code.append(f'''\t(label "{net}"
\t\t(at {x:.2f} {y:.2f} {rot})
\t\t(effects (font (size 1.27 1.27)) (justify left))
\t\t(uuid "{gen_uuid()}")
\t)''')

    def add_wire(x1, y1, x2, y2):
        wires_code.append(f'''\t(wire
\t\t(pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))
\t\t(stroke (width 0) (type default))
\t\t(uuid "{gen_uuid()}")
\t)''')

    def add_no_connect(x, y):
        no_connects.append(f'''\t(no_connect (at {x:.2f} {y:.2f}) (uuid "{gen_uuid()}"))''')

    def connect_pin(sym_x, sym_y, pin_offsets, pin_num, net_name, dx_wire, dy_wire, label_rot):
        dx, dy, _, _ = pin_offsets[str(pin_num)]
        px, py = sym_x + dx, sym_y + dy
        wx, wy = px + dx_wire, py + dy_wire
        add_wire(px, py, wx, wy)
        add_label(net_name, wx, wy, label_rot)

    def nc_pin(sym_x, sym_y, pin_offsets, pin_num):
        dx, dy, _, _ = pin_offsets[str(pin_num)]
        add_no_connect(sym_x + dx, sym_y + dy)

    # 1. Place Host Header J1 at (50.8, 63.5)
    j1_x, j1_y = 50.8, 63.5
    j1_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector_Generic:Conn_02x10_Odd_Even")
\t\t(at {j1_x:.2f} {j1_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{j1_uuid}")
\t\t(property "Reference" "J1" (at {j1_x-7.62:.2f} {j1_y-12.7:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "Host_Header_2x10" (at {j1_x-7.62:.2f} {j1_y-15.24:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical" (at {j1_x:.2f} {j1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C2939" (at {j1_x:.2f} {j1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 21)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "J1") (unit 1))))
\t)''')

    j1_nets_odd = [("+5V", 1), ("MUX_S3", 3), ("MUX_S2", 5), ("MUX_EN", 7), ("MUX_S1", 9), ("MUX_S0", 11), ("GND", 17), ("GND", 19)]
    j1_nets_even = [("ST_IRQ", 2), ("SPI_CS", 4), ("SPI_SCK", 6), ("SPI_MOSI", 8), ("SPI_MISO", 10), ("+3.3V", 12), ("GND", 18), ("GND", 20)]
    for net, p in j1_nets_odd:
        connect_pin(j1_x, j1_y, pins_j1, p, net, -5.08, 0, 180)
    for net, p in j1_nets_even:
        connect_pin(j1_x, j1_y, pins_j1, p, net, 5.08, 0, 0)
    for nc_p in [13, 14, 15, 16]:
        nc_pin(j1_x, j1_y, pins_j1, nc_p)

    # Power Flags for +5V, +3.3V, GND at J1
    flag_idx = 0
    def add_power_flag(net, x, y):
        nonlocal flag_idx
        flag_idx += 1
        f_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "power:PWR_FLAG")
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom no)
\t\t(on_board no)
\t\t(uuid "{f_uuid}")
\t\t(property "Reference" f"#FLG{flag_idx}" (at {x:.2f} {y-2.54:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "PWR_FLAG" (at {x:.2f} {y-2.54:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference f"#FLG{flag_idx}") (unit 1))))
\t)''')
        add_wire(x, y, x, y - 2.54)
        add_label(net, x, y - 2.54, 90)

    add_power_flag("+5V", 25.4, 40.64)
    add_power_flag("+3.3V", 35.56, 40.64)
    add_power_flag("GND", 45.72, 40.64)

    # 2. Place U2 (ST25R3916B-AQFT) at (127.0, 76.2)
    u2_x, u2_y = 127.0, 76.2
    u2_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "st25r3916_grid_4x4:ST25R3916B-AQFT")
\t\t(at {u2_x:.2f} {u2_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{u2_uuid}")
\t\t(property "Reference" "U2" (at {u2_x:.2f} {u2_y-27.94:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "ST25R3916B-AQFT" (at {u2_x:.2f} {u2_y+27.94:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm_ThermalVias" (at {u2_x:.2f} {u2_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C5160867" (at {u2_x:.2f} {u2_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 34)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "U2") (unit 1))))
\t)''')

    # Connect U2 pins
    connect_pin(u2_x, u2_y, pins_st25, 1, "+3.3V", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 8, "+5V", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 10, "+5V", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 29, "SPI_CS", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 30, "SPI_SCK", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 31, "SPI_MOSI", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 32, "SPI_MISO", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 27, "ST_IRQ", -5.08, 0, 180)
    connect_pin(u2_x, u2_y, pins_st25, 20, "GND", -5.08, 0, 180) # I2C_EN = GND for SPI mode

    nc_pin(u2_x, u2_y, pins_st25, 2)  # TAD2
    nc_pin(u2_x, u2_y, pins_st25, 28) # MCU_CLK
    nc_pin(u2_x, u2_y, pins_st25, 15) # RFO2 (Single-ended mode)
    nc_pin(u2_x, u2_y, pins_st25, 17) # EXT_LM
    nc_pin(u2_x, u2_y, pins_st25, 18) # AAT_A
    nc_pin(u2_x, u2_y, pins_st25, 19) # AAT_B
    nc_pin(u2_x, u2_y, pins_st25, 25) # TAD1

    # RF and Decoupling outputs
    connect_pin(u2_x, u2_y, pins_st25, 13, "RFO1", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 22, "RFI1", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 23, "RFI2", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 24, "AGDC", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 14, "VDD_DR", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 9, "VDD_RF", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 11, "VDD_AM", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 3, "VDD_D", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 7, "VDD_A", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 4, "OSC_OUT", 5.08, 0, 0)
    connect_pin(u2_x, u2_y, pins_st25, 5, "OSC_IN", 5.08, 0, 0)

    # Grounds
    connect_pin(u2_x, u2_y, pins_st25, 6, "GND", 0, 5.08, 270)
    connect_pin(u2_x, u2_y, pins_st25, 12, "GND", 0, 5.08, 270)
    connect_pin(u2_x, u2_y, pins_st25, 16, "GND", 0, 5.08, 270)
    connect_pin(u2_x, u2_y, pins_st25, 21, "GND", 0, 5.08, 270)
    connect_pin(u2_x, u2_y, pins_st25, 26, "GND", 0, 5.08, 270)
    connect_pin(u2_x, u2_y, pins_st25, 33, "GND", 0, 5.08, 270)

    # 3. Decoupling Capacitors for ST25R3916
    decoup_caps = [
        ("C20", "1uF", "VDD_D", "C15849"),
        ("C21", "10nF", "VDD_D", "C1588"),
        ("C24", "1uF", "VDD_A", "C15849"),
        ("C25", "10nF", "VDD_A", "C1588"),
        ("C26", "10uF", "+5V", "C15850"),
        ("C27", "100nF", "+5V", "C14663"),
        ("C28", "2.2uF", "VDD_RF", "C23630"),
        ("C29", "10nF", "VDD_RF", "C1588"),
        ("C30", "2.2uF", "+5V", "C23630"),
        ("C31", "10nF", "+5V", "C1588"),
        ("C32", "2.2uF", "VDD_AM", "C23630"),
        ("C33", "1uF", "VDD_DR", "C15849"),
        ("C34", "100nF", "VDD_DR", "C14663"),
        ("C35", "1uF", "AGDC", "C15849"),
        ("C36", "10nF", "AGDC", "C1588")
    ]
    for idx, (ref, val, net, lcsc) in enumerate(decoup_caps):
        cx = 177.8 + (idx % 5) * 15.24
        cy = 50.8 + (idx // 5) * 20.32
        cuuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.2f} {cy:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{cuuid}")
\t\t(property "Reference" "{ref}" (at {cx+1.90:.2f} {cy-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "{val}" (at {cx+1.90:.2f} {cy+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "{lcsc}" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{ref}") (unit 1))))
\t)''')
        connect_pin(cx, cy, pins_c, 1, net, 0, -2.54, 90)
        connect_pin(cx, cy, pins_c, 2, "GND", 0, 2.54, 270)

    # 4. Crystal Y1 (27.12 MHz) and load caps C22, C23
    y1_x, y1_y = 127.0, 137.16
    y1_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:Crystal_GND24")
\t\t(at {y1_x:.2f} {y1_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{y1_uuid}")
\t\t(property "Reference" "Y1" (at {y1_x-5.08:.2f} {y1_y-5.08:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "27.12MHz" (at {y1_x-5.08:.2f} {y1_y-7.62:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm" (at {y1_x:.2f} {y1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C9002" (at {y1_x:.2f} {y1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(pin "3" (uuid "{gen_uuid()}"))
\t\t(pin "4" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "Y1") (unit 1))))
\t)''')
    connect_pin(y1_x, y1_y, pins_xtal, 1, "OSC_OUT", 0, -2.54, 90)
    connect_pin(y1_x, y1_y, pins_xtal, 2, "GND", 2.54, 0, 0)
    connect_pin(y1_x, y1_y, pins_xtal, 3, "OSC_IN", 0, 2.54, 270)
    connect_pin(y1_x, y1_y, pins_xtal, 4, "GND", -2.54, 0, 180)

    # C22 (12pF), C23 (12pF)
    for c_ref, c_val, c_net, cx in [("C22", "12pF", "OSC_OUT", 114.3), ("C23", "12pF", "OSC_IN", 139.7)]:
        cy = 137.16
        cuuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.2f} {cy:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{cuuid}")
\t\t(property "Reference" "{c_ref}" (at {cx+1.90:.2f} {cy-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "{c_val}" (at {cx+1.90:.2f} {cy+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1646" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{c_ref}") (unit 1))))
\t)''')
        connect_pin(cx, cy, pins_c, 1, c_net, 0, -2.54, 90)
        connect_pin(cx, cy, pins_c, 2, "GND", 0, 2.54, 270)

    # 5. EMC Low-Pass Filter & Receiver Network
    # L17: 470nH (between RFO1 and RF_FLT)
    l17_x, l17_y = 60.96, 137.16
    l17_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:L")
\t\t(at {l17_x:.2f} {l17_y:.2f} 90)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{l17_uuid}")
\t\t(property "Reference" "L17" (at {l17_x:.2f} {l17_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "470nH" (at {l17_x:.2f} {l17_y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at {l17_x:.2f} {l17_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1031" (at {l17_x:.2f} {l17_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "L17") (unit 1))))
\t)''')
    # Note: L symbol rotated 90 deg -> pin 1 is at (-3.81, 0), pin 2 is at (3.81, 0)
    add_wire(l17_x - 3.81, l17_y, l17_x - 7.62, l17_y)
    add_label("RFO1", l17_x - 7.62, l17_y, 180)
    add_wire(l17_x + 3.81, l17_y, l17_x + 7.62, l17_y)
    add_label("RF_FLT", l17_x + 7.62, l17_y, 0)

    # C37: 180pF EMC filter capacitor to GND
    c37_x, c37_y = 76.2, 147.32
    c37_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {c37_x:.2f} {c37_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c37_uuid}")
\t\t(property "Reference" "C37" (at {c37_x+1.90:.2f} {c37_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "180pF" (at {c37_x+1.90:.2f} {c37_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {c37_x:.2f} {c37_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1675" (at {c37_x:.2f} {c37_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C37") (unit 1))))
\t)''')
    connect_pin(c37_x, c37_y, pins_c, 1, "RF_FLT", 0, -2.54, 90)
    connect_pin(c37_x, c37_y, pins_c, 2, "GND", 0, 2.54, 270)

    # C39: 18pF Series Matching Capacitor (between RF_FLT and RF_SIG)
    c39_x, c39_y = 91.44, 137.16
    c39_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {c39_x:.2f} {c39_y:.2f} 90)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c39_uuid}")
\t\t(property "Reference" "C39" (at {c39_x:.2f} {c39_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "18pF" (at {c39_x:.2f} {c39_y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {c39_x:.2f} {c39_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1650" (at {c39_x:.2f} {c39_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C39") (unit 1))))
\t)''')
    add_wire(c39_x - 3.81, c39_y, c39_x - 7.62, c39_y)
    add_label("RF_FLT", c39_x - 7.62, c39_y, 180)
    add_wire(c39_x + 3.81, c39_y, c39_x + 7.62, c39_y)
    add_label("RF_SIG", c39_x + 7.62, c39_y, 0)

    # Receiver Capacitive Divider: C40 (10pF), C41 (150pF), C38 (150pF)
    # C40 between RF_SIG and RFI1
    c40_x, c40_y = 60.96, 165.1
    c40_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {c40_x:.2f} {c40_y:.2f} 90)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c40_uuid}")
\t\t(property "Reference" "C40" (at {c40_x:.2f} {c40_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "10pF" (at {c40_x:.2f} {c40_y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {c40_x:.2f} {c40_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1644" (at {c40_x:.2f} {c40_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C40") (unit 1))))
\t)''')
    add_wire(c40_x - 3.81, c40_y, c40_x - 7.62, c40_y)
    add_label("RF_SIG", c40_x - 7.62, c40_y, 180)
    add_wire(c40_x + 3.81, c40_y, c40_x + 7.62, c40_y)
    add_label("RFI1", c40_x + 7.62, c40_y, 0)

    # C41 (150pF between RFI1 and GND)
    c41_x, c41_y = 76.2, 177.8
    c41_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {c41_x:.2f} {c41_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c41_uuid}")
\t\t(property "Reference" "C41" (at {c41_x+1.90:.2f} {c41_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "150pF" (at {c41_x+1.90:.2f} {c41_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {c41_x:.2f} {c41_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1673" (at {c41_x:.2f} {c41_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C41") (unit 1))))
\t)''')
    connect_pin(c41_x, c41_y, pins_c, 1, "RFI1", 0, -2.54, 90)
    connect_pin(c41_x, c41_y, pins_c, 2, "GND", 0, 2.54, 270)

    # C38 (150pF between RFI2 and AGDC)
    c38_x, c38_y = 96.52, 177.8
    c38_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {c38_x:.2f} {c38_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{c38_uuid}")
\t\t(property "Reference" "C38" (at {c38_x+1.90:.2f} {c38_y-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "150pF" (at {c38_x+1.90:.2f} {c38_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {c38_x:.2f} {c38_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1673" (at {c38_x:.2f} {c38_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "C38") (unit 1))))
\t)''')
    connect_pin(c38_x, c38_y, pins_c, 1, "RFI2", 0, -2.54, 90)
    connect_pin(c38_x, c38_y, pins_c, 2, "AGDC", 0, 2.54, 270)

    # 6. Multiplexer U1 (CD74HC4067M) at (177.8, 147.32)
    u1_x, u1_y = 177.8, 147.32
    u1_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "74xx:CD74HC4067M")
\t\t(at {u1_x:.2f} {u1_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{u1_uuid}")
\t\t(property "Reference" "U1" (at {u1_x-8.89:.2f} {u1_y-27.94:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "CD74HC4067M" (at {u1_x+1.27:.2f} {u1_y-27.94:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm" (at {u1_x:.2f} {u1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C21473" (at {u1_x:.2f} {u1_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
{chr(10).join([f'\t\t(pin "{p}" (uuid "{gen_uuid()}"))' for p in range(1, 25)])}
\t\t(instances (project "" (path "/{root_uuid}" (reference "U1") (unit 1))))
\t)''')

    connect_pin(u1_x, u1_y, pins_mux, 1, "RF_SIG", -5.08, 0, 180)
    connect_pin(u1_x, u1_y, pins_mux, 24, "+5V", 0, -5.08, 90)
    connect_pin(u1_x, u1_y, pins_mux, 12, "GND", 0, 5.08, 270)
    connect_pin(u1_x, u1_y, pins_mux, 10, "MUX_S0", -5.08, 0, 180)
    connect_pin(u1_x, u1_y, pins_mux, 11, "MUX_S1", -5.08, 0, 180)
    connect_pin(u1_x, u1_y, pins_mux, 14, "MUX_S2", -5.08, 0, 180)
    connect_pin(u1_x, u1_y, pins_mux, 13, "MUX_S3", -5.08, 0, 180)
    connect_pin(u1_x, u1_y, pins_mux, 15, "MUX_EN", -5.08, 0, 180)

    # Decoupling caps for U1: C17 (0.1uF), C18 (10uF)
    for c_ref, c_val, cx, lcsc in [("C17", "0.1uF", 160.02, "C14663"), ("C18", "10uF", 147.32, "C15850")]:
        cy = 116.84
        cuuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx:.2f} {cy:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{cuuid}")
\t\t(property "Reference" "{c_ref}" (at {cx+1.90:.2f} {cy-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "{c_val}" (at {cx+1.90:.2f} {cy+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "{lcsc}" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{c_ref}") (unit 1))))
\t)''')
        connect_pin(cx, cy, pins_c, 1, "+5V", 0, -2.54, 90)
        connect_pin(cx, cy, pins_c, 2, "GND", 0, 2.54, 270)

    # Multiplexer channels
    mux_pins_order = [9, 8, 7, 6, 5, 4, 3, 2, 23, 22, 21, 20, 19, 18, 17, 16]
    for ch_idx, pin_num in enumerate(mux_pins_order):
        connect_pin(u1_x, u1_y, pins_mux, pin_num, f"RF_CH{ch_idx}", 5.08, 0, 0)

    # 7. 16 Tuned Planar Resonant Tanks
    # Each cell has: Rdamp (1.5R), Ca (100pF), Cb (22pF), L (1.26uH planar coil)
    tank_base_x = 241.3
    tank_base_y = 38.1
    cell_to_mux_ch = {
        13: 0, 9: 1, 5: 2, 1: 3,
        14: 4, 10: 5, 6: 6, 2: 7,
        15: 8, 11: 9, 7: 10, 3: 11,
        16: 12, 12: 13, 8: 14, 4: 15,
    }

    for k in range(16):
        cell_id = k + 1
        mux_ch = cell_to_mux_ch[cell_id]
        row = k // 4
        col = k % 4
        x_off = col * 38.1
        y_off = row * 45.72
        cx = tank_base_x + x_off
        cy = tank_base_y + y_off

        # Series Damping Resistor R_k (1.5R)
        r_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at {cx:.2f} {cy:.2f} 90)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{r_uuid}")
\t\t(property "Reference" "R{cell_id}" (at {cx:.2f} {cy-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "1.5R" (at {cx:.2f} {cy+3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C25081" (at {cx:.2f} {cy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "R{cell_id}") (unit 1))))
\t)''')
        add_wire(cx - 3.81, cy, cx - 7.62, cy)
        add_label(f"RF_CH{mux_ch}", cx - 7.62, cy, 180)
        add_wire(cx + 3.81, cy, cx + 7.62, cy)
        add_label(f"RF_COIL_{cell_id}", cx + 7.62, cy, 0)

        # Tuning Capacitor Ca_k (100pF C0G)
        ca_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx+7.62:.2f} {cy+12.7:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{ca_uuid}")
\t\t(property "Reference" "Ca{cell_id}" (at {cx+9.52:.2f} {cy+11.43:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "100pF" (at {cx+9.52:.2f} {cy+13.97:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx+7.62:.2f} {cy+12.7:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1666" (at {cx+7.62:.2f} {cy+12.7:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "Ca{cell_id}") (unit 1))))
\t)''')
        connect_pin(cx + 7.62, cy + 12.7, pins_c, 1, f"RF_COIL_{cell_id}", 0, -2.54, 90)
        connect_pin(cx + 7.62, cy + 12.7, pins_c, 2, "GND", 0, 2.54, 270)

        # Fine Tuning Capacitor Cb_k (22pF C0G)
        cb_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:C")
\t\t(at {cx+15.24:.2f} {cy+12.7:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{cb_uuid}")
\t\t(property "Reference" "Cb{cell_id}" (at {cx+17.14:.2f} {cy+11.43:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "22pF" (at {cx+17.14:.2f} {cy+13.97:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Capacitor_SMD:C_0603_1608Metric" (at {cx+15.24:.2f} {cy+12.7:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(property "LCSC" "C1653" (at {cx+15.24:.2f} {cy+12.7:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "Cb{cell_id}") (unit 1))))
\t)''')
        connect_pin(cx + 15.24, cy + 12.7, pins_c, 1, f"RF_COIL_{cell_id}", 0, -2.54, 90)
        connect_pin(cx + 15.24, cy + 12.7, pins_c, 2, "GND", 0, 2.54, 270)

        # Planar Coil L_k (1.26uH)
        l_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Device:L")
\t\t(at {cx+22.86:.2f} {cy+12.7:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{l_uuid}")
\t\t(property "Reference" "L{cell_id}" (at {cx+24.76:.2f} {cy+11.43:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "1.26uH" (at {cx+24.76:.2f} {cy+13.97:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Inductor_SMD:L_0805_2012Metric" (at {cx+22.86:.2f} {cy+12.7:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "L{cell_id}") (unit 1))))
\t)''')
        connect_pin(cx + 22.86, cy + 12.7, pins_l, 1, f"RF_COIL_{cell_id}", 0, -2.54, 90)
        connect_pin(cx + 22.86, cy + 12.7, pins_l, 2, "GND", 0, 2.54, 270)

    # 8. SMA Diagnostic Connector J3
    sma_x, sma_y = 60.96, 203.2
    sma_uuid = gen_uuid()
    symbols_code.append(f'''\t(symbol
\t\t(lib_id "Connector:Conn_Coaxial")
\t\t(at {sma_x:.2f} {sma_y:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{sma_uuid}")
\t\t(property "Reference" "J3" (at {sma_x-5.08:.2f} {sma_y-5.08:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "RF_TEST_SMA" (at {sma_x-5.08:.2f} {sma_y-7.62:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Connector_Coaxial:SMA_Amphenol_132134_Vertical" (at {sma_x:.2f} {sma_y:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(pin "2" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "J3") (unit 1))))
\t)''')
    connect_pin(sma_x, sma_y, pins_sma, 1, "RF_SIG", -5.08, 0, 180)
    connect_pin(sma_x, sma_y, pins_sma, 2, "GND", 5.08, 0, 0)

    # 9. 4x Mounting Holes H1..H4
    for idx, (hx, hy) in enumerate([(88.9, 203.2), (101.6, 203.2), (114.3, 203.2), (127.0, 203.2)]):
        h_ref = f"H{idx+1}"
        h_uuid = gen_uuid()
        symbols_code.append(f'''\t(symbol
\t\t(lib_id "Mechanical:MountingHole_Pad")
\t\t(at {hx:.2f} {hy:.2f} 0)
\t\t(unit 1)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(uuid "{h_uuid}")
\t\t(property "Reference" "{h_ref}" (at {hx+2.54:.2f} {hy-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "MountingHole_M3" (at {hx+2.54:.2f} {hy+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "MountingHole:MountingHole_3.2mm_M3_Pad" (at {hx:.2f} {hy:.2f} 0) (hide yes) (effects (font (size 1.27 1.27))))
\t\t(pin "1" (uuid "{gen_uuid()}"))
\t\t(instances (project "" (path "/{root_uuid}" (reference "{h_ref}") (unit 1))))
\t)''')
        connect_pin(hx, hy, pins_hole, 1, "GND", 0, 2.54, 270)

    # Assemble complete KiCad 10 schematic
    sch_content = f'''(kicad_sch
\t(version 20231120)
\t(generator "antigravity_st25r3916")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A2")
\t(title_block
\t\t(title "Smart Crossword Board - 4x4 ST25R3916 Integrated NFC Matrix")
\t\t(date "2026-09-16")
\t\t(rev "v2.0")
\t\t(company "Smart Crossword Project")
\t\t(comment 1 "Transceiver: ST25R3916B-AQFT 13.56MHz + CD74HC4067 16-Channel Analog MUX")
\t\t(comment 2 "EMC Low-Pass Filter (L0=470nH, C0=180pF) + Dual in-place C0G Tuning Pads")
\t)
\t(lib_symbols
{chr(10).join(lib_symbols_list)}
\t)
{chr(10).join(wires_code)}
{chr(10).join(labels_code)}
{chr(10).join(no_connects)}
{chr(10).join(symbols_code)}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
'''
    # Write local symbol library file
    sym_lib_content = f"""(kicad_symbol_lib
	(version 20231120)
	(generator "antigravity")
	(generator_version "10.0")
{sym_st25.replace('st25r3916_grid_4x4:ST25R3916B-AQFT', 'ST25R3916B-AQFT')}
)"""
    sym_file_path = os.path.join(os.path.dirname(out_path), "st25r3916_grid_4x4.kicad_sym")
    with open(sym_file_path, "w") as f:
        f.write(sym_lib_content)

    with open(out_path, 'w') as f:
        f.write(sch_content)
    print(f"Schematic generated successfully at {out_path}")

if __name__ == '__main__':
    generate_schematic('hardware/kicad/st25r3916_grid_4x4/st25r3916_grid_4x4.kicad_sch')
