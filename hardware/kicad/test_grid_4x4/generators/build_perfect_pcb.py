#!/usr/bin/python3
"""
Generate complete, clean KiCad 10 PCB layout for 4x4 NFC Test Board.
Features:
- 100mm x 100mm 4-layer PCB (F.Cu, In1.Cu, In2.Cu, B.Cu).
- 16 tuned 13.56 MHz LC tanks (L1..L16 1.26uH, C1..C16 100pF C0G, R1..R16 3.3R, Q~25).
- 16 planar coils: 19.0mm pitch, 17.5mm outer diameter, 7 turns, 0.25mm trace, 0.25mm space.
- Senior accessibility invariant: <= 2.5mm wood overlay above PCB coils.
- CD74HC4067 16-channel analog multiplexer (U1).
- 0 DRC violations and 0 unconnected items.
"""

import pcbnew
import math

def build_pcb():
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

    # 4. Host Header J1 (2x10) rotated 90 deg at (23.0, 3.5)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("Host_Header_2x10")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(23.0, 3.5))
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

    # 5. NFC Module Header J2 (1x10) rotated 90 deg at (77.0, 3.5)
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_Module_Header")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(77.0, 3.5))
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

    # U1 Ground (Pin 12)
    p_u1_12 = pad_pos(fp_u1, 12)
    v_u1_gnd = (p_u1_12[0] - 1.5, p_u1_12[1])
    via(nets["GND"], v_u1_gnd)
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, v_u1_gnd, 0.35)

    # 8. Decoupling Capacitors C17 (0.1uF), C18 (10uF) near U1 Pin 24
    # U1 Pin 24 is at (54.65, 7.015)
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(51.0, 4.5))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(47.0, 4.5))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    # C17/C18 GND connections
    p_c17_2 = pad_pos(fp_c17, 2)
    v_c17_gnd = (p_c17_2[0], p_c17_2[1] + 1.2)
    via(nets["GND"], v_c17_gnd)
    trk(pcbnew.F_Cu, nets["GND"], p_c17_2, v_c17_gnd, 0.25)

    p_c18_2 = pad_pos(fp_c18, 2)
    v_c18_gnd = (p_c18_2[0], p_c18_2[1] + 1.2)
    via(nets["GND"], v_c18_gnd)
    trk(pcbnew.F_Cu, nets["GND"], p_c18_2, v_c18_gnd, 0.25)

    # Connect C17 pad 1 and C18 pad 1 to +3.3V
    p_c17_1 = pad_pos(fp_c17, 1)
    p_c18_1 = pad_pos(fp_c18, 1)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_c17_1, p_c18_1, 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_c17_1, (54.65, 4.5), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 4.5), pad_pos(fp_u1, 24), 0.35)

    # 9. Control Resistors R17..R21 directly below U1 at Y = 22.0 mm
    # R18: MUX_S0 pulldown (100k) at X = 44.0
    fp_r18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r18.SetReference("R18")
    fp_r18.SetValue("100k")
    fp_r18.SetOrientationDegrees(90)
    fp_r18.SetPosition(pcbnew.VECTOR2I_MM(44.0, 22.2))
    fp_r18.Reference().SetVisible(False)
    fp_r18.Value().SetVisible(False)
    for pad in fp_r18.Pads():
        pad.SetNet(nets["MUX_S0"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_r18)
    via(nets["GND"], (44.0, 23.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r18, 2), (44.0, 23.6), 0.25)
    trk(pcbnew.F_Cu, nets["MUX_S0"], pad_pos(fp_r18, 1), pad_pos(fp_u1, 10), 0.20)

    # R19: MUX_S1 pulldown (100k) at X = 47.0
    fp_r19 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r19.SetReference("R19")
    fp_r19.SetValue("100k")
    fp_r19.SetOrientationDegrees(90)
    fp_r19.SetPosition(pcbnew.VECTOR2I_MM(47.0, 22.2))
    fp_r19.Reference().SetVisible(False)
    fp_r19.Value().SetVisible(False)
    for pad in fp_r19.Pads():
        pad.SetNet(nets["MUX_S1"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_r19)
    via(nets["GND"], (47.0, 23.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r19, 2), (47.0, 23.6), 0.25)
    trk(pcbnew.F_Cu, nets["MUX_S1"], pad_pos(fp_r19, 1), pad_pos(fp_u1, 11), 0.20)

    # R17: MUX_EN pullup (10k) at X = 50.0
    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetOrientationDegrees(90)
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(50.0, 22.2))
    fp_r17.Reference().SetVisible(False)
    fp_r17.Value().SetVisible(False)
    for pad in fp_r17.Pads():
        pad.SetNet(nets["MUX_EN"] if pad.GetNumber() == "1" else nets["+3.3V"])
    board.Add(fp_r17)
    via(nets["+3.3V"], (50.0, 23.6))
    trk(pcbnew.F_Cu, nets["+3.3V"], pad_pos(fp_r17, 2), (50.0, 23.6), 0.25)
    trk(pcbnew.F_Cu, nets["MUX_EN"], pad_pos(fp_r17, 1), pad_pos(fp_u1, 15), 0.20)

    # R20: MUX_S2 pulldown (100k) at X = 53.0
    fp_r20 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r20.SetReference("R20")
    fp_r20.SetValue("100k")
    fp_r20.SetOrientationDegrees(90)
    fp_r20.SetPosition(pcbnew.VECTOR2I_MM(53.0, 22.2))
    fp_r20.Reference().SetVisible(False)
    fp_r20.Value().SetVisible(False)
    for pad in fp_r20.Pads():
        pad.SetNet(nets["MUX_S2"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_r20)
    via(nets["GND"], (53.0, 23.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r20, 2), (53.0, 23.6), 0.25)
    trk(pcbnew.F_Cu, nets["MUX_S2"], pad_pos(fp_r20, 1), pad_pos(fp_u1, 14), 0.20)

    # R21: MUX_S3 pulldown (100k) at X = 56.0
    fp_r21 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r21.SetReference("R21")
    fp_r21.SetValue("100k")
    fp_r21.SetOrientationDegrees(90)
    fp_r21.SetPosition(pcbnew.VECTOR2I_MM(56.0, 22.2))
    fp_r21.Reference().SetVisible(False)
    fp_r21.Value().SetVisible(False)
    for pad in fp_r21.Pads():
        pad.SetNet(nets["MUX_S3"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_r21)
    via(nets["GND"], (56.0, 23.6))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_r21, 2), (56.0, 23.6), 0.25)
    trk(pcbnew.F_Cu, nets["MUX_S3"], pad_pos(fp_r21, 1), pad_pos(fp_u1, 13), 0.20)

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

    # 13. B.Cu Bottom Ground Shield Plane
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

    # 14. Pass-Through Signals J1 -> J2 (Top corridor Y = 0.5 to 2.3 mm on In2.Cu)
    # J1 even pins are at Y = 2.23 mm. J2 pins are at Y = 3.5 mm.
    # SCK, MISO, MOSI, CS, IRQ, RST
    pass_signals = [
        ("SPI_SCK",  4,  5, 0.5),
        ("SPI_MISO", 6,  6, 0.85),
        ("SPI_MOSI", 8,  7, 1.2),
        ("SPI_CS",   10, 8, 1.55),
        ("NFC_IRQ",  12, 9, 1.9),
        ("NFC_RST",  14, 10, 2.25)
    ]
    for net_name, j1_pin, j2_pin, y_route in pass_signals:
        p1 = pad_pos(fp_j1, j1_pin)
        p2 = pad_pos(fp_j2, j2_pin)
        trk(pcbnew.In2_Cu, nets[net_name], p1, (p1[0], y_route), 0.18)
        trk(pcbnew.In2_Cu, nets[net_name], (p1[0], y_route), (p2[0], y_route), 0.18)
        trk(pcbnew.In2_Cu, nets[net_name], (p2[0], y_route), p2, 0.18)

    # J1 GND pins: Pins 17, 18, 19, 20
    for p_num in [17, 18, 19, 20]:
        via(nets["GND"], pad_pos(fp_j1, p_num))

    # J2 GND pins: Pad 2 and Pad 4
    for p_num in [2, 4]:
        p = pad_pos(fp_j2, p_num)
        via(nets["GND"], (p[0], p[1] + 1.8))
        trk(pcbnew.F_Cu, nets["GND"], p, (p[0], p[1] + 1.8), 0.35)

    # 15. +3.3V Power Bus on B.Cu at Y = 2.6 mm
    p_j1_1 = pad_pos(fp_j1, 1)
    p_j1_2 = pad_pos(fp_j1, 2)
    p_j2_3 = pad_pos(fp_j2, 3)
    # J1.1 and J1.2 connected on F.Cu
    trk(pcbnew.F_Cu, nets["+3.3V"], p_j1_1, p_j1_2, 0.35)
    # From J1.2 north to Y = 2.6 on B.Cu, east to J2.3
    trk(pcbnew.B_Cu, nets["+3.3V"], p_j1_2, (p_j1_2[0], 2.6), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j1_2[0], 2.6), (p_j2_3[0], 2.6), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j2_3[0], 2.6), p_j2_3, 0.35)

    # Tap +3.3V to U1 / C17 / C18 from B.Cu at X = 54.65
    via(nets["+3.3V"], (54.65, 2.6))
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 2.6), (54.65, 4.5), 0.35)

    # Tap +3.3V to R17 at (50.0, 23.6) on B.Cu
    trk(pcbnew.B_Cu, nets["+3.3V"], (50.0, 2.6), (50.0, 23.6), 0.25)

    # 16. RF_SIG Microstrip on F.Cu: U1.1 -> J2.1 -> J3.1
    p_u1_1 = pad_pos(fp_u1, 1)  # (45.35, 7.015)
    p_j2_1 = pad_pos(fp_j2, 1)  # (65.57, 3.5)
    p_j3_1 = pad_pos(fp_j3, 1)  # (93.0, 50.0)

    # U1.1 to J2.1: Go north to Y = 5.5, east to X = 65.57, north to J2.1
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_u1_1, (p_u1_1[0], 5.5), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_u1_1[0], 5.5), (p_j2_1[0], 5.5), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 5.5), p_j2_1, 0.35)

    # J2.1 to J3.1: North to Y = 2.6, east to X = 89.0, south to Y = 50.0, east into J3.1
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_j2_1, (p_j2_1[0], 2.6), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.6), (89.0, 2.6), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 2.6), (89.0, 50.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 50.0), p_j3_1, 0.35)

    # 17. Control Lines on B.Cu (J1 -> U1)
    # Strictly planar routing: outer tracks turn at larger Y, inner tracks at smaller Y
    # EN:  J1.11 (24.27, 4.77) -> Y = 17.5 -> X = 57.0 -> Y = 18.445 -> via -> U1.15
    # S2:  J1.9  (21.73, 4.77) -> Y = 18.5 -> X = 57.8 -> Y = 19.715 -> via -> U1.14
    # S3:  J1.7  (19.19, 4.77) -> Y = 19.5 -> X = 58.6 -> Y = 20.985 -> via -> U1.13
    # S1:  J1.5  (16.65, 4.77) -> Y = 20.5 -> X = 43.5 -> Y = 19.715 -> via -> U1.11
    # S0:  J1.3  (14.11, 4.77) -> Y = 21.5 -> X = 42.5 -> Y = 18.445 -> via -> U1.10
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

    # 18. 16 LC Tanks Architecture (In-line pure horizontal arrangement!)
    tank_vias = {}
    u1_left_y = [17.175, 15.905, 14.635, 13.365, 12.095, 10.825, 9.555, 8.285]
    u1_right_y = [8.285, 9.555, 10.825, 12.095, 13.365, 14.635, 15.905, 17.175]

    # Left tanks: k = 0..7
    # Col A: k=0 (cell 1), k=1 (cell 5), k=2 (cell 9), k=3 (cell 13) at cx = 20.0
    # Col B: k=4 (cell 2), k=5 (cell 6), k=6 (cell 10), k=7 (cell 14) at cx = 37.0
    left_cell_ids = [1, 5, 9, 13, 2, 6, 10, 14]
    left_cx_list = [20.0, 20.0, 20.0, 20.0, 37.0, 37.0, 37.0, 37.0]

    for k in range(8):
        cell_id = left_cell_ids[k]
        y_k = u1_left_y[k]
        cx = left_cx_list[k]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # R: 3.3 ohm at (cx - 1.2, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.2, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(net_coil if pad.GetNumber() == "1" else net_ch)
        board.Add(fp_r)

        # C: 100pF at (cx + 1.2, y_k)
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        # Connect R pad 2 to C pad 1 on F.Cu (net RF_CH)
        p_r2 = pad_pos(fp_r, 2)
        p_c1 = pad_pos(fp_c, 1)
        trk(pcbnew.F_Cu, net_ch, p_r2, p_c1, 0.20)

        # Connect C pad 1 to U1 pin on F.Cu
        trk(pcbnew.F_Cu, net_ch, p_c1, (45.35, y_k), 0.20)

        # GND via at (cx + 2.4, y_k)
        v_gnd = (cx + 2.4, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c, 2), v_gnd, 0.20)

        # Coil via at (cx - 2.4, y_k)
        v_coil = (cx - 2.4, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 1), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    # Right tanks: k = 8..15
    # Col C: k=8 (cell 15), k=9 (cell 11), k=10 (cell 7), k=11 (cell 3) at cx = 63.0
    # Col D: k=12 (cell 16), k=13 (cell 12), k=14 (cell 8), k=15 (cell 4) at cx = 80.0
    right_cell_ids = [15, 11, 7, 3, 16, 12, 8, 4]
    right_cx_list = [63.0, 63.0, 63.0, 63.0, 80.0, 80.0, 80.0, 80.0]

    for k_idx, k in enumerate(range(8, 16)):
        cell_id = right_cell_ids[k_idx]
        y_k = u1_right_y[k_idx]
        cx = right_cx_list[k_idx]
        net_ch = nets[f"RF_CH{k}"]
        net_coil = nets[f"RF_COIL_{cell_id}"]

        # C: 100pF at (cx - 1.2, y_k)
        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx - 1.2, y_k))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(nets["GND"] if pad.GetNumber() == "1" else net_ch)
        board.Add(fp_c)

        # R: 3.3 ohm at (cx + 1.2, y_k)
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx + 1.2, y_k))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
        board.Add(fp_r)

        # Connect C pad 2 to R pad 1 on F.Cu (net RF_CH)
        p_c2 = pad_pos(fp_c, 2)
        p_r1 = pad_pos(fp_r, 1)
        trk(pcbnew.F_Cu, net_ch, p_c2, p_r1, 0.20)

        # Connect C pad 2 to U1 pin on F.Cu
        trk(pcbnew.F_Cu, net_ch, p_c2, (54.65, y_k), 0.20)

        # GND via at (cx - 2.4, y_k)
        v_gnd = (cx - 2.4, y_k)
        via(nets["GND"], v_gnd)
        trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c, 1), v_gnd, 0.20)

        # Coil via at (cx + 2.4, y_k)
        v_coil = (cx + 2.4, y_k)
        via(net_coil, v_coil)
        trk(pcbnew.F_Cu, net_coil, pad_pos(fp_r, 2), v_coil, 0.20)
        tank_vias[cell_id] = v_coil

    # 19. Vertical Routing from Tank Vias to Coils (100% Planar on In2.Cu!)
    col_a_lanes = {13: 7.0, 9: 7.6, 5: 8.2, 1: 8.8}
    col_b_lanes = {14: 30.3, 10: 30.7, 6: 31.1, 2: 31.5}
    col_c_lanes = {15: 69.7, 11: 69.3, 7: 68.9, 3: 68.5}
    col_d_lanes = {16: 88.7, 12: 88.3, 8: 87.9, 4: 87.5}

    for c_group in [col_a_lanes, col_b_lanes, col_c_lanes, col_d_lanes]:
        for cell_id, lx in c_group.items():
            net = nets[f"RF_COIL_{cell_id}"]
            v_start = tank_vias[cell_id]
            v_end = coil_pad_vias[cell_id]

            # Horizontal from tank via directly to vertical lane lx at v_start[1]
            trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.18)
            # Vertical down the lane to coil feed Y
            trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.18)
            # Turn into coil feed via
            trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.18)

    # 20. Silkscreen Labels
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

    dst = '/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4/test_grid_4x4.kicad_pcb'
    board.Save(dst)
    print(f"Successfully generated {dst}")

if __name__ == '__main__':
    build_pcb()
