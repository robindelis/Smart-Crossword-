#!/usr/bin/python3
"""
Test layout for st25r3916_grid_4x4 to verify zero DRC violations.
"""
import pcbnew
import math

def build():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets
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

    # 2. Board Outline
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

    # 4. Host Header J1 (2x10) rotated 90 deg at (23.0, 3.5)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(23.0, 3.5))
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

    # J1 GND pins (17, 18, 19, 20)
    for p_num in [17, 18, 19, 20]:
        via(nets["GND"], pad_pos(fp_j1, p_num))

    # 5. U1 CD74HC4067 at (50.0, 14.0)
    fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
    fp_u1.SetReference("U1")
    fp_u1.SetValue("CD74HC4067M")
    fp_u1.SetPosition(pcbnew.VECTOR2I_MM(50.0, 14.0))
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

    # U1 Ground (Pin 12)
    p_u1_12 = pad_pos(fp_u1, 12)
    v_u1_gnd = (p_u1_12[0] - 1.5, p_u1_12[1])
    via(nets["GND"], v_u1_gnd)
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, v_u1_gnd, 0.35)

    # U1 Decoupling C17 (0.1uF), C18 (10uF) near Pin 24
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(51.0, 4.5))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Pads()[0].SetNet(nets["+5V"])
    fp_c17.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(47.0, 4.5))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Pads()[0].SetNet(nets["+5V"])
    fp_c18.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c18)

    p_c17_2 = pad_pos(fp_c17, 2)
    v_c17_g = (p_c17_2[0], p_c17_2[1] + 1.2)
    via(nets["GND"], v_c17_g)
    trk(pcbnew.F_Cu, nets["GND"], p_c17_2, v_c17_g, 0.25)

    p_c18_2 = pad_pos(fp_c18, 2)
    v_c18_g = (p_c18_2[0], p_c18_2[1] + 1.2)
    via(nets["GND"], v_c18_g)
    trk(pcbnew.F_Cu, nets["GND"], p_c18_2, v_c18_g, 0.25)

    p_c17_1 = pad_pos(fp_c17, 1)
    p_c18_1 = pad_pos(fp_c18, 1)
    trk(pcbnew.F_Cu, nets["+5V"], p_c17_1, p_c18_1, 0.35)
    trk(pcbnew.F_Cu, nets["+5V"], p_c17_1, (54.65, 4.5), 0.35)
    trk(pcbnew.F_Cu, nets["+5V"], (54.65, 4.5), pad_pos(fp_u1, 24), 0.35)

    # 6. MUX Control Resistors R17..R21 directly below U1 at Y = 22.2 mm
    for r_ref, r_val, r_net, p_dest, rx, r_vcc_gnd in [
        ("R18", "100k", "MUX_S0", 10, 44.0, "GND"),
        ("R19", "100k", "MUX_S1", 11, 47.0, "GND"),
        ("R17", "10k",  "MUX_EN", 15, 50.0, "+3.3V"),
        ("R20", "100k", "MUX_S2", 14, 53.0, "GND"),
        ("R21", "100k", "MUX_S3", 13, 56.0, "GND"),
    ]:
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(r_ref)
        fp_r.SetValue(r_val)
        fp_r.SetOrientationDegrees(90)
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(rx, 22.2))
        fp_r.Reference().SetVisible(False)
        fp_r.Pads()[0].SetNet(nets[r_net])
        fp_r.Pads()[1].SetNet(nets[r_vcc_gnd])
        board.Add(fp_r)

        via(nets[r_vcc_gnd], (rx, 23.6))
        trk(pcbnew.F_Cu, nets[r_vcc_gnd], pad_pos(fp_r, 2), (rx, 23.6), 0.25)
        trk(pcbnew.F_Cu, nets[r_net], pad_pos(fp_r, 1), pad_pos(fp_u1, p_dest), 0.20)

    # 7. MUX Control Lines on B.Cu (J1 -> U1)
    ctrl_routes = [
        ("MUX_EN", 11, 17.5, 57.0, 18.445, pad_pos(fp_u1, 15)),
        ("MUX_S2", 9,  18.5, 57.8, 19.715, pad_pos(fp_u1, 14)),
        ("MUX_S3", 7,  19.5, 58.6, 20.985, pad_pos(fp_u1, 13)),
        ("MUX_S1", 5,  20.5, 43.5, 19.715, pad_pos(fp_u1, 11)),
        ("MUX_S0", 3,  21.5, 42.5, 18.445, pad_pos(fp_u1, 10))
    ]
    for net_name, j1_pin, y_turn, x_end, y_dest, u1_pad in ctrl_routes:
        p_j1 = pad_pos(fp_j1, j1_pin)
        trk(pcbnew.B_Cu, nets[net_name], p_j1, (p_j1[0], y_turn), 0.18)
        trk(pcbnew.B_Cu, nets[net_name], (p_j1[0], y_turn), (x_end, y_turn), 0.18)
        trk(pcbnew.B_Cu, nets[net_name], (x_end, y_turn), (x_end, y_dest), 0.18)
        via(nets[net_name], (x_end, y_dest))
        trk(pcbnew.F_Cu, nets[net_name], (x_end, y_dest), u1_pad, 0.18)

    # 8. ST25R3916B (U2) at (75.0, 4.2)
    fp_u2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_DFN_QFN.pretty', 'VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm_ThermalVias')
    fp_u2.SetReference("U2")
    fp_u2.SetValue("ST25R3916B-AQFT")
    fp_u2.SetPosition(pcbnew.VECTOR2I_MM(75.0, 4.2))
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

    # 9. Crystal Y1 at (84.5, 4.2)
    fp_y1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm')
    fp_y1.SetReference("Y1")
    fp_y1.SetValue("27.12MHz")
    fp_y1.SetPosition(pcbnew.VECTOR2I_MM(84.5, 4.2))
    for pad in fp_y1.Pads():
        p_num = pad.GetNumber()
        if p_num == "1": pad.SetNet(nets["OSC_OUT"])
        elif p_num == "3": pad.SetNet(nets["OSC_IN"])
        else: pad.SetNet(nets["GND"])
    board.Add(fp_y1)

    # Crystal GND pads
    for p_num in [2, 4]:
        p = pad_pos(fp_y1, p_num)
        via(nets["GND"], (p[0], p[1] + (1.2 if p_num==2 else -1.2)))
        trk(pcbnew.F_Cu, nets["GND"], p, (p[0], p[1] + (1.2 if p_num==2 else -1.2)), 0.25)

    # C22 (12pF) and C23 (12pF) load caps
    fp_c22 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c22.SetReference("C22")
    fp_c22.SetValue("12pF")
    fp_c22.SetPosition(pcbnew.VECTOR2I_MM(81.0, 2.0))
    fp_c22.Pads()[0].SetNet(nets["OSC_OUT"])
    fp_c22.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c22)

    via(nets["GND"], (81.0, 0.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c22, 2), (81.0, 0.8), 0.25)
    trk(pcbnew.F_Cu, nets["OSC_OUT"], pad_pos(fp_u2, 4), pad_pos(fp_c22, 1), 0.18)
    trk(pcbnew.F_Cu, nets["OSC_OUT"], pad_pos(fp_c22, 1), pad_pos(fp_y1, 1), 0.18)

    fp_c23 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c23.SetReference("C23")
    fp_c23.SetValue("12pF")
    fp_c23.SetPosition(pcbnew.VECTOR2I_MM(81.0, 6.4))
    fp_c23.Pads()[0].SetNet(nets["OSC_IN"])
    fp_c23.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c23)

    via(nets["GND"], (81.0, 7.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c23, 2), (81.0, 7.6), 0.25)
    trk(pcbnew.F_Cu, nets["OSC_IN"], pad_pos(fp_u2, 5), pad_pos(fp_c23, 1), 0.18)
    trk(pcbnew.F_Cu, nets["OSC_IN"], pad_pos(fp_c23, 1), pad_pos(fp_y1, 3), 0.18)

    # 10. EMC Filter L17 (470nH 0805), C37 (180pF 0603), C39 (18pF 0603)
    # L17 at (68.0, 4.2)
    fp_l17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Inductor_SMD.pretty', 'L_0805_2012Metric')
    fp_l17.SetReference("L17")
    fp_l17.SetValue("470nH")
    fp_l17.SetPosition(pcbnew.VECTOR2I_MM(68.0, 4.2))
    fp_l17.Pads()[0].SetNet(nets["RFO1"])
    fp_l17.Pads()[1].SetNet(nets["RF_FLT"])
    board.Add(fp_l17)

    # Connect U2.13 (RFO1) to L17.1
    trk(pcbnew.F_Cu, nets["RFO1"], pad_pos(fp_u2, 13), pad_pos(fp_l17, 1), 0.25)

    # C37 (180pF 0603) at (64.5, 4.2) rotated 90
    fp_c37 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c37.SetReference("C37")
    fp_c37.SetValue("180pF")
    fp_c37.SetOrientationDegrees(90)
    fp_c37.SetPosition(pcbnew.VECTOR2I_MM(64.5, 4.2))
    fp_c37.Pads()[0].SetNet(nets["RF_FLT"])
    fp_c37.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c37)

    via(nets["GND"], (64.5, 5.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c37, 2), (64.5, 5.8), 0.25)
    trk(pcbnew.F_Cu, nets["RF_FLT"], pad_pos(fp_l17, 2), pad_pos(fp_c37, 1), 0.30)

    # C39 (18pF 0603) at (61.5, 4.2)
    fp_c39 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c39.SetReference("C39")
    fp_c39.SetValue("18pF")
    fp_c39.SetPosition(pcbnew.VECTOR2I_MM(61.5, 4.2))
    fp_c39.Pads()[0].SetNet(nets["RF_FLT"])
    fp_c39.Pads()[1].SetNet(nets["RF_SIG"])
    board.Add(fp_c39)
    trk(pcbnew.F_Cu, nets["RF_FLT"], pad_pos(fp_c37, 1), pad_pos(fp_c39, 1), 0.30)

    # Connect C39.2 (RF_SIG) to U1 Pin 1 (at 45.35, 7.015)
    p_u1_1 = pad_pos(fp_u1, 1)
    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_c39, 2), (p_u1_1[0], 4.2), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_u1_1[0], 4.2), p_u1_1, 0.35)

    # 11. RX Divider: C40 (10pF), C41 (150pF), C38 (150pF)
    # C40 (10pF) at (61.5, 1.8)
    fp_c40 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c40.SetReference("C40")
    fp_c40.SetValue("10pF")
    fp_c40.SetPosition(pcbnew.VECTOR2I_MM(61.5, 1.8))
    fp_c40.Pads()[0].SetNet(nets["RF_SIG"])
    fp_c40.Pads()[1].SetNet(nets["RFI1"])
    board.Add(fp_c40)
    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_c39, 2), pad_pos(fp_c40, 1), 0.20)

    # C41 (150pF) at (65.0, 1.8)
    fp_c41 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c41.SetReference("C41")
    fp_c41.SetValue("150pF")
    fp_c41.SetPosition(pcbnew.VECTOR2I_MM(65.0, 1.8))
    fp_c41.Pads()[0].SetNet(nets["RFI1"])
    fp_c41.Pads()[1].SetNet(nets["GND"])
    board.Add(fp_c41)

    via(nets["GND"], (65.0, 0.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c41, 2), (65.0, 0.6), 0.25)
    trk(pcbnew.F_Cu, nets["RFI1"], pad_pos(fp_c40, 2), pad_pos(fp_c41, 1), 0.20)
    trk(pcbnew.F_Cu, nets["RFI1"], pad_pos(fp_c41, 1), pad_pos(fp_u2, 22), 0.18)

    # C38 (150pF) at (68.5, 1.8)
    fp_c38 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c38.SetReference("C38")
    fp_c38.SetValue("150pF")
    fp_c38.SetPosition(pcbnew.VECTOR2I_MM(68.5, 1.8))
    fp_c38.Pads()[0].SetNet(nets["RFI2"])
    fp_c38.Pads()[1].SetNet(nets["AGDC"])
    board.Add(fp_c38)
    trk(pcbnew.F_Cu, nets["RFI2"], pad_pos(fp_c38, 1), pad_pos(fp_u2, 23), 0.18)
    trk(pcbnew.F_Cu, nets["AGDC"], pad_pos(fp_c38, 2), pad_pos(fp_u2, 24), 0.18)

    # 12. SMA J3 at (93.0, 4.2)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("RF_TEST_SMA")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 4.2))
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    trk(pcbnew.F_Cu, nets["RF_SIG"], pad_pos(fp_c39, 2), (pad_pos(fp_c39, 2)[0], 3.0), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (pad_pos(fp_c39, 2)[0], 3.0), (88.0, 3.0), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.0, 3.0), (88.0, 4.2), 0.30)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.0, 4.2), pad_pos(fp_j3, 1), 0.30)

    # 13. Digital SPI J1 -> U2 (In2.Cu)
    spi_routes = [
        ("SPI_SCK",  4,  30, 0.6),
        ("SPI_MISO", 6,  32, 0.9),
        ("SPI_MOSI", 8,  31, 1.2),
        ("SPI_CS",   10, 29, 1.5),
        ("ST_IRQ",   12, 27, 1.8)
    ]
    for net_name, j1_pin, u2_pin, y_route in spi_routes:
        p1 = pad_pos(fp_j1, j1_pin)
        p2 = pad_pos(fp_u2, u2_pin)
        trk(pcbnew.In2_Cu, nets[net_name], p1, (p1[0], y_route), 0.18)
        trk(pcbnew.In2_Cu, nets[net_name], (p1[0], y_route), (p2[0], y_route), 0.18)
        trk(pcbnew.In2_Cu, nets[net_name], (p2[0], y_route), p2, 0.18)

    # 14. 16 Planar Coils L1..L16
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

    # Coil vias
    coil_pad_vias = {}
    for c_id in range(1, 17):
        lp1 = l_pad1[c_id]
        v_l = (lp1[0], lp1[1] - 0.7)
        via(nets[f"RF_COIL_{c_id}"], v_l)
        trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
        coil_pad_vias[c_id] = v_l

    # 15. In1.Cu Ground Plane with Keepouts
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

    # 17. 16 In-line Resonant Tanks
    tank_vias = {}
    u1_left_y = [17.175, 15.905, 14.635, 13.365, 12.095, 10.825, 9.555, 8.285]
    u1_right_y = [8.285, 9.555, 10.825, 12.095, 13.365, 14.635, 15.905, 17.175]

    left_cell_ids = [1, 5, 9, 13, 2, 6, 10, 14]
    left_cx_list = [20.0, 20.0, 20.0, 20.0, 37.0, 37.0, 37.0, 37.0]

    for k in range(8):
        cell_id = left_cell_ids[k]
        y_k = u1_left_y[k]
        cx = left_cx_list[k]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # R: 1.5R at (cx - 1.2, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("1.5R")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.2, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Pads()[0].SetNet(net_coil)
        fp_r.Pads()[1].SetNet(net_ch)
        board.Add(fp_r)

        # Ca: 100pF at (cx + 1.2, y_k)
        fp_ca = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_ca.SetReference(f"Ca{cell_id}")
        fp_ca.SetValue("100pF")
        fp_ca.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_ca.Reference().SetVisible(False)
        fp_ca.Pads()[0].SetNet(net_ch)
        fp_ca.Pads()[1].SetNet(nets["GND"])
        board.Add(fp_ca)

        # Cb: 22pF at (cx + 3.2, y_k)
        fp_cb = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_cb.SetReference(f"Cb{cell_id}")
        fp_cb.SetValue("22pF")
        fp_cb.SetPosition(pcbnew.VECTOR2I_MM(cx + 3.2, y_k))
        fp_cb.Reference().SetVisible(False)
        fp_cb.Pads()[0].SetNet(net_ch)
        fp_cb.Pads()[1].SetNet(nets["GND"])
        board.Add(fp_cb)

        # Connect R pad 2 to Ca pad 1 to Cb pad 1
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_r, 2), pad_pos(fp_ca, 1), 0.20)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 1), pad_pos(fp_cb, 1), 0.20)

        # Connect Cb pad 1 to U1 pin
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_cb, 1), (45.35, y_k), 0.20)

        # GND via at (cx + 4.8, y_k)
        v_gnd = (cx + 4.8, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 2), pad_pos(fp_cb, 2), 0.20)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_cb, 2), v_gnd, 0.20)

        # Coil via at (cx - 2.8, y_k)
        v_coil = (cx - 2.8, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 1), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    right_cell_ids = [15, 11, 7, 3, 16, 12, 8, 4]
    right_cx_list = [63.0, 63.0, 63.0, 63.0, 80.0, 80.0, 80.0, 80.0]

    for k_idx, k in enumerate(range(8, 16)):
        cell_id = right_cell_ids[k_idx]
        y_k = u1_right_y[k_idx]
        cx = right_cx_list[k_idx]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # Ca: 100pF at (cx - 3.2, y_k)
        fp_ca = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_ca.SetReference(f"Ca{cell_id}")
        fp_ca.SetValue("100pF")
        fp_ca.SetPosition(pcbnew.VECTOR2I_MM(cx - 3.2, y_k))
        fp_ca.Reference().SetVisible(False)
        fp_ca.Pads()[0].SetNet(nets["GND"])
        fp_ca.Pads()[1].SetNet(net_ch)
        board.Add(fp_ca)

        # Cb: 22pF at (cx - 1.2, y_k)
        fp_cb = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_cb.SetReference(f"Cb{cell_id}")
        fp_cb.SetValue("22pF")
        fp_cb.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.2, y_k))
        fp_cb.Reference().SetVisible(False)
        fp_cb.Pads()[0].SetNet(nets["GND"])
        fp_cb.Pads()[1].SetNet(net_ch)
        board.Add(fp_cb)

        # R: 1.5R at (cx + 1.2, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("1.5R")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Pads()[0].SetNet(net_ch)
        fp_r.Pads()[1].SetNet(net_coil)
        board.Add(fp_r)

        # Connect Ca.2 to Cb.2 to R.1
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 2), pad_pos(fp_cb, 2), 0.20)
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_cb, 2), pad_pos(fp_r, 1), 0.20)

        # Connect to U1
        trk(pcbnew.F_Cu, net_ch, pad_pos(fp_ca, 2), (54.65, y_k), 0.20)

        # GND via at (cx - 4.8, y_k)
        v_gnd = (cx - 4.8, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 1), pad_pos(fp_cb, 1), 0.20)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_ca, 1), v_gnd, 0.20)

        # Coil via at (cx + 2.8, y_k)
        v_coil = (cx + 2.8, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 2), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    # 18. Feeder Tracks Tank Vias -> Coil Vias (B.Cu)
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

        trk(pcbnew.B_Cu, net_c, v_tank, (fx, v_tank[1]), 0.25)
        trk(pcbnew.B_Cu, net_c, (fx, v_tank[1]), (fx, v_coil[1]), 0.25)
        trk(pcbnew.B_Cu, net_c, (fx, v_coil[1]), v_coil, 0.25)

    board.Save('hardware/kicad/st25r3916_grid_4x4/st25r3916_grid_4x4.kicad_pcb')
    print("Test layout saved!")

if __name__ == '__main__':
    build()
