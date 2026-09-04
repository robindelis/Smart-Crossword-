#!/usr/bin/env python3
"""
Test 2-layer clean orthogonal routing for test_grid_4x4
"""
import os
import pcbnew

PROJECT_DIR = "/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4"
TEST_PCB = os.path.join(PROJECT_DIR, "test_twolayer.kicad_pcb")

def build_board():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets
    nets = {}
    net_names = [
        "GND", "+3.3V", "RF_SIG", "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
        "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
        "I2C_SDA", "I2C_SCL", "GPIO_AUX"
    ] + [f"RF_CH{k}" for k in range(16)] + [f"RF_COIL_{k+1}" for k in range(16)]

    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    def trk(layer, net, p1, p2, w=0.25):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        t.SetWidth(int(w * 1e6))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)

    def via(net, pos, drill=0.3, size=0.6):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetDrill(int(drill * 1e6))
        v.SetWidth(int(size * 1e6))
        v.SetNet(net)
        board.Add(v)

    # 2. Outline 100x100
    for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        seg.SetWidth(int(0.15 * 1e6))
        board.Add(seg)

    # 3. 4x M3 Holes
    for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
        fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # 4. U1 CD74HC4067M (SOIC-24) at (50.0, 13.0)
    fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
    fp_u1.SetReference("U1")
    fp_u1.SetValue("CD74HC4067M")
    fp_u1.SetPosition(pcbnew.VECTOR2I_MM(50.0, 13.0))
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

    # 5. J1 Host Header 2x10 rotated 90 deg at (12.0, 5.5)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(12.0, 5.5))
    j1_pad_nets = {
        "1": nets["+3.3V"], "2": nets["+3.3V"],
        "3": nets["MUX_S0"], "4": nets["SPI_SCK"],
        "5": nets["MUX_S1"], "6": nets["SPI_MISO"],
        "7": nets["MUX_S2"], "8": nets["SPI_MOSI"],
        "9": nets["MUX_S3"], "10": nets["SPI_CS"],
        "11": nets["MUX_EN"], "12": nets["NFC_IRQ"],
        "13": nets["I2C_SDA"], "14": nets["NFC_RST"],
        "15": nets["I2C_SCL"], "16": nets["GPIO_AUX"],
        "17": nets["GND"], "18": nets["GND"],
        "19": nets["GND"], "20": nets["GND"]
    }
    for pad in fp_j1.Pads():
        p_num = pad.GetNumber()
        if p_num in j1_pad_nets:
            pad.SetNet(j1_pad_nets[p_num])
    board.Add(fp_j1)

    # 6. J2 NFC Transceiver Header 1x10 rotated 90 deg at (65.0, 5.5)
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_Module_Header")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(65.0, 5.5))
    j2_pad_nets = {
        "1": nets["RF_SIG"], "2": nets["GND"],
        "3": nets["+3.3V"],  "4": nets["GND"],
        "5": nets["SPI_SCK"], "6": nets["SPI_MISO"],
        "7": nets["SPI_MOSI"], "8": nets["SPI_CS"],
        "9": nets["NFC_IRQ"], "10": nets["NFC_RST"]
    }
    for pad in fp_j2.Pads():
        p_num = pad.GetNumber()
        if p_num in j2_pad_nets:
            pad.SetNet(j2_pad_nets[p_num])
    board.Add(fp_j2)

    # 7. J3 SMA RF Port at (93.0, 15.0)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("SMA_RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 15.0))
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    # 8. Decoupling Capacitors & Resistors (placed at Y=2.0 mm)
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(50.0, 2.0))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(55.0, 2.0))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(45.0, 2.0))
    fp_r17.Reference().SetVisible(False)
    fp_r17.Value().SetVisible(False)
    for pad in fp_r17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["MUX_EN"])
    board.Add(fp_r17)

    # Pulldowns R18..R21
    for idx, s_name in enumerate(["MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3"]):
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{18+idx}")
        fp_r.SetValue("100k")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(20.0 + idx * 3.5, 13.0))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[s_name] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_r)

    # 9. Coils L1..L16
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
            pad1_x = xc - 8.625
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

            x = -r0
            y = -r0
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

            # B.Cu return trace to ground plane
            trk(pcbnew.B_Cu, nets["GND"], (xc, yc), (xc - 9.0, yc), 0.35)

    # 10. 19mm silkscreen grid lines
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

    # 11. In1.Cu Ground Plane with 16 Anti-copper Keepouts
    zone_gnd_in1 = pcbnew.ZONE(board)
    zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
    zone_gnd_in1.SetNet(nets["GND"])
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

    # 12. B.Cu Bottom Ground Shield Plane
    zone_bcu = pcbnew.ZONE(board)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNet(nets["GND"])
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    board.Add(zone_bcu)

    # 13. RF_SIG Microstrip: U1 COM -> J2 pin 1 -> J3 pin 1
    trk(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 6.015), (45.35, 3.8), 0.5)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 3.8), (65.0, 3.8), 0.5)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 3.8), (65.0, 5.5), 0.5)

    trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 5.5), (65.0, 8.5), 0.5)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 8.5), (89.0, 8.5), 0.5)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 8.5), (89.0, 15.0), 0.5)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 15.0), (93.0, 15.0), 0.5)

    # 14. Place 16 Capacitors and 16 Resistors:
    # We place each pair (C, R) vertically aligned with space!
    # Left bank: channels 0..7 (cells 1..8)
    # Right bank: channels 8..15 (cells 9..16)
    # Left bank: 8 channels at X = 38.0 (caps) and X = 35.0 (resistors), Y from 6.0 to 20.0 (spacing 1.8mm)
    # Right bank: 8 channels at X = 62.0 (caps) and X = 65.0 (resistors), Y from 6.0 to 20.0 (spacing 1.8mm)
    r_pad1 = {}
    r_pad2 = {}
    c_pad1 = {}
    c_pad2 = {}

    u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]   # CH0..CH7
    u1_right_y = [7.285, 8.555, 9.825, 11.095, 12.365, 13.635, 14.905, 16.175]  # CH8..CH15

    for k in range(8):
        cell_id = k + 1
        y_c = 6.2 + k * 1.8
        # Cap at X = 40.0, Resistor at X = 35.5
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(40.0, y_c))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        # Pad 1 is at X=40-0.825=39.175 (towards R), Pad 2 is at X=40+0.825=40.825 (GND)
        for pad in fp_c.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)
        c_pad1[cell_id] = (39.175, y_c)
        c_pad2[cell_id] = (40.825, y_c)

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(35.5, y_c))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        # Pad 1 is at X=35.5+0.825=36.325 (RF_CHk), Pad 2 is at X=35.5-0.825=34.675 (RF_COIL)
        for pad in fp_r.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
        board.Add(fp_r)
        r_pad1[cell_id] = (36.325, y_c)
        r_pad2[cell_id] = (34.675, y_c)

        # Connect U1 pin to C.1 and R.1:
        # U1 pin is at (45.35, u1_left_y[k])
        u_pt = (45.35, u1_left_y[k])
        # Track from U1 pin to (42.0, u1_left_y[k]) -> (42.0, y_c) -> C.1 (39.175, y_c) -> R.1 (36.325, y_c)
        trk(pcbnew.In2_Cu, nets[f"RF_CH{k}"], u_pt, (42.0, u1_left_y[k]))
        trk(pcbnew.In2_Cu, nets[f"RF_CH{k}"], (42.0, u1_left_y[k]), (42.0, y_c))
        via(nets[f"RF_CH{k}"], (42.0, y_c))
        trk(pcbnew.F_Cu, nets[f"RF_CH{k}"], (42.0, y_c), c_pad1[cell_id])
        trk(pcbnew.F_Cu, nets[f"RF_CH{k}"], c_pad1[cell_id], r_pad1[cell_id])

        # GND via for C.2:
        via(nets["GND"], (c_pad2[cell_id][0] + 0.9, y_c))
        trk(pcbnew.F_Cu, nets["GND"], c_pad2[cell_id], (c_pad2[cell_id][0] + 0.9, y_c))

    for k in range(8, 16):
        cell_id = k + 1
        y_c = 6.2 + (k - 8) * 1.8
        # Cap at X = 60.0, Resistor at X = 64.5
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(60.0, y_c))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)
        c_pad1[cell_id] = (60.825, y_c)
        c_pad2[cell_id] = (59.175, y_c)

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(64.5, y_c))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
        board.Add(fp_r)
        r_pad1[cell_id] = (63.675, y_c)
        r_pad2[cell_id] = (65.325, y_c)

        u_pt = (54.65, u1_right_y[k - 8])
        trk(pcbnew.In2_Cu, nets[f"RF_CH{k}"], u_pt, (58.0, u1_right_y[k - 8]))
        trk(pcbnew.In2_Cu, nets[f"RF_CH{k}"], (58.0, u1_right_y[k - 8]), (58.0, y_c))
        via(nets[f"RF_CH{k}"], (58.0, y_c))
        trk(pcbnew.F_Cu, nets[f"RF_CH{k}"], (58.0, y_c), c_pad1[cell_id])
        trk(pcbnew.F_Cu, nets[f"RF_CH{k}"], c_pad1[cell_id], r_pad1[cell_id])

        # GND via for C.2:
        via(nets["GND"], (c_pad2[cell_id][0] - 0.9, y_c))
        trk(pcbnew.F_Cu, nets["GND"], c_pad2[cell_id], (c_pad2[cell_id][0] - 0.9, y_c))

    # 15. Ground Vias for remaining SMD parts:
    # U1 GND (pin 12) at (45.35, 19.985)
    via(nets["GND"], (44.0, 19.985))
    trk(pcbnew.F_Cu, nets["GND"], (45.35, 19.985), (44.0, 19.985))

    # C17 pad 2 GND (50.825, 2.0), C18 pad 2 GND (55.95, 2.0)
    for gx, gy in [(50.825, 2.0), (55.95, 2.0)]:
        via(nets["GND"], (gx + 1.0, gy))
        trk(pcbnew.F_Cu, nets["GND"], (gx, gy), (gx + 1.0, gy))

    # R18..R21 pad 2 GND
    for idx in range(4):
        rx = 20.0 + idx * 3.5
        via(nets["GND"], (rx + 1.8, 13.0))
        trk(pcbnew.F_Cu, nets["GND"], (rx + 0.825, 13.0), (rx + 1.8, 13.0))

    # 16. +3.3V Connections (Continuous clean power bus on In2_Cu)
    # Route power track on In2_Cu at Y=1.2 mm: from J1 pin 1,2 across to J2 pin 3
    # J1 pin 1,2 at (12.0, 5.5 and 2.96). J2 pin 3 at (70.08, 5.5)
    trk(pcbnew.In2_Cu, nets["+3.3V"], (12.0, 2.96), (12.0, 1.2), 0.5)
    trk(pcbnew.In2_Cu, nets["+3.3V"], (12.0, 1.2), (70.08, 1.2), 0.5)
    trk(pcbnew.In2_Cu, nets["+3.3V"], (70.08, 1.2), (70.08, 5.5), 0.5)

    # Drop vias from In2_Cu power bus to SMD pads:
    # R17 pad 1 at (44.175, 2.0), C17 pad 1 at (49.175, 2.0), C18 pad 1 at (54.05, 2.0)
    for vx in [44.175, 49.175, 54.05]:
        via(nets["+3.3V"], (vx, 1.2))
        trk(pcbnew.F_Cu, nets["+3.3V"], (vx, 1.2), (vx, 2.0))

    # U1 VCC (pin 24) at (54.65, 6.015)
    via(nets["+3.3V"], (54.65, 4.5))
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 6.015), (54.65, 4.5))
    trk(pcbnew.In2_Cu, nets["+3.3V"], (54.65, 4.5), (54.65, 1.2))

    # 17. MUX Control Lines on In2_Cu & F_Cu:
    # S0: J1.3 (14.54, 5.5) -> R18.1 (19.175, 13.0) -> U1.10 (45.35, 17.445)
    trk(pcbnew.F_Cu, nets["MUX_S0"], (14.54, 5.5), (14.54, 9.0))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (14.54, 9.0), (19.175, 9.0))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (19.175, 9.0), (19.175, 13.0))
    via(nets["MUX_S0"], (19.175, 14.5))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (19.175, 13.0), (19.175, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S0"], (19.175, 14.5), (30.0, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S0"], (30.0, 14.5), (30.0, 17.445))
    trk(pcbnew.In2_Cu, nets["MUX_S0"], (30.0, 17.445), (45.35, 17.445))

    # S1: J1.5 (17.08, 5.5) -> R19.1 (22.675, 13.0) -> U1.11 (45.35, 18.715)
    trk(pcbnew.F_Cu, nets["MUX_S1"], (17.08, 5.5), (17.08, 9.5))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (17.08, 9.5), (22.675, 9.5))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (22.675, 9.5), (22.675, 13.0))
    via(nets["MUX_S1"], (22.675, 14.5))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (22.675, 13.0), (22.675, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S1"], (22.675, 14.5), (29.5, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S1"], (29.5, 14.5), (29.5, 18.715))
    trk(pcbnew.In2_Cu, nets["MUX_S1"], (29.5, 18.715), (45.35, 18.715))

    # S2: J1.7 (19.62, 5.5) -> R20.1 (26.175, 13.0) -> U1.14 (54.65, 18.715)
    trk(pcbnew.F_Cu, nets["MUX_S2"], (19.62, 5.5), (19.62, 10.0))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (19.62, 10.0), (26.175, 10.0))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (26.175, 10.0), (26.175, 13.0))
    via(nets["MUX_S2"], (26.175, 14.5))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (26.175, 13.0), (26.175, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S2"], (26.175, 14.5), (26.175, 21.0))
    trk(pcbnew.In2_Cu, nets["MUX_S2"], (26.175, 21.0), (53.0, 21.0))
    trk(pcbnew.In2_Cu, nets["MUX_S2"], (53.0, 21.0), (53.0, 18.715))
    trk(pcbnew.In2_Cu, nets["MUX_S2"], (53.0, 18.715), (54.65, 18.715))

    # S3: J1.9 (22.16, 5.5) -> R21.1 (29.675, 13.0) -> U1.13 (54.65, 19.985)
    trk(pcbnew.F_Cu, nets["MUX_S3"], (22.16, 5.5), (22.16, 10.5))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (22.16, 10.5), (29.675, 10.5))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (29.675, 10.5), (29.675, 13.0))
    via(nets["MUX_S3"], (29.675, 14.5))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (29.675, 13.0), (29.675, 14.5))
    trk(pcbnew.In2_Cu, nets["MUX_S3"], (29.675, 14.5), (29.675, 21.5))
    trk(pcbnew.In2_Cu, nets["MUX_S3"], (29.675, 21.5), (54.0, 21.5))
    trk(pcbnew.In2_Cu, nets["MUX_S3"], (54.0, 21.5), (54.0, 19.985))
    trk(pcbnew.In2_Cu, nets["MUX_S3"], (54.0, 19.985), (54.65, 19.985))

    # EN: J1.11 (24.70, 5.5) -> R17.2 (45.825, 2.0) -> U1.15 (54.65, 17.445)
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 5.5), (24.70, 2.0))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 2.0), (45.825, 2.0))
    via(nets["MUX_EN"], (45.825, 2.0))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (45.825, 2.0), (47.0, 2.0))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (47.0, 2.0), (47.0, 22.0))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (47.0, 22.0), (52.0, 22.0))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (52.0, 22.0), (52.0, 17.445))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (52.0, 17.445), (54.65, 17.445))

    # 18. Pass-Through Signals J1 -> J2 on In2_Cu (cleanly spaced between Y=2.5 and 4.0)
    pass_pins = [
        ("SPI_SCK",  (14.54, 2.96), (75.16, 5.5), 2.5),
        ("SPI_MISO", (17.08, 2.96), (77.70, 5.5), 2.8),
        ("SPI_MOSI", (19.62, 2.96), (80.24, 5.5), 3.1),
        ("SPI_CS",   (22.16, 2.96), (82.78, 5.5), 3.4),
        ("NFC_IRQ",  (24.70, 2.96), (85.32, 5.5), 3.7),
        ("NFC_RST",  (27.24, 2.96), (87.86, 5.5), 4.0),
    ]
    for s_name, p_j1, p_j2, y_route in pass_pins:
        trk(pcbnew.In2_Cu, nets[s_name], p_j1, (p_j1[0], y_route))
        trk(pcbnew.In2_Cu, nets[s_name], (p_j1[0], y_route), (p_j2[0], y_route))
        trk(pcbnew.In2_Cu, nets[s_name], (p_j2[0], y_route), p_j2)

    # 19. Connect R_k to Coil L_k:
    # 4 columns:
    # Col 0 coils: 1, 5, 9, 13.
    # Col 1 coils: 2, 6, 10, 14.
    # Col 2 coils: 3, 7, 11, 15.
    # Col 3 coils: 4, 8, 12, 16.
    # All vertical lanes on In2_Cu!
    # Left coils (Col 0, 1) have their lanes on In2_Cu at X=8..11 and X=29..32.
    # Right coils (Col 2, 3) have their lanes on In2_Cu at X=49..52 and X=89..92.
    # Horizontal feed from Rk to vertical lanes is on B.Cu!
    # Since horizontal feeds are on B.Cu and vertical lanes are on In2_Cu, they NEVER cross!
    for cell_id in range(1, 17):
        net_coil = nets[f"RF_COIL_{cell_id}"]
        # R pad 2
        rp2 = r_pad2[cell_id]
        via(net_coil, (rp2[0], rp2[1] + 0.6))
        trk(pcbnew.F_Cu, net_coil, rp2, (rp2[0], rp2[1] + 0.6))

        # Coil Pad 1
        lp1 = l_pad1[cell_id]
        via(net_coil, (lp1[0], lp1[1] - 0.7))
        trk(pcbnew.F_Cu, net_coil, (lp1[0], lp1[1] - 0.7), lp1)

    board.Save(TEST_PCB)
    print(f"Board saved to {TEST_PCB}")

if __name__ == '__main__':
    build_board()
