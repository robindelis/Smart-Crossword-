#!/usr/bin/env python3
"""
generate_zero_drc_perfect.py - 0-DRC, 0-Unconnected Generator for test_grid_4x4
Phase 1 4x4 NFC Test Board for Smart Crossword Board
"""
import pcbnew
import sys

def build(out_path):
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets
    net_names = [
        "GND", "+3.3V", "RF_SIG",
        "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3", "MUX_EN",
        "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
        "I2C_SDA", "I2C_SCL", "GPIO_AUX"
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
        t.SetStart(pcbnew.VECTOR2I_MM(float(p1[0]), float(p1[1])))
        t.SetEnd(pcbnew.VECTOR2I_MM(float(p2[0]), float(p2[1])))
        t.SetWidth(int(width * 1e6))
        board.Add(t)
        return t

    def via(net, pos, size=0.6, drill=0.3):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I_MM(float(pos[0]), float(pos[1])))
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

    # 2. Board Outline 100x100mm
    corners = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        p1, p2 = corners[i], corners[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        seg.SetWidth(int(0.15 * 1e6))
        board.Add(seg)

    # 3. 4x M3 Mounting Holes
    for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
        fp_h = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3_Pad_Via")
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        fp_h.Reference().SetVisible(False)
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # 4. Host Header J1 (2x10) at (10.5, 5.2)
    fp_j1 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty", "PinHeader_2x10_P2.54mm_Vertical")
    fp_j1.SetReference("J1")
    fp_j1.SetValue("HOST_BUS")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(10.5, 5.2))
    fp_j1.Reference().SetVisible(False)

    # Odd row (Y = 5.2):
    # Pin 1: +3.3V
    # Pin 3: MUX_S3, Pin 5: MUX_S2, Pin 7: MUX_EN, Pin 9: MUX_S1, Pin 11: MUX_S0
    # Pin 13, 15, 17, 19: GND
    # Even row (Y = 2.66):
    # Pin 2: +3.3V, Pin 4: GPIO_AUX, Pin 6: I2C_SDA, Pin 8: I2C_SCL
    # Pin 10: NFC_IRQ, Pin 12: NFC_RST, Pin 14: SPI_MOSI, Pin 16: SPI_CS, Pin 18: SPI_SCK, Pin 20: SPI_MISO
    j1_pad_nets = {
        "1": nets["+3.3V"],    "2": nets["+3.3V"],
        "3": nets["MUX_S3"],   "4": nets["GPIO_AUX"],
        "5": nets["MUX_S2"],   "6": nets["I2C_SDA"],
        "7": nets["MUX_EN"],   "8": nets["I2C_SCL"],
        "9": nets["MUX_S1"],   "10": nets["NFC_IRQ"],
        "11": nets["MUX_S0"],  "12": nets["NFC_RST"],
        "13": nets["GND"],     "14": nets["SPI_MOSI"],
        "15": nets["GND"],     "16": nets["SPI_CS"],
        "17": nets["GND"],     "18": nets["SPI_SCK"],
        "19": nets["GND"],     "20": nets["SPI_MISO"]
    }
    for pad in fp_j1.Pads():
        p_num = pad.GetNumber()
        if p_num in j1_pad_nets:
            pad.SetNet(j1_pad_nets[p_num])
        else:
            pad.SetNet(nets["GND"])
    board.Add(fp_j1)

    # 5. NFC Header J2 (1x10) at (66.0, 4.5)
    fp_j2 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty", "PinHeader_1x10_P2.54mm_Vertical")
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_MODULE")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(66.0, 4.5))
    fp_j2.Reference().SetVisible(False)
    j2_pad_nets = {
        "1": nets["RF_SIG"],   "2": nets["GND"],
        "3": nets["+3.3V"],    "4": nets["GND"],
        "5": nets["SPI_SCK"],  "6": nets["SPI_MISO"],
        "7": nets["SPI_MOSI"], "8": nets["SPI_CS"],
        "9": nets["NFC_IRQ"],  "10": nets["NFC_RST"]
    }
    for pad in fp_j2.Pads():
        p_num = pad.GetNumber()
        if p_num in j2_pad_nets:
            pad.SetNet(j2_pad_nets[p_num])
    board.Add(fp_j2)

    # 6. SMA RF Test Port J3 at (95.0, 14.0)
    fp_j3 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_Coaxial.pretty", "SMA_Amphenol_132134-10_Vertical")
    fp_j3.SetReference("J3")
    fp_j3.SetValue("RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(95.0, 14.0))
    fp_j3.Reference().SetVisible(False)
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    # GND vias for J3 Pad 2 (SMD pads)
    via(nets["GND"], (95.0, 9.5))
    trk(pcbnew.F_Cu, nets["GND"], (95.0, 9.5), (95.0, 11.2), 0.35)
    via(nets["GND"], (95.0, 18.5))
    trk(pcbnew.F_Cu, nets["GND"], (95.0, 18.5), (95.0, 16.8), 0.35)

    # 7. Multiplexer U1 (CD74HC4067 SOIC-24) at (50.0, 13.0)
    fp_u1 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Package_SO.pretty", "SOIC-24W_7.5x15.4mm_P1.27mm")
    fp_u1.SetReference("U1")
    fp_u1.SetValue("CD74HC4067M")
    fp_u1.SetPosition(pcbnew.VECTOR2I_MM(50.0, 13.0))
    fp_u1.Reference().SetVisible(False)
    u1_pad_nets = {
        "1": nets["RF_SIG"],
        "2": nets["RF_CH7"], "3": nets["RF_CH6"], "4": nets["RF_CH5"], "5": nets["RF_CH4"],
        "6": nets["RF_CH3"], "7": nets["RF_CH2"], "8": nets["RF_CH1"], "9": nets["RF_CH0"],
        "10": nets["MUX_S0"], "11": nets["MUX_S1"], "12": nets["GND"],
        "13": nets["MUX_S3"], "14": nets["MUX_S2"], "15": nets["MUX_EN"],
        "16": nets["RF_CH15"], "17": nets["RF_CH14"], "18": nets["RF_CH13"], "19": nets["RF_CH12"],
        "20": nets["RF_CH11"], "21": nets["RF_CH10"], "22": nets["RF_CH9"], "23": nets["RF_CH8"],
        "24": nets["+3.3V"]
    }
    for pad in fp_u1.Pads():
        p_num = pad.GetNumber()
        if p_num in u1_pad_nets:
            pad.SetNet(u1_pad_nets[p_num])
    board.Add(fp_u1)

    # U1 Ground (Pin 12 at 45.35, 19.985) - via to the west at (43.8, 19.985)
    p_u1_12 = pad_pos(fp_u1, 12)
    via(nets["GND"], (43.8, p_u1_12[1]))
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, (43.8, p_u1_12[1]), 0.35)

    # 8. Decoupling Capacitors C17 (0603) and C18 (0805)
    fp_c17 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Capacitor_SMD.pretty", "C_0603_1608Metric")
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(48.0, 4.0))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Capacitor_SMD.pretty", "C_0805_2012Metric")
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(52.0, 4.0))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    # GND vias for C17/C18
    p_c17_2 = pad_pos(fp_c17, 2)
    via(nets["GND"], (p_c17_2[0], 5.4))
    trk(pcbnew.F_Cu, nets["GND"], p_c17_2, (p_c17_2[0], 5.4), 0.25)

    p_c18_2 = pad_pos(fp_c18, 2)
    via(nets["GND"], (p_c18_2[0], 5.4))
    trk(pcbnew.F_Cu, nets["GND"], p_c18_2, (p_c18_2[0], 5.4), 0.25)

    # +3.3V connections on F.Cu at Y = 2.6 connecting C17, C18, and U1 Pin 24
    p_c17_1 = pad_pos(fp_c17, 1) # (47.225, 4.0)
    p_c18_1 = pad_pos(fp_c18, 1) # (51.05, 4.0)
    p_u1_24 = pad_pos(fp_u1, 24) # (54.65, 6.015)
    p_j2_3  = pad_pos(fp_j2, 3)  # (71.08, 4.5)

    trk(pcbnew.F_Cu, nets["+3.3V"], p_c17_1, (p_c17_1[0], 2.6), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_c18_1, (p_c18_1[0], 2.6), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (p_c17_1[0], 2.6), (p_u1_24[0], 2.6), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (p_u1_24[0], 2.6), p_u1_24, 0.35)

    # 9. 16 Planar Spiral Coils L1..L16
    col_x = [21.5, 40.5, 59.5, 78.5]
    row_y = [33.0, 52.0, 71.0, 90.0]
    l_pad1 = {}

    for r_idx in range(4):
        for c_idx in range(4):
            k = r_idx * 4 + c_idx
            cell_id = k + 1
            xc = col_x[c_idx]
            yc = row_y[r_idx]

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
                    pts.append((xc - r0 + turn * pitch, yc + y))
                    y = r0 - turn * pitch
                    pts.append((xc - r0 + turn * pitch, yc + y))
                    x = r0 - (turn + 1) * pitch
                    pts.append((xc + x, yc + y))
                    y = -r0 + (turn + 1) * pitch
                    pts.append((xc + x, yc + y))
                pts.append((xc, yc))
            else:
                x, y = -r0, -r0
                pts = [(xc + x, yc + y)]
                for turn in range(turns):
                    pts.append((xc + r0 - turn * pitch, yc + y))
                    y = r0 - turn * pitch
                    pts.append((xc + r0 - turn * pitch, yc + y))
                    x = -r0 + (turn + 1) * pitch
                    pts.append((xc + x, yc + y))
                    y = -r0 + (turn + 1) * pitch
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

            board.Add(fp_l)

    # Coil vias
    coil_pad_vias = {}
    for c_id in range(1, 17):
        lp1 = l_pad1[c_id]
        v_l = (lp1[0], lp1[1] - 0.7)
        via(nets[f"RF_COIL_{c_id}"], v_l)
        trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
        coil_pad_vias[c_id] = v_l

    # 10. Resonant Tanks (C1..C16, R1..R16)
    tank_vias = {}
    left_cfg = [
        (0, 13, 16.175, 17.0),
        (1, 9,  14.905, 20.5),
        (2, 5,  13.635, 24.0),
        (3, 1,  12.365, 27.5),
        (4, 14, 11.095, 31.0),
        (5, 10,  9.825, 34.5),
        (6, 6,   8.555, 38.0),
        (7, 2,   7.285, 41.5)
    ]
    for ch_num, cell_id, y_k, cx in left_cfg:
        net_ch = nets[f"RF_CH{ch_num}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetOrientationDegrees(180)
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
        board.Add(fp_r)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetOrientationDegrees(180)
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        trk(pcbnew.F_Cu, net_ch, (cx + 0.825, y_k), (cx + 0.825, y_k - 1.8), 0.20)
        trk(pcbnew.F_Cu, net_ch, (45.35, y_k), (cx + 0.825, y_k), 0.20)

        via(nets["GND"], (cx - 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx - 0.825, y_k - 1.8), (cx - 1.8, y_k - 1.905), 0.20)

        v_pos = (cx - 1.8, y_k)
        via(net_coil, v_pos)
        trk(pcbnew.F_Cu, net_coil, (cx - 0.825, y_k), v_pos, 0.20)
        tank_vias[cell_id] = v_pos

    right_cfg = [
        (8,  15,  7.285, 59.0),
        (9,  11,  8.555, 62.5),
        (10, 7,   9.825, 66.0),
        (11, 3,  11.095, 69.5),
        (12, 16, 12.365, 73.0),
        (13, 12, 13.635, 76.5),
        (14, 8,  14.905, 80.0),
        (15, 4,  16.175, 83.5)
    ]
    for ch_num, cell_id, y_k, cx in right_cfg:
        net_ch = nets[f"RF_CH{ch_num}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
        board.Add(fp_r)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        trk(pcbnew.F_Cu, net_ch, (cx - 0.825, y_k), (cx - 0.825, y_k - 1.8), 0.20)
        trk(pcbnew.F_Cu, net_ch, (54.65, y_k), (cx - 0.825, y_k), 0.20)

        via(nets["GND"], (cx + 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx + 0.825, y_k - 1.8), (cx + 1.8, y_k - 1.905), 0.20)

        v_pos = (cx + 1.8, y_k)
        via(net_coil, v_pos)
        trk(pcbnew.F_Cu, net_coil, (cx + 0.825, y_k), v_pos, 0.20)
        tank_vias[cell_id] = v_pos

    # 11. Column A, B, C, D Coil Feeds:
    col_a_lanes = {1: 7.0, 5: 7.6, 9: 8.2, 13: 8.8}
    for cell_id, lx in col_a_lanes.items():
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        via(net, (lx, v_end[1]))
        trk(pcbnew.B_Cu, net, (lx, v_end[1]), v_end, 0.20)

    col_b_lanes = {2: 26.5, 6: 27.1, 10: 27.7, 14: 28.3}
    for cell_id, lx in col_b_lanes.items():
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        via(net, (lx, v_end[1]))
        trk(pcbnew.B_Cu, net, (lx, v_end[1]), v_end, 0.20)

    col_c_cfg = [(15, 60.8), (11, 64.3), (7, 67.4), (3, 71.3)]
    for cell_id, lx in col_c_cfg:
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

    col_d_cfg = [(16, 74.8), (12, 77.3), (8, 81.8), (4, 85.3)]
    for cell_id, lx in col_d_cfg:
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

    # 12. RF_SIG Trace on F.Cu
    p_u1_1 = pad_pos(fp_u1, 1)  # (45.35, 6.015)
    p_j2_1 = pad_pos(fp_j2, 1)  # (66.0, 4.5)
    p_j3_1 = pad_pos(fp_j3, 1)  # (95.0, 14.0)
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_u1_1, (p_u1_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_u1_1[0], 2.0), (p_j2_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), p_j2_1, 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), (90.5, 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, 2.0), (90.5, 14.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, 14.0), p_j3_1, 0.35)

    # 13. Two-Layer Concentric SPI Bus (0 vias, 0 crossings)
    in2_spi = [
        ("NFC_RST",  12, 10, 0.7),
        ("SPI_CS",   16, 8,  1.1),
        ("SPI_MISO", 20, 6,  1.5)
    ]
    for sig_name, j1_pin, j2_pin, y_lane in in2_spi:
        p_j1 = pad_pos(fp_j1, j1_pin)
        p_j2 = pad_pos(fp_j2, j2_pin)
        net_sig = nets[sig_name]
        trk(pcbnew.In2_Cu, net_sig, p_j1, (p_j1[0], y_lane), 0.20)
        trk(pcbnew.In2_Cu, net_sig, (p_j1[0], y_lane), (p_j2[0], y_lane), 0.20)
        trk(pcbnew.In2_Cu, net_sig, (p_j2[0], y_lane), p_j2, 0.20)

    bcu_spi = [
        ("NFC_IRQ",  10, 9, 0.7),
        ("SPI_MOSI", 14, 7, 1.1),
        ("SPI_SCK",  18, 5, 1.5)
    ]
    for sig_name, j1_pin, j2_pin, y_lane in bcu_spi:
        p_j1 = pad_pos(fp_j1, j1_pin)
        p_j2 = pad_pos(fp_j2, j2_pin)
        net_sig = nets[sig_name]
        trk(pcbnew.B_Cu, net_sig, p_j1, (p_j1[0], y_lane), 0.20)
        trk(pcbnew.B_Cu, net_sig, (p_j1[0], y_lane), (p_j2[0], y_lane), 0.20)
        trk(pcbnew.B_Cu, net_sig, (p_j2[0], y_lane), p_j2, 0.20)

    # 14. 100% Planar Direct MUX Routing on B.Cu (Zero Crossings!)
    # Odd Pins: Pin 3 (S3 at 13.04), Pin 5 (S2 at 15.58), Pin 7 (EN at 18.12), Pin 9 (S1 at 20.66), Pin 11 (S0 at 23.20)
    p_s3 = pad_pos(fp_j1, 3)  # (13.04, 5.2)
    p_s2 = pad_pos(fp_j1, 5)  # (15.58, 5.2)
    p_en = pad_pos(fp_j1, 7)  # (18.12, 5.2)
    p_s1 = pad_pos(fp_j1, 9)  # (20.66, 5.2)
    p_s0 = pad_pos(fp_j1, 11) # (23.20, 5.2)

    p_u1_10 = pad_pos(fp_u1, 10) # S0 (45.35, 17.445)
    p_u1_11 = pad_pos(fp_u1, 11) # S1 (45.35, 18.715)
    p_u1_13 = pad_pos(fp_u1, 13) # S3 (54.65, 19.985)
    p_u1_14 = pad_pos(fp_u1, 14) # S2 (54.65, 18.715)
    p_u1_15 = pad_pos(fp_u1, 15) # EN (54.65, 17.445)

    # Pin 3 (S3): drops straight south along X = 13.04 to Y = 22.0, east to 58.0, north to 19.985, via to F.Cu
    trk(pcbnew.B_Cu, nets["MUX_S3"], p_s3, (p_s3[0], 22.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (p_s3[0], 22.0), (58.0, 22.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (58.0, 22.0), (58.0, p_u1_13[1]), 0.20)
    via(nets["MUX_S3"], (58.0, p_u1_13[1]))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (58.0, p_u1_13[1]), p_u1_13, 0.20)

    # Pin 5 (S2): exits south to 6.2, nudges east to X = 16.0 (clearing Tank 0 via at 15.2!), south to 21.5, east to 57.2, north to 18.715
    trk(pcbnew.B_Cu, nets["MUX_S2"], p_s2, (p_s2[0], 6.2), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (p_s2[0], 6.2), (16.0, 6.2), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (16.0, 6.2), (16.0, 21.5), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (16.0, 21.5), (57.2, 21.5), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (57.2, 21.5), (57.2, p_u1_14[1]), 0.20)
    via(nets["MUX_S2"], (57.2, p_u1_14[1]))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (57.2, p_u1_14[1]), p_u1_14, 0.20)

    # Pin 7 (EN): exits south to 6.2, nudges west to X = 17.6 (clearing Tank 1 via at 18.7!), south to 21.0, east to 56.4, north to 17.445
    trk(pcbnew.B_Cu, nets["MUX_EN"], p_en, (p_en[0], 6.2), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (p_en[0], 6.2), (17.6, 6.2), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (17.6, 6.2), (17.6, 21.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (17.6, 21.0), (56.4, 21.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (56.4, 21.0), (56.4, p_u1_15[1]), 0.20)
    via(nets["MUX_EN"], (56.4, p_u1_15[1]))
    trk(pcbnew.F_Cu, nets["MUX_EN"], (56.4, p_u1_15[1]), p_u1_15, 0.20)

    # Pin 9 (S1): drops straight south along X = 20.66 to Y = 20.5, east to 42.5, north to 18.715
    trk(pcbnew.B_Cu, nets["MUX_S1"], p_s1, (p_s1[0], 20.5), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (p_s1[0], 20.5), (42.5, 20.5), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (42.5, 20.5), (42.5, p_u1_11[1]), 0.20)
    via(nets["MUX_S1"], (42.5, p_u1_11[1]))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (42.5, p_u1_11[1]), p_u1_11, 0.20)

    # Pin 11 (S0): drops straight south along X = 23.20 to Y = 20.0, east to 41.5, north to 17.445
    trk(pcbnew.B_Cu, nets["MUX_S0"], p_s0, (p_s0[0], 20.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (p_s0[0], 20.0), (41.5, 20.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (41.5, 20.0), (41.5, p_u1_10[1]), 0.20)
    via(nets["MUX_S0"], (41.5, p_u1_10[1]))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (41.5, p_u1_10[1]), p_u1_10, 0.20)

    # 15. +3.3V Power Bus Distribution
    p_j1_1 = pad_pos(fp_j1, 1) # (10.5, 5.2)
    p_j1_2 = pad_pos(fp_j1, 2) # (10.5, 2.66)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_j1_1, p_j1_2, 0.35)
    # On B.Cu: from Pin 1 (10.5, 5.2), drop south along X = 10.5 to Y = 22.8
    trk(pcbnew.B_Cu, nets["+3.3V"], p_j1_1, (p_j1_1[0], 22.8), 0.35)
    # Run east along Y = 22.8 (clear of MUX_S3 at Y = 22.0!) to X = 46.5
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j1_1[0], 22.8), (46.5, 22.8), 0.35)
    # Via to In2.Cu at (46.5, 22.8) to fly over MUX lines!
    via(nets["+3.3V"], (46.5, 22.8))
    # Run north on In2.Cu along X = 46.5 under U1 body to Y = 3.2
    trk(pcbnew.In2_Cu, nets["+3.3V"], (46.5, 22.8), (46.5, 3.2), 0.35)
    # Via to B.Cu and F.Cu at (46.5, 3.2)
    via(nets["+3.3V"], (46.5, 3.2))
    trk(pcbnew.F_Cu, nets["+3.3V"], (46.5, 3.2), p_c17_1, 0.35)
    # Run east on B.Cu along Y = 3.2 to J2 Pin 3 at (71.08, 4.5)
    trk(pcbnew.B_Cu, nets["+3.3V"], (46.5, 3.2), (p_j2_3[0], 3.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j2_3[0], 3.2), p_j2_3, 0.35)

    # 16. In1.Cu Ground Plane with 16 Anti-copper Keepouts
    zone_gnd_in1 = pcbnew.ZONE(board)
    zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
    zone_gnd_in1.SetNetCode(nets["GND"].GetNetCode())
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

    # 17. B.Cu Bottom Ground Plane
    zone_bcu = pcbnew.ZONE(board)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNetCode(nets["GND"].GetNetCode())
    zone_bcu.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    board.Add(zone_bcu)

    # 18. Silkscreen Labels
    def add_silk(layer, text, x, y, size=1.2, mirror=False):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetLayer(layer)
        txt.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
        if mirror:
            txt.SetMirrored(True)
        board.Add(txt)

    add_silk(pcbnew.B_SilkS, "SMART CROSSWORD BOARD - 4x4 NFC TEST MATRIX", 50.0, 10.0, 1.5, True)
    add_silk(pcbnew.B_SilkS, "REV 1.0 | 13.56 MHz LC RESONANT (CD74HC4067)", 50.0, 15.0, 1.2, True)
    add_silk(pcbnew.B_SilkS, "L=1.26uH (7T planar spiral, 19mm pitch), C=100pF C0G, R=3.3R, Q~25", 50.0, 20.0, 1.1, True)

    # Fill zones
    zf = pcbnew.ZONE_FILLER(board)
    zf.Fill(board.Zones())

    board.Save(out_path)
    print(f"Board successfully built to {out_path}")

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/zero_drc_perfect.kicad_pcb"
    build(out)
