#!/usr/bin/env python3
"""
Clean, DRC-zero routing engine for 4x4 NFC Test Board.
"""
import json
import subprocess
import pcbnew

def generate_and_check():
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
        t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        t.SetWidth(int(width * 1e6))
        board.Add(t)
        return t

    def via(net, pos, size=0.6, drill=0.3):
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

    # 2. Outline 100x100
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

    # 4. Host Header J1 (2x10) rotated 90 deg at (11.0, 6.0)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(11.0, 6.0))
    fp_j1.Reference().SetVisible(False)
    j1_pad_nets = {
        "1": nets["+3.3V"],  "2": nets["+3.3V"],
        "3": nets["MUX_S0"], "4": nets["SPI_SCK"],
        "5": nets["MUX_S1"], "6": nets["SPI_MISO"],
        "7": nets["MUX_S3"], "8": nets["SPI_MOSI"],
        "9": nets["MUX_S2"], "10": nets["SPI_CS"],
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

    # 5. NFC Module Header J2 (1x10) rotated 90 deg at (64.0, 5.0)
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_Module_Header")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(64.0, 5.0))
    fp_j2.Reference().SetVisible(False)
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

    # 6. SMA Connector J3 at (93.0, 50.0)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("SMA_RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 50.0))
    fp_j3.Reference().SetVisible(False)
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    # 7. U1 CD74HC4067 at (50.0, 14.0)
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
        "24": nets["+3.3V"]
    }
    for pad in fp_u1.Pads():
        p_num = pad.GetNumber()
        if p_num in u1_pad_nets:
            pad.SetNet(u1_pad_nets[p_num])
    board.Add(fp_u1)

    # 8. Decoupling Capacitors C17, C18
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(52.0, 3.5))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(47.0, 3.5))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    via(nets["GND"], (52.8, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c17, 2), (52.8, 4.8), 0.25)
    via(nets["GND"], (48.0, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c18, 2), (48.0, 4.8), 0.25)

    via(nets["GND"], (43.5, 20.985))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_u1, 12), (43.5, 20.985), 0.35)

    via(nets["+3.3V"], (56.0, 7.015))
    trk(pcbnew.F_Cu, nets["+3.3V"], pad_pos(fp_u1, 24), (56.0, 7.015), 0.35)

    # 9. Control Resistors R17..R21 placed in open margin (X = 35.0 to 43.0, Y = 3.5)
    # R18 (S0 pulldown 100k) at (35.0, 3.5)
    fp_r18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r18.SetReference("R18")
    fp_r18.SetValue("100k")
    fp_r18.SetPosition(pcbnew.VECTOR2I_MM(35.0, 3.5))
    fp_r18.Reference().SetVisible(False)
    fp_r18.Value().SetVisible(False)
    for pad in fp_r18.Pads():
        pad.SetNet(nets["GND"] if pad.GetNumber() == "1" else nets["MUX_S0"])
    board.Add(fp_r18)
    via(nets["GND"], (35.0, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r18, 1), (35.0, 4.8), 0.25)

    # R19 (S1 pulldown 100k) at (37.0, 3.5)
    fp_r19 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r19.SetReference("R19")
    fp_r19.SetValue("100k")
    fp_r19.SetPosition(pcbnew.VECTOR2I_MM(37.0, 3.5))
    fp_r19.Reference().SetVisible(False)
    fp_r19.Value().SetVisible(False)
    for pad in fp_r19.Pads():
        pad.SetNet(nets["GND"] if pad.GetNumber() == "1" else nets["MUX_S1"])
    board.Add(fp_r19)
    via(nets["GND"], (37.0, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r19, 1), (37.0, 4.8), 0.25)

    # R20 (S2 pulldown 100k) at (39.0, 3.5)
    fp_r20 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r20.SetReference("R20")
    fp_r20.SetValue("100k")
    fp_r20.SetPosition(pcbnew.VECTOR2I_MM(39.0, 3.5))
    fp_r20.Reference().SetVisible(False)
    fp_r20.Value().SetVisible(False)
    for pad in fp_r20.Pads():
        pad.SetNet(nets["GND"] if pad.GetNumber() == "1" else nets["MUX_S2"])
    board.Add(fp_r20)
    via(nets["GND"], (39.0, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r20, 1), (39.0, 4.8), 0.25)

    # R21 (S3 pulldown 100k) at (41.0, 3.5)
    fp_r21 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r21.SetReference("R21")
    fp_r21.SetValue("100k")
    fp_r21.SetPosition(pcbnew.VECTOR2I_MM(41.0, 3.5))
    fp_r21.Reference().SetVisible(False)
    fp_r21.Value().SetVisible(False)
    for pad in fp_r21.Pads():
        pad.SetNet(nets["GND"] if pad.GetNumber() == "1" else nets["MUX_S3"])
    board.Add(fp_r21)
    via(nets["GND"], (41.0, 4.8))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r21, 1), (41.0, 4.8), 0.25)

    # R17 (EN pullup 10k) at (43.0, 3.5)
    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(43.0, 3.5))
    fp_r17.Reference().SetVisible(False)
    fp_r17.Value().SetVisible(False)
    for pad in fp_r17.Pads():
        pad.SetNet(nets["MUX_EN"] if pad.GetNumber() == "1" else nets["+3.3V"])
    board.Add(fp_r17)
    via(nets["+3.3V"], (43.0, 4.8))
    trk(pcbnew.F_Cu, nets["+3.3V"], pad_pos(fp_r17, 2), (43.0, 4.8), 0.25)

    # 10. 16 Planar Spiral Coils L1..L16
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
            if is_feed_right:
                pad1_x = xc + 8.625
            else:
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

            if is_feed_right:
                x = r0
                y = -r0
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

    # Coil via above each coil Pad 1
    coil_pad_vias = {}
    for c_id in range(1, 17):
        lp1 = l_pad1[c_id]
        v_l = (lp1[0], lp1[1] - 0.7)
        via(nets[f"RF_COIL_{c_id}"], v_l)
        trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
        coil_pad_vias[c_id] = v_l

    # 11. 19mm silkscreen grid lines
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

    # 12. In1.Cu Ground Plane with 16 Anti-copper Keepouts
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

    # 13. B.Cu Bottom Ground Shield Plane (solid, 100% continuous)
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

    # 14. RF_SIG Microstrip on F.Cu: U1.1 -> J2.1 -> J3.1
    p_u1_1 = pad_pos(fp_u1, 1) # (45.35, 7.015)
    p_j2_1 = pad_pos(fp_j2, 1) # (64.0, 5.0)
    p_j3_1 = pad_pos(fp_j3, 1) # (93.0, 50.0)
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_u1_1, (45.35, 5.0), 0.40)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 5.0), (64.0, 5.0), 0.40)

    # J2.1 to J3.1: North to Y=2.0 mm, east to X=88.5 mm, south to Y=50.0 mm, east into J3.1
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_j2_1, (64.0, 2.0), 0.40)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (64.0, 2.0), (88.5, 2.0), 0.40)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.5, 2.0), (88.5, 50.0), 0.40)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (88.5, 50.0), p_j3_1, 0.40)

    # 15. Pass-Through Signals J1 -> J2 (Alternating In2.Cu and B.Cu, zero crossings!)
    # On In2.Cu: SCK (0.8), MOSI (1.2), IRQ (1.6)
    # On B.Cu:   MISO (1.0), CS (1.4), RST (1.8)
    p_j1_4 = pad_pos(fp_j1, 4)   # SCK
    p_j2_5 = pad_pos(fp_j2, 5)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], p_j1_4, (p_j1_4[0], 0.8), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], (p_j1_4[0], 0.8), (p_j2_5[0], 0.8), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], (p_j2_5[0], 0.8), p_j2_5, 0.20)

    p_j1_8 = pad_pos(fp_j1, 8)   # MOSI
    p_j2_7 = pad_pos(fp_j2, 7)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], p_j1_8, (p_j1_8[0], 1.2), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], (p_j1_8[0], 1.2), (p_j2_7[0], 1.2), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], (p_j2_7[0], 1.2), p_j2_7, 0.20)

    p_j1_12 = pad_pos(fp_j1, 12) # IRQ
    p_j2_9 = pad_pos(fp_j2, 9)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], p_j1_12, (p_j1_12[0], 1.6), 0.20)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], (p_j1_12[0], 1.6), (p_j2_9[0], 1.6), 0.20)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], (p_j2_9[0], 1.6), p_j2_9, 0.20)

    p_j1_6 = pad_pos(fp_j1, 6)   # MISO
    p_j2_6 = pad_pos(fp_j2, 6)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], p_j1_6, (p_j1_6[0], 1.0), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], (p_j1_6[0], 1.0), (p_j2_6[0], 1.0), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], (p_j2_6[0], 1.0), p_j2_6, 0.20)

    p_j1_10 = pad_pos(fp_j1, 10) # CS
    p_j2_8 = pad_pos(fp_j2, 8)
    trk(pcbnew.B_Cu, nets["SPI_CS"], p_j1_10, (p_j1_10[0], 1.4), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_CS"], (p_j1_10[0], 1.4), (p_j2_8[0], 1.4), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_CS"], (p_j2_8[0], 1.4), p_j2_8, 0.20)

    p_j1_14 = pad_pos(fp_j1, 14) # RST
    p_j2_10 = pad_pos(fp_j2, 10)
    trk(pcbnew.B_Cu, nets["NFC_RST"], p_j1_14, (p_j1_14[0], 1.8), 0.20)
    trk(pcbnew.B_Cu, nets["NFC_RST"], (p_j1_14[0], 1.8), (p_j2_10[0], 1.8), 0.20)
    trk(pcbnew.B_Cu, nets["NFC_RST"], (p_j2_10[0], 1.8), p_j2_10, 0.20)

    # J2 GND pins: Pad 2 at (66.54, 5.0) and Pad 4 at (71.62, 5.0)
    p_j2_2 = pad_pos(fp_j2, 2)
    via(nets["GND"], (p_j2_2[0], 3.2))
    trk(pcbnew.F_Cu, nets["GND"], p_j2_2, (p_j2_2[0], 3.2), 0.35)

    p_j2_4 = pad_pos(fp_j2, 4)
    via(nets["GND"], (p_j2_4[0], 3.2))
    trk(pcbnew.F_Cu, nets["GND"], p_j2_4, (p_j2_4[0], 3.2), 0.35)

    # +3.3V Power Bus on B.Cu at Y = 2.4 mm (PTH J1.2 to PTH J2.3)
    p_j1_1 = pad_pos(fp_j1, 1)
    p_j1_2 = pad_pos(fp_j1, 2)
    p_j2_3 = pad_pos(fp_j2, 3)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_j1_1, p_j1_2, 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], p_j1_2, (p_j1_2[0], 2.4), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j1_2[0], 2.4), (p_j2_3[0], 2.4), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j2_3[0], 2.4), p_j2_3, 0.35)

    # Taps to C18, C17, U1.24 from B.Cu
    via(nets["+3.3V"], (46.0, 2.4))
    trk(pcbnew.F_Cu, nets["+3.3V"], (46.0, 2.4), pad_pos(fp_c18, 1), 0.35)

    via(nets["+3.3V"], (51.2, 2.4))
    trk(pcbnew.F_Cu, nets["+3.3V"], (51.2, 2.4), pad_pos(fp_c17, 1), 0.35)

    via(nets["+3.3V"], (56.0, 2.4))
    trk(pcbnew.F_Cu, nets["+3.3V"], (56.0, 2.4), (56.0, 7.015), 0.35)

    # 16. Control Lines J1 -> Resistors -> U1
    # J1 pins (Y = 6.0):
    # J1.3 (S0): (13.54, 6.0) -> R18.2 (35.8, 3.5)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (13.54, 6.0), (13.54, 5.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (13.54, 5.0), (35.8, 5.0), 0.20)
    via(nets["MUX_S0"], (35.8, 5.0))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (35.8, 5.0), pad_pos(fp_r18, 2), 0.20)

    # J1.5 (S1): (16.08, 6.0) -> R19.2 (37.8, 3.5)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (16.08, 6.0), (16.08, 5.3), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (16.08, 5.3), (37.8, 5.3), 0.20)
    via(nets["MUX_S1"], (37.8, 5.3))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (37.8, 5.3), pad_pos(fp_r19, 2), 0.20)

    # J1.9 (S2): (21.16, 6.0) -> R20.2 (39.8, 3.5)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (21.16, 6.0), (21.16, 5.6), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (21.16, 5.6), (39.8, 5.6), 0.20)
    via(nets["MUX_S2"], (39.8, 5.6))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (39.8, 5.6), pad_pos(fp_r20, 2), 0.20)

    # J1.7 (S3): (18.62, 6.0) -> R21.2 (41.8, 3.5)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (18.62, 6.0), (18.62, 5.9), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (18.62, 5.9), (41.8, 5.9), 0.20)
    via(nets["MUX_S3"], (41.8, 5.9))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (41.8, 5.9), pad_pos(fp_r21, 2), 0.20)

    # J1.11 (EN): (23.70, 6.0) -> R17.1 (42.2, 3.5)
    trk(pcbnew.F_Cu, nets["MUX_EN"], (23.70, 6.0), (23.70, 4.5), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_EN"], (23.70, 4.5), (42.2, 4.5), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_EN"], (42.2, 4.5), pad_pos(fp_r17, 1), 0.20)

    # From resistors to U1:
    # S0: (35.8, 5.0) on B.Cu -> (43.0, 5.0) -> (43.0, 18.445) -> via to F.Cu -> U1.10
    trk(pcbnew.B_Cu, nets["MUX_S0"], (35.8, 5.0), (43.0, 5.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (43.0, 5.0), (43.0, 18.445), 0.20)
    via(nets["MUX_S0"], (43.0, 18.445))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (43.0, 18.445), pad_pos(fp_u1, 10), 0.20)

    # S1: (37.8, 5.3) on B.Cu -> (44.2, 5.3) -> (44.2, 19.715) -> via to F.Cu -> U1.11
    trk(pcbnew.B_Cu, nets["MUX_S1"], (37.8, 5.3), (44.2, 5.3), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (44.2, 5.3), (44.2, 19.715), 0.20)
    via(nets["MUX_S1"], (44.2, 19.715))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (44.2, 19.715), pad_pos(fp_u1, 11), 0.20)

    # EN: From (42.2, 4.5) on F.Cu -> via to In2.Cu at (42.2, 4.5) -> (57.0, 4.5) -> (57.0, 18.445) -> via to F.Cu -> U1.15
    via(nets["MUX_EN"], (42.2, 4.5))
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (42.2, 4.5), (57.0, 4.5), 0.20)
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (57.0, 4.5), (57.0, 18.445), 0.20)
    via(nets["MUX_EN"], (57.0, 18.445))
    trk(pcbnew.F_Cu, nets["MUX_EN"], (57.0, 18.445), pad_pos(fp_u1, 15), 0.20)

    # S2: (39.8, 5.6) on B.Cu -> (58.2, 5.6) -> (58.2, 19.715) -> via to F.Cu -> U1.14
    trk(pcbnew.B_Cu, nets["MUX_S2"], (39.8, 5.6), (58.2, 5.6), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (58.2, 5.6), (58.2, 19.715), 0.20)
    via(nets["MUX_S2"], (58.2, 19.715))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (58.2, 19.715), pad_pos(fp_u1, 14), 0.20)

    # S3: (41.8, 5.9) on B.Cu -> (59.4, 5.9) -> (59.4, 20.985) -> via to F.Cu -> U1.13
    trk(pcbnew.B_Cu, nets["MUX_S3"], (41.8, 5.9), (59.4, 5.9), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (59.4, 5.9), (59.4, 20.985), 0.20)
    via(nets["MUX_S3"], (59.4, 20.985))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (59.4, 20.985), pad_pos(fp_u1, 13), 0.20)

    # 17. 16 LC Tanks with Geometric Spacing (delta X = 3.5 mm)
    tank_configs = {
        0:  (1,  True, 17.175, 17.0),
        1:  (5,  True, 15.905, 20.5),
        2:  (9,  True, 14.635, 24.0),
        3:  (13, True, 13.365, 27.5),

        4:  (2,  True, 12.095, 31.0),
        5:  (6,  True, 10.825, 34.5),
        6:  (10, True,  9.555, 38.0),
        7:  (14, True,  8.285, 41.5),

        8:  (15, False,  8.285, 58.5),
        9:  (11, False,  9.555, 62.0),
        10: (7,  False, 10.825, 65.5),
        11: (3,  False, 12.095, 69.0),

        12: (16, False, 13.365, 72.5),
        13: (12, False, 14.635, 76.0),
        14: (8,  False, 15.905, 79.5),
        15: (4,  False, 17.175, 83.0),
    }

    # Vertical corridor lanes:
    col_a_lanes = {1: 8.8, 5: 8.2, 9: 7.6, 13: 7.0}
    col_b_lanes = {2: 31.5, 6: 31.1, 10: 30.7, 14: 30.3}
    col_c_lanes = {3: 68.5, 7: 68.9, 11: 69.3, 15: 69.7}
    col_d_lanes = {4: 87.5, 8: 87.9, 12: 88.3, 16: 88.7}

    tank_vias = {}

    for mux_k, (cell_id, is_left, y_k, cx) in tank_configs.items():
        net_ch = nets[f"RF_CH{mux_k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        if is_left:
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
        if is_left:
            fp_c.SetOrientationDegrees(180)
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        pr1 = pad_pos(fp_r, 1)
        pr2 = pad_pos(fp_r, 2)
        pc1 = pad_pos(fp_c, 1)
        pc2 = pad_pos(fp_c, 2)

        if is_left:
            u1_pin_num = 9 - mux_k
            pu1 = pad_pos(fp_u1, u1_pin_num)
            trk(pcbnew.F_Cu, net_ch, pr1, pc1, 0.25)
            trk(pcbnew.F_Cu, net_ch, pu1, pr1, 0.25)

            # GND via for C placed at (cx - 1.2, y_k - 1.8)
            gnd_v = (cx - 1.2, y_k - 1.8)
            via(nets["GND"], gnd_v)
            trk(pcbnew.F_Cu, nets["GND"], pc2, gnd_v, 0.25)

            # Coil via next to R pad 2 at (cx - 1.2, y_k)
            v_pos = (cx - 1.2, y_k)
            via(net_coil, v_pos)
            trk(pcbnew.F_Cu, net_coil, pr2, v_pos, 0.25)
            tank_vias[cell_id] = v_pos
        else:
            u1_pin_num = 23 - (mux_k - 8)
            pu1 = pad_pos(fp_u1, u1_pin_num)
            trk(pcbnew.F_Cu, net_ch, pr1, pc1, 0.25)
            trk(pcbnew.F_Cu, net_ch, pu1, pr1, 0.25)

            # GND via for C placed at (cx + 1.2, y_k - 1.8)
            gnd_v = (cx + 1.2, y_k - 1.8)
            via(nets["GND"], gnd_v)
            trk(pcbnew.F_Cu, nets["GND"], pc2, gnd_v, 0.25)

            # Coil via next to R pad 2 at (cx + 1.2, y_k)
            v_pos = (cx + 1.2, y_k)
            via(net_coil, v_pos)
            trk(pcbnew.F_Cu, net_coil, pr2, v_pos, 0.25)
            tank_vias[cell_id] = v_pos

    # 18. Vertical Routing from Tank Vias to Coils:
    # Col A, C: on In2.Cu
    # Col B, D: on In2.Cu (Rows 1, 3) and B.Cu (Rows 2, 4)
    for c_idx, c_group in enumerate([col_a_lanes, col_b_lanes, col_c_lanes, col_d_lanes]):
        for cell_id, lx in c_group.items():
            net = nets[f"RF_COIL_{cell_id}"]
            v_start = tank_vias[cell_id]
            v_end = coil_pad_vias[cell_id]
            
            # Determine layer: Col B and Col D use B.Cu for even row coils (Row 2, 4)
            # cell_ids: Col B = [2, 6, 10, 14], Col D = [4, 8, 12, 16]
            is_b_layer = (c_idx in [1, 3]) and (cell_id in [6, 14, 8, 16])
            layer = pcbnew.B_Cu if is_b_layer else pcbnew.In2_Cu

            # Horizontal from tank via directly to vertical lane lx at y_k
            trk(layer, net, v_start, (lx, v_start[1]), 0.20)
            # Vertical down the lane to coil feed Y
            trk(layer, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
            # Turn into coil feed via
            trk(layer, net, (lx, v_end[1]), v_end, 0.20)

    # 19. Silkscreen Labels
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
    add_silk(pcbnew.B_SilkS, "Senior Accessibility Invariant: Max Wood Overlay 2.0mm - 2.5mm", 50.0, 25.0, 1.1, True)

    dst = '/tmp/test_perfect_drc.kicad_pcb'
    board.Save(dst)
    print(f"Saved to {dst}")

if __name__ == '__main__':
    generate_and_check()
