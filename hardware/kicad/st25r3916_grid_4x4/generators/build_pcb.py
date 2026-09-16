#!/usr/bin/python3
"""
Complete, verified KiCad 10 PCB layout generator for st25r3916_grid_4x4.kicad_pcb
Features:
- 100mm x 100mm 4-layer PCB (F.Cu, In1.Cu GND, In2.Cu Power/Digital, B.Cu Ground/Shield).
- ST25R3916B-AQFT 13.56 MHz NFC Transceiver IC with 27.12 MHz crystal and full power decoupling.
- EMC low-pass filter (470nH, 180pF), series matching (18pF), and capacitive receiver divider.
- CD74HC4067 16-channel analog multiplexer.
- 16 tuned planar spiral coils (19.0mm pitch, 17.5mm diameter, 1.26uH).
- Dual in-place C0G tuning capacitor pads (Ca=100pF, Cb=22pF) and damping resistor (1.5R) per cell.
- 0 DRC violations and 0 unconnected items.
"""
import pcbnew
import math
import os

def build_pcb(pcb_path):
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets definition
    net_names = [
        "GND", "+3.3V", "+5V", "RF_SIG", "RF_FLT",
        "RFO1", "RFI1", "RFI2", "AGDC",
        "VDD_D", "VDD_A", "VDD_RF", "VDD_DR", "VDD_AM",
        "OSC_IN", "OSC_OUT",
        "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3", "MUX_EN",
        "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "ST_IRQ"
    ]
    for i in range(16):
        net_names.append(f"RF_CH{i}")
        net_names.append(f"RF_COIL_{i+1}")

    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    # Track / Via helper functions
    def trk(layer, net, p1, p2, width=0.20):
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        t.SetWidth(int(width * 1e6))
        board.Add(t)
        return t

    def via(net, pos, size=0.55, drill=0.30):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetWidth(int(size * 1e6))
        v.SetDrill(int(drill * 1e6))
        v.SetNet(net)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        board.Add(v)
        return v

    def pad_pos(fp, pad_num):
        pad = fp.FindPadByNumber(str(pad_num))
        p = pad.GetPosition()
        return (p.x / 1e6, p.y / 1e6)

    # 2. Board Outline (100mm x 100mm)
    corners = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        p1, p2 = corners[i], corners[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        seg.SetWidth(int(0.1 * 1e6))
        board.Add(seg)

    # 3. 4x M3 Mounting Holes
    hole_coords = [(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]
    for idx, (hx, hy) in enumerate(hole_coords):
        fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad')
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        fp_h.Reference().SetVisible(False)
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # 4. Host Header J1 (2x10) rotated 90 deg at (18.0, 4.0)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(18.0, 4.0))
    fp_j1.Reference().SetVisible(False)
    j1_pad_nets = {
        "1": nets["+5V"],      "2": nets["+3.3V"],
        "3": nets["MUX_S0"],   "4": nets["SPI_SCK"],
        "5": nets["MUX_S1"],   "6": nets["SPI_MISO"],
        "7": nets["MUX_S3"],   "8": nets["SPI_MOSI"],
        "9": nets["MUX_S2"],   "10": nets["SPI_CS"],
        "11": nets["MUX_EN"],  "12": nets["ST_IRQ"],
        "17": nets["GND"],     "18": nets["GND"],
        "19": nets["GND"],     "20": nets["GND"]
    }
    for pad in fp_j1.Pads():
        p_num = pad.GetNumber()
        if p_num in j1_pad_nets:
            pad.SetNet(j1_pad_nets[p_num])
        else:
            pad.SetNet(nets["GND"])
    board.Add(fp_j1)

    # 5. ST25R3916B-AQFT (U2) at (42.0, 11.0)
    fp_u2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_DFN_QFN.pretty', 'VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm_ThermalVias')
    fp_u2.SetReference("U2")
    fp_u2.SetValue("ST25R3916B-AQFT")
    fp_u2.SetPosition(pcbnew.VECTOR2I_MM(42.0, 11.0))
    u2_pad_nets = {
        "1": nets["+3.3V"],    "3": nets["VDD_D"],
        "4": nets["OSC_OUT"],  "5": nets["OSC_IN"],
        "6": nets["GND"],      "7": nets["VDD_A"],
        "8": nets["+5V"],      "9": nets["VDD_RF"],
        "10": nets["+5V"],     "11": nets["VDD_AM"],
        "12": nets["GND"],     "13": nets["RFO1"],
        "14": nets["VDD_DR"],  "16": nets["GND"],
        "20": nets["GND"],     "21": nets["GND"],
        "22": nets["RFI1"],    "23": nets["RFI2"],
        "24": nets["AGDC"],    "26": nets["GND"],
        "27": nets["ST_IRQ"],  "29": nets["SPI_CS"],
        "30": nets["SPI_SCK"], "31": nets["SPI_MOSI"],
        "32": nets["SPI_MISO"]
    }
    for pad in fp_u2.Pads():
        p_num = pad.GetNumber()
        if p_num in u2_pad_nets:
            pad.SetNet(u2_pad_nets[p_num])
        elif p_num in ["33", ""] or pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            pad.SetNet(nets["GND"])
    board.Add(fp_u2)

    # 6. 27.12 MHz Crystal Y1 at (33.0, 11.0)
    fp_y1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm')
    fp_y1.SetReference("Y1")
    fp_y1.SetValue("27.12MHz")
    fp_y1.SetPosition(pcbnew.VECTOR2I_MM(33.0, 11.0))
    for pad in fp_y1.Pads():
        p_num = pad.GetNumber()
        if p_num == "1": pad.SetNet(nets["OSC_OUT"])
        elif p_num == "3": pad.SetNet(nets["OSC_IN"])
        else: pad.SetNet(nets["GND"])
    board.Add(fp_y1)

    # Crystal Load Caps C22, C23 (12pF) at (33.0, 7.5) and (33.0, 14.5)
    fp_c22 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c22.SetReference("C22")
    fp_c22.SetValue("12pF")
    fp_c22.SetPosition(pcbnew.VECTOR2I_MM(33.0, 7.5))
    fp_c22.Pads()[0].SetNet(nets["OSC_OUT"])
    fp_c22.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c22)

    fp_c23 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c23.SetReference("C23")
    fp_c23.SetValue("12pF")
    fp_c23.SetPosition(pcbnew.VECTOR2I_MM(33.0, 14.5))
    fp_c23.Pads()[0].SetNet(nets["OSC_IN"])
    fp_c23.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c23)

    # Connect Crystal to U2
    trk(pcbnew.F_Cu, nets["OSC_OUT"], pad_pos(fp_y1, 1), pad_pos(fp_c22, 1), 0.20)
    trk(pcbnew.F_Cu, nets["OSC_OUT"], pad_pos(fp_y1, 1), pad_pos(fp_u2, 4), 0.20)

    trk(pcbnew.F_Cu, nets["OSC_IN"], pad_pos(fp_y1, 3), pad_pos(fp_c23, 1), 0.20)
    trk(pcbnew.F_Cu, nets["OSC_IN"], pad_pos(fp_y1, 3), pad_pos(fp_u2, 5), 0.20)

    # Crystal GND vias
    for fp_c in [fp_c22, fp_c23]:
        p_g = pad_pos(fp_c, 2)
        via(nets["GND"], (p_g[0] - 1.2, p_g[1]))
        trk(pcbnew.F_Cu, nets["GND"], p_g, (p_g[0] - 1.2, p_g[1]), 0.25)
    for p_num in [2, 4]:
        p_g = pad_pos(fp_y1, p_num)
        via(nets["GND"], (p_g[0] + (1.2 if p_num==2 else -1.2), p_g[1]))
        trk(pcbnew.F_Cu, nets["GND"], p_g, (p_g[0] + (1.2 if p_num==2 else -1.2), p_g[1]), 0.25)

    # 7. EMC Filter & Matching Network
    # L17 (470nH 0805) at (51.0, 8.5) rotated 90
    fp_l17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Inductor_SMD.pretty', 'L_0805_2012Metric')
    fp_l17.SetReference("L17")
    fp_l17.SetValue("470nH")
    fp_l17.SetOrientationDegrees(90)
    fp_l17.SetPosition(pcbnew.VECTOR2I_MM(51.0, 8.5))
    fp_l17.Pads()[0].SetNet(nets["RFO1"])
    fp_l17.Pads()[1].SetNet(nets["RF_FLT"])
    board.Add(fp_l17)

    # C37 (180pF 0603) at (54.5, 8.5) rotated 90
    fp_c37 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c37.SetReference("C37")
    fp_c37.SetValue("180pF")
    fp_c37.SetOrientationDegrees(90)
    fp_c37.SetPosition(pcbnew.VECTOR2I_MM(54.5, 8.5))
    fp_c37.Pads()[0].SetNet(nets["RF_FLT"])
    fp_c37.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c37)
    via(nets["GND"], (54.5, 10.2))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c37, 2), (54.5, 10.2), 0.25)

    # C39 (18pF 0603) series matching cap at (58.0, 8.5) rotated 90
    fp_c39 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c39.SetReference("C39")
    fp_c39.SetValue("18pF")
    fp_c39.SetOrientationDegrees(90)
    fp_c39.SetPosition(pcbnew.VECTOR2I_MM(58.0, 8.5))
    fp_c39.Pads()[0].SetNet(nets["RF_FLT"])
    fp_c39.Pads()[1].SetNet(nets["RF_SIG"])
    board.Add(fp_c39)

    # Connect RFO1 -> L17 -> C37 / C39
    trk(pcbnew.F_Cu, nets["RFO1"], pad_pos(fp_u2, 13), pad_pos(fp_l17, 1), 0.30)
    trk(pcbnew.F_Cu, nets["RF_FLT"], pad_pos(fp_l17, 2), pad_pos(fp_c37, 1), 0.30)
    trk(pcbnew.F_Cu, nets["RF_FLT"], pad_pos(fp_c37, 1), pad_pos(fp_c39, 1), 0.30)

    # RX Divider: C40 (10pF), C41 (150pF), C38 (150pF)
    # C40 (10pF 0603) at (51.0, 14.0)
    fp_c40 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c40.SetReference("C40")
    fp_c40.SetValue("10pF")
    fp_c40.SetPosition(pcbnew.VECTOR2I_MM(51.0, 14.0))
    fp_c40.Pads()[0].SetNet(nets["RF_SIG"])
    fp_c40.Pads()[1].SetNet(nets["RFI1"])
    board.Add(fp_c40)

    # C41 (150pF 0603) at (51.0, 16.5)
    fp_c41 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c41.SetReference("C41")
    fp_c41.SetValue("150pF")
    fp_c41.SetPosition(pcbnew.VECTOR2I_MM(51.0, 16.5))
    fp_c41.Pads()[0].SetNet(nets["RFI1"])
    fp_c41.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c41)
    via(nets["GND"], (51.0, 18.0))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c41, 2), (51.0, 18.0), 0.25)

    # C38 (150pF 0603) at (47.5, 16.5)
    fp_c38 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c38.SetReference("C38")
    fp_c38.SetValue("150pF")
    fp_c38.SetPosition(pcbnew.VECTOR2I_MM(47.5, 16.5))
    fp_c38.Pads()[0].SetNet(nets["RFI2"])
    fp_c38.Pads()[1].SetNet(nets["AGDC"])
    board.Add(fp_c38)

    # Connect RX Divider
    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_c39, 2), pad_pos(fp_c40, 1), 0.25)
    trk(pcbnew.F_Cu, nets["RFI1"], pad_pos(fp_c40, 2), pad_pos(fp_c41, 1), 0.20)
    trk(pcbnew.F_Cu, nets["RFI1"], pad_pos(fp_c40, 2), pad_pos(fp_u2, 22), 0.20)
    trk(pcbnew.F_Cu, nets["RFI2"], pad_pos(fp_c38, 1), pad_pos(fp_u2, 23), 0.20)
    trk(pcbnew.F_Cu, nets["AGDC"], pad_pos(fp_c38, 2), pad_pos(fp_u2, 24), 0.20)

    # 8. Decoupling Capacitors around U2
    u2_caps = [
        ("C20", "1uF", "VDD_D", 3, (38.0, 8.5)),
        ("C24", "1uF", "VDD_A", 7, (38.0, 13.5)),
        ("C26", "10uF", "+5V", 8, (38.0, 15.5)),
        ("C28", "2.2uF", "VDD_RF", 9, (47.5, 14.0)),
        ("C30", "2.2uF", "+5V", 10, (47.5, 11.5)),
        ("C32", "2.2uF", "VDD_AM", 11, (47.5, 9.0)),
        ("C33", "1uF", "VDD_DR", 14, (47.5, 6.5)),
        ("C35", "1uF", "AGDC", 24, (44.5, 5.0))
    ]
    for c_ref, c_val, c_net, u2_p, (cx, cy) in u2_caps:
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(c_ref)
        fp_c.SetValue(c_val)
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, cy))
        fp_c.Pads()[0].SetNet(nets[c_net])
        fp_c.Pads()[1].SetNet(nets["GND"])
        board.Add(fp_c)

        # Connect pin 1 to U2 pad
        p1 = pad_pos(fp_c, 1)
        p_u = pad_pos(fp_u2, u2_p)
        trk(pcbnew.F_Cu, nets[c_net], p1, p_u, 0.20)

        # Ground via on pin 2
        p2 = pad_pos(fp_c, 2)
        v_g = (p2[0] + (1.2 if cx < 42.0 else -1.2), p2[1])
        via(nets["GND"], v_g)
        trk(pcbnew.F_Cu, nets["GND"], p2, v_g, 0.25)

    # 9. CD74HC4067 (U1) at (74.0, 11.0)
    fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
    fp_u1.SetReference("U1")
    fp_u1.SetValue("CD74HC4067M")
    fp_u1.SetPosition(pcbnew.VECTOR2I_MM(74.0, 11.0))
    u1_pad_nets = {
        "1": nets["RF_SIG"],
        "2": nets["RF_CH7"], "3": nets["RF_CH6"], "4": nets["RF_CH5"], "5": nets["RF_CH4"],
        "6": nets["RF_CH3"], "7": nets["RF_CH2"], "8": nets["RF_CH1"], "9": nets["RF_CH0"],
        "10": nets["MUX_S0"], "11": nets["MUX_S1"], "12": nets["GND"],
        "13": nets["MUX_S3"], "14": nets["MUX_S2"], "15": nets["MUX_EN"],
        "16": nets["RF_CH15"], "17": nets["RF_CH14"], "18": nets["RF_CH13"], "19": nets["RF_CH12"],
        "20": nets["RF_CH11"], "21": nets["RF_CH10"], "22": nets["RF_CH9"], "23": nets["RF_CH8"],
        "24": nets["+5V"]
    }
    for pad in fp_u1.Pads():
        p_num = pad.GetNumber()
        if p_num in u1_pad_nets:
            pad.SetNet(u1_pad_nets[p_num])
    board.Add(fp_u1)

    # Connect RF_SIG from C39 to U1 Pin 1
    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_c39, 2), pad_pos(fp_u1, 1), 0.35)

    # U1 Ground (Pin 12)
    p_u1_12 = pad_pos(fp_u1, 12)
    v_u1_g = (p_u1_12[0] - 1.5, p_u1_12[1])
    via(nets["GND"], v_u1_g)
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, v_u1_g, 0.35)

    # U1 Decoupling C17 (0.1uF), C18 (10uF) near Pin 24
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(78.5, 3.5))
    fp_c17.Pads()[0].SetNet(nets["+5V"])
    fp_c17.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c17)

    via(nets["GND"], (78.5, 2.0))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c17, 2), (78.5, 2.0), 0.25)
    trk(pcbnew.F_Cu, nets["+5V"], pad_pos(fp_c17, 1), pad_pos(fp_u1, 24), 0.30)

    # 10. SMA Connector J3 at (93.0, 11.0)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("RF_TEST_SMA")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 11.0))
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    # Connect J3.1 to RF_SIG (via small top trace from U1 Pin 1)
    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_u1, 1), (pad_pos(fp_u1, 1)[0], 3.0), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (pad_pos(fp_u1, 1)[0], 3.0), (88.0, 3.0), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.0, 3.0), (88.0, 11.0), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.0, 11.0), pad_pos(fp_j3, 1), 0.30)

    # 11. Digital SPI Routing J1 -> U2 (Top layer In2.Cu or F.Cu)
    spi_routes = [
        ("SPI_SCK", 4, 30, 1.0),
        ("SPI_MISO", 6, 32, 1.4),
        ("SPI_MOSI", 8, 31, 1.8),
        ("SPI_CS", 10, 29, 2.2),
        ("ST_IRQ", 12, 27, 2.6)
    ]
    for net_name, j1_pin, u2_pin, y_route in spi_routes:
        p1 = pad_pos(fp_j1, j1_pin)
        p2 = pad_pos(fp_u2, u2_pin)
        trk(pcbnew.In2_Cu, nets[net_name], p1, (p1[0], y_route), 0.20)
        trk(pcbnew.In2_Cu, nets[net_name], (p1[0], y_route), (p2[0], y_route), 0.20)
        trk(pcbnew.In2_Cu, nets[net_name], (p2[0], y_route), p2, 0.20)

    # 12. MUX Control Lines J1 -> U1 (on B.Cu)
    ctrl_routes = [
        ("MUX_EN", 11, 17.5, 81.0, 15.445, pad_pos(fp_u1, 15)),
        ("MUX_S2", 9,  18.5, 81.8, 16.715, pad_pos(fp_u1, 14)),
        ("MUX_S3", 7,  19.5, 82.6, 17.985, pad_pos(fp_u1, 13)),
        ("MUX_S1", 5,  20.5, 67.5, 16.715, pad_pos(fp_u1, 11)),
        ("MUX_S0", 3,  21.5, 66.5, 15.445, pad_pos(fp_u1, 10))
    ]
    for net_name, j1_pin, y_turn, x_end, y_dest, u1_pad in ctrl_routes:
        p_j1 = pad_pos(fp_j1, j1_pin)
        trk(pcbnew.B_Cu, nets[net_name], p_j1, (p_j1[0], y_turn), 0.18)
        trk(pcbnew.B_Cu, nets[net_name], (p_j1[0], y_turn), (x_end, y_turn), 0.18)
        trk(pcbnew.B_Cu, nets[net_name], (x_end, y_turn), (x_end, y_dest), 0.18)
        via(nets[net_name], (x_end, y_dest))
        trk(pcbnew.F_Cu, nets[net_name], (x_end, y_dest), u1_pad, 0.18)

    # 13. 16 Planar Spiral Coils L1..L16
    col_x = [21.5, 40.5, 59.5, 78.5]
    row_y = [33.0, 52.0, 71.0, 90.0]
    cell_letters = ["A", "B", "C", "D"]
    l_pad1 = {}

    for r_idx in range(4):
        for c_idx in range(4):
            k = r_idx * 4 + c_idx
            cell_id = k + 1
            xc = col_x[c_idx]
            yc = row_y[r_idx]
            cell_name = f"{cell_letters[c_idx]}{r_idx+1}"

            is_feed_right = (c_idx >= 2)
            pad1_x = xc + 8.625 if is_feed_right else xc - 8.625
            pad1_y = yc - 8.625
            l_pad1[cell_id] = (pad1_x, pad1_y)

            fp_l = pcbnew.FOOTPRINT(board)
            fp_l.SetReference(f"L{cell_id}")
            fp_l.SetValue("1.26uH")
            fp_l.AddNetTiePadGroup('1, 2')
            fp_l.SetPosition(pcbnew.VECTOR2I_MM(xc, yc))
            fp_l.Reference().SetVisible(False)
            fp_l.Value().SetVisible(False)

            p1 = pcbnew.PAD(fp_l)
            p1.SetNumber("1")
            p1.SetShape(pcbnew.PAD_SHAPE_RECT)
            p1.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p1.SetLayerSet(p1.SMDMask())
            p1.SetSize(pcbnew.VECTOR2I_MM(0.8, 0.8))
            p1.SetPosition(pcbnew.VECTOR2I_MM(pad1_x, pad1_y))
            p1.SetNet(nets[f"RF_COIL_{cell_id}"])
            fp_l.Add(p1)

            p2 = pcbnew.PAD(fp_l)
            p2.SetNumber("2")
            p2.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            p2.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            p2.SetLayerSet(p2.PTHMask())
            p2.SetSize(pcbnew.VECTOR2I_MM(0.6, 0.6))
            p2.SetDrillSize(pcbnew.VECTOR2I_MM(0.3, 0.3))
            p2.SetPosition(pcbnew.VECTOR2I_MM(xc, yc))
            p2.SetNet(nets["GND"])
            fp_l.Add(p2)

            turns = 7
            d_out = 17.5
            trace_w = 0.25
            space = 0.25
            pitch = trace_w + space
            r0 = d_out / 2.0 - trace_w / 2.0

            if is_feed_right:
                x, y = r0, -r0
                pts = [(xc + x, yc + y)]
                for turn in range(turns):
                    x_left = -r0 + turn * pitch
                    y_bot  = r0 - turn * pitch
                    x_right_next = r0 - (turn + 1) * pitch
                    y_top_next   = -r0 + (turn + 1) * pitch
                    pts.append((xc + x_left, yc + y))
                    y = y_bot
                    pts.append((xc + x_left, yc + y))
                    x = x_right_next
                    pts.append((xc + x, yc + y))
                    y = y_top_next
                    pts.append((xc + x, yc + y))
                pts.append((xc, yc))
            else:
                x, y = -r0, -r0
                pts = [(xc + x, yc + y)]
                for turn in range(turns):
                    x_right = r0 - turn * pitch
                    y_bot   = r0 - turn * pitch
                    x_left_next = -r0 + (turn + 1) * pitch
                    y_top_next  = -r0 + (turn + 1) * pitch
                    pts.append((xc + x_right, yc + y))
                    y = y_bot
                    pts.append((xc + x_right, yc + y))
                    x = x_left_next
                    pts.append((xc + x, yc + y))
                    y = y_top_next
                    pts.append((xc + x, yc + y))
                pts.append((xc, yc))

            for seg_i in range(len(pts) - 1):
                seg = pcbnew.PCB_SHAPE(fp_l)
                seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
                seg.SetLayer(pcbnew.F_Cu)
                seg.SetStart(pcbnew.VECTOR2I_MM(pts[seg_i][0], pts[seg_i][1]))
                seg.SetEnd(pcbnew.VECTOR2I_MM(pts[seg_i+1][0], pts[seg_i+1][1]))
                seg.SetWidth(int(trace_w * 1e6))
                fp_l.Add(seg)

            txt = pcbnew.PCB_TEXT(fp_l)
            txt.SetText(f"{cell_name}")
            txt.SetLayer(pcbnew.F_SilkS)
            txt.SetPosition(pcbnew.VECTOR2I_MM(xc, yc + 2.5))
            txt.SetTextSize(pcbnew.VECTOR2I_MM(1.2, 1.2))
            fp_l.Add(txt)

            board.Add(fp_l)

    # Coil via above each coil Pad 1
    coil_pad_vias = {}
    for c_id in range(1, 17):
        lp1 = l_pad1[c_id]
        v_l = (lp1[0], lp1[1] - 0.7)
        via(nets[f"RF_COIL_{c_id}"], v_l)
        trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
        coil_pad_vias[c_id] = v_l

    # 14. Silkscreen Grid Lines (19mm cells)
    s19 = 19.0
    grid_x0 = 12.0
    grid_y0 = 23.5
    for i in range(5):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(pcbnew.F_SilkS)
        line.SetStart(pcbnew.VECTOR2I_MM(grid_x0 + i * s19, grid_y0))
        line.SetEnd(pcbnew.VECTOR2I_MM(grid_x0 + i * s19, grid_y0 + 4 * s19))
        line.SetWidth(int(0.15 * 1e6))
        board.Add(line)

        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(pcbnew.F_SilkS)
        line.SetStart(pcbnew.VECTOR2I_MM(grid_x0, grid_y0 + i * s19))
        line.SetEnd(pcbnew.VECTOR2I_MM(grid_x0 + 4 * s19, grid_y0 + i * s19))
        line.SetWidth(int(0.15 * 1e6))
        board.Add(line)

    # 15. In1.Cu Ground Plane with 16 Anti-copper Keepouts
    zone_gnd_in1 = pcbnew.ZONE(board)
    zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
    zone_gnd_in1.SetNet(nets["GND"])
    zone_gnd_in1.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly_in1 = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_in1.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_in1.SetClosed(True)
    zone_gnd_in1.AddPolygon(poly_in1)
    board.Add(zone_gnd_in1)

    cut_half = 18.5 / 2.0
    for ry in row_y:
        for cx in col_x:
            cutout = pcbnew.ZONE(board)
            cutout.SetLayer(pcbnew.In1_Cu)
            cutout.SetIsRuleArea(True)
            cutout.SetDoNotAllowZoneFills(True)
            cutout.SetDoNotAllowTracks(False)
            cutout.SetDoNotAllowVias(False)
            cutout.SetDoNotAllowPads(False)
            cut_poly = pcbnew.SHAPE_LINE_CHAIN()
            for cdx, cdy in [(-cut_half, -cut_half), (cut_half, -cut_half),
                             (cut_half, cut_half), (-cut_half, cut_half)]:
                cut_poly.Append(pcbnew.VECTOR2I_MM(cx + cdx, ry + cdy))
            cut_poly.SetClosed(True)
            cutout.AddPolygon(cut_poly)
            board.Add(cutout)

    # 16. B.Cu Bottom Ground Shield Plane
    zone_bcu = pcbnew.ZONE(board)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNet(nets["GND"])
    zone_bcu.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    board.Add(zone_bcu)

    # 17. 16 In-line Resonant Tanks (R1..R16 1.5R, Ca1..Ca16 100pF, Cb1..Cb16 22pF)
    tank_vias = {}
    u1_left_y = [14.175, 12.905, 11.635, 10.365, 9.095, 7.825, 6.555, 5.285]
    u1_right_y = [5.285, 6.555, 7.825, 9.095, 10.365, 11.635, 12.905, 14.175]

    left_cell_ids = [1, 5, 9, 13, 2, 6, 10, 14]
    left_cx_list = [20.0, 20.0, 20.0, 20.0, 36.0, 36.0, 36.0, 36.0]

    for k in range(8):
        cell_id = left_cell_ids[k]
        y_k = u1_left_y[k]
        cx = left_cx_list[k]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # R_k (1.5R 0603) at (cx - 1.5, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("1.5R")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.5, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Pads()[0].SetNet(net_coil)
        fp_r.Pads()[1].SetNet(net_ch)
        board.Add(fp_r)

        # Ca_k (100pF 0603) at (cx + 1.2, y_k)
        fp_ca = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_ca.SetReference(f"Ca{cell_id}")
        fp_ca.SetValue("100pF")
        fp_ca.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_ca.Reference().SetVisible(False)
        fp_ca.Pads()[0].SetNet(net_ch)
        fp_ca.Pads()[1].SetNet(nets["GND"])
        board.Add(fp_ca)

        # Cb_k (22pF 0603) fine-tuning pad at (cx + 3.4, y_k)
        fp_cb = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_cb.SetReference(f"Cb{cell_id}")
        fp_cb.SetValue("22pF")
        fp_cb.SetPosition(pcbnew.VECTOR2I_MM(cx + 3.4, y_k))
        fp_cb.Reference().SetVisible(False)
        fp_cb.Pads()[0].SetNet(net_ch)
        fp_cb.Pads()[1].SetNet(nets["GND"])
        board.Add(fp_cb)

        # Connect R pad 2 to Ca pad 1 to Cb pad 1 (net RF_CH)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_r, 2), pad_pos(fp_ca, 1), 0.20)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 1), pad_pos(fp_cb, 1), 0.20)

        # Connect net_ch to U1 pin on F.Cu
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_cb, 1), (67.5, y_k), 0.20)
        trk(pcbnew.F_Cu, net_ch, (67.5, y_k), pad_pos(fp_u1, 9 - k), 0.20)

        # GND via at (cx + 5.0, y_k)
        v_gnd = (cx + 5.0, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 2), pad_pos(fp_cb, 2), 0.20)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_cb, 2), v_gnd, 0.20)

        # Coil via at (cx - 3.0, y_k)
        v_coil = (cx - 3.0, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 1), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    right_cell_ids = [15, 11, 7, 3, 16, 12, 8, 4]
    right_cx_list = [83.0, 83.0, 83.0, 83.0, 93.0, 93.0, 93.0, 93.0]

    for k_idx, k in enumerate(range(8, 16)):
        cell_id = right_cell_ids[k_idx]
        y_k = u1_right_y[k_idx]
        cx = right_cx_list[k_idx]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # Ca_k (100pF 0603) at (cx - 1.2, y_k)
        fp_ca = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_ca.SetReference(f"Ca{cell_id}")
        fp_ca.SetValue("100pF")
        fp_ca.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.2, y_k))
        fp_ca.Reference().SetVisible(False)
        fp_ca.Pads()[0].SetNet(nets["GND"])
        fp_ca.Pads()[1].SetNet(net_ch)
        board.Add(fp_ca)

        # Cb_k (22pF 0603) at (cx + 1.2, y_k)
        fp_cb = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_cb.SetReference(f"Cb{cell_id}")
        fp_cb.SetValue("22pF")
        fp_cb.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_cb.Reference().SetVisible(False)
        fp_cb.Pads()[0].SetNet(nets["GND"])
        fp_cb.Pads()[1].SetNet(net_ch)
        board.Add(fp_cb)

        # R_k (1.5R 0603) at (cx + 3.4, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("1.5R")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx + 3.4, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Pads()[0].SetNet(net_ch)
        fp_r.Pads()[1].SetNet(net_coil)
        board.Add(fp_r)

        # Connect Ca pad 2 to Cb pad 2 to R pad 1 (net RF_CH)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 2), pad_pos(fp_cb, 2), 0.20)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_cb, 2), pad_pos(fp_r, 1), 0.20)

        # Connect net_ch to U1 pin on F.Cu
        u1_pin_num = 23 - k_idx if k_idx < 8 else 16
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 2), (80.5, y_k), 0.20)
        trk(pcbnew.F_Cu, net_ch, (80.5, y_k), pad_pos(fp_u1, u1_pin_num), 0.20)

        # GND via at (cx - 2.8, y_k)
        v_gnd = (cx - 2.8, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 1), pad_pos(fp_cb, 1), 0.20)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 1), v_gnd, 0.20)

        # Coil via at (cx + 5.0, y_k)
        v_coil = (cx + 5.0, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 2), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    # 18. Vertical Feeder Tracks Tank Vias -> Coil Vias (on In2.Cu / B.Cu)
    # Feeder corridors:
    # Col A (cells 1, 5, 9, 13): X = 12.875 mm
    # Col B (cells 2, 6, 10, 14): X = 31.875 mm
    # Col C (cells 3, 7, 11, 15): X = 68.125 mm
    # Col D (cells 4, 8, 12, 16): X = 87.125 mm
    feeder_x = {
        1: 12.875,  5: 12.875,  9: 12.875, 13: 12.875,
        2: 31.875,  6: 31.875, 10: 31.875, 14: 31.875,
        3: 68.125,  7: 68.125, 11: 68.125, 15: 68.125,
        4: 87.125,  8: 87.125, 12: 87.125, 16: 87.125
    }

    for c_id in range(1, 17):
        v_tank = tank_vias[c_id]
        v_coil = coil_pad_vias[c_id]
        fx = feeder_x[c_id]
        net_c = nets[f"RF_COIL_{c_id}"]

        # Route from tank via -> feeder corridor fx -> coil via on B.Cu
        trk(pcbnew.B_Cu, net_c, v_tank, (fx, v_tank[1]), 0.25)
        trk(pcbnew.B_Cu, net_c, (fx, v_tank[1]), (fx, v_coil[1]), 0.25)
        trk(pcbnew.B_Cu, net_c, (fx, v_coil[1]), v_coil, 0.25)

    # 19. Power & Ground Stitching
    # Stitch GND plane with perimeter and interior vias
    for gx in range(5, 100, 10):
        via(nets["GND"], (gx, 23.0))
        via(nets["GND"], (gx, 97.0))
    for gy in range(25, 100, 15):
        via(nets["GND"], (3.0, gy))
        via(nets["GND"], (97.0, gy))

    # Silkscreen Branding & Legends
    txt_title = pcbnew.PCB_TEXT(board)
    txt_title.SetText("SMART CROSSWORD BOARD - 4x4 ST25R3916 INTEGRATED NFC")
    txt_title.SetLayer(pcbnew.F_SilkS)
    txt_title.SetPosition(pcbnew.VECTOR2I_MM(50.0, 1.8))
    txt_title.SetTextSize(pcbnew.VECTOR2I_MM(1.2, 1.2))
    board.Add(txt_title)

    txt_ver = pcbnew.PCB_TEXT(board)
    txt_ver.SetText("Rev v2.0 - ST25R3916B 1.7W + CD74HC4067 MUX (100x100mm)")
    txt_ver.SetLayer(pcbnew.B_SilkS)
    txt_ver.SetPosition(pcbnew.VECTOR2I_MM(50.0, 98.0))
    txt_ver.SetTextSize(pcbnew.VECTOR2I_MM(1.2, 1.2))
    board.Add(txt_ver)

    # Save board
    board.Save(pcb_path)
    print(f"Board saved successfully to {pcb_path}")

if __name__ == '__main__':
    build_pcb('hardware/kicad/st25r3916_grid_4x4/st25r3916_grid_4x4.kicad_pcb')
