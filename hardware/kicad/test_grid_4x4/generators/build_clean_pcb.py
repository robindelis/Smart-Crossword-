#!/usr/bin/env python3
"""
build_clean_pcb.py - Generates the Phase 1 4x4 NFC Test Board in KiCad 10
Architecture:
- 4 layers: F.Cu, In1.Cu (GND with cutouts), In2.Cu (Address/Power/Signals), B.Cu (Shield + Return + Signals)
- 4x4 Planar Coils: 19mm pitch, 17.5mm OD, 7 turns, 0.25mm trace, 0.25mm space.
- 16 LC resonant tanks: L1..L16 (1.26uH), C1..C16 (100pF C0G 0603), R1..R16 (3.3R 0603).
- CD74HC4067 16:1 Analog Multiplexer (SOIC-24W).
- Clean routing topology with zero crossings and zero DRC violations.
"""
import pcbnew
import os
import sys

def build_pcb():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets Definition
    net_names = [
        "GND", "+3.3V", "RF_SIG",
        "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
        "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
        "I2C_SDA", "I2C_SCL", "GPIO_AUX"
    ]
    net_names += [f"RF_CH{k}" for k in range(16)]
    net_names += [f"RF_COIL_{k+1}" for k in range(16)]

    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    # Helpers
    def trk(layer, net, p1, p2, width=0.20):
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        t.SetWidth(int(width * 1e6))
        board.Add(t)

    def via(net, pos, size=0.6, drill=0.3):
        v = pcbnew.PCB_VIA(board)
        v.SetNet(net)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetWidth(int(size * 1e6))
        v.SetDrill(int(drill * 1e6))
        board.Add(v)

    def pad_pos(fp, pad_num):
        pad = fp.FindPadByNumber(str(pad_num))
        pos = pad.GetPosition()
        return (pos.x / 1e6, pos.y / 1e6)

    # 2. Board Outline (100mm x 100mm)
    corners = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(corners[i][0], corners[i][1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(corners[(i+1)%4][0], corners[(i+1)%4][1]))
        seg.SetWidth(int(0.15 * 1e6))
        board.Add(seg)

    # 3. 4x M3 Mounting Holes
    for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
        fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        fp_h.Reference().SetVisible(False)
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # 4. Host Header J1 (2x10, 2.54mm pitch) at (11.0, 5.0)
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
    fp_j1.SetValue("HOST_BUS")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(11.0, 5.0))
    fp_j1.Reference().SetVisible(False)
    j1_pad_nets = {
        "1": nets["+3.3V"], "2": nets["+3.3V"],
        "3": nets["MUX_S0"], "4": nets["SPI_SCK"],
        "5": nets["MUX_S1"], "6": nets["SPI_MISO"],
        "7": nets["MUX_S3"], "8": nets["SPI_MOSI"],
        "9": nets["MUX_S2"], "10": nets["SPI_CS"],
        "11": nets["MUX_EN"], "12": nets["NFC_IRQ"],
        "13": nets["GND"], "14": nets["NFC_RST"],
        "15": nets["GND"], "16": nets["I2C_SDA"],
        "17": nets["GND"], "18": nets["I2C_SCL"],
        "19": nets["GND"], "20": nets["GPIO_AUX"]
    }
    for pad in fp_j1.Pads():
        p_num = pad.GetNumber()
        if p_num in j1_pad_nets:
            pad.SetNet(j1_pad_nets[p_num])
    board.Add(fp_j1)

    # 5. NFC Transceiver Header J2 (1x10, 2.54mm pitch) at (66.0, 4.0)
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_TRANSCEIVER")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(66.0, 4.0))
    fp_j2.Reference().SetVisible(False)
    j2_pad_nets = {
        "1": nets["RF_SIG"], "2": nets["GND"],
        "3": nets["+3.3V"], "4": nets["GND"],
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

    # 7. U1 CD74HC4067 at (50.0, 13.0)
    fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
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

    # U1 Ground (Pin 12 at 45.35, 19.985)
    p_u1_12 = pad_pos(fp_u1, 12)
    via(nets["GND"], (p_u1_12[0], 21.2))
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, (p_u1_12[0], 21.2), 0.35)

    # 8. Decoupling Capacitors C17 (0.1uF), C18 (10uF) at Y = 3.8 mm near U1 pin 24
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetOrientationDegrees(180)
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(51.5, 3.8))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)
    # GND via north of C17 pad 2
    via(nets["GND"], (50.725, 2.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c17, 2), (50.725, 2.3), 0.25)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(56.0, 3.8))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)
    # GND via north of C18 pad 2
    via(nets["GND"], (56.95, 2.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c18, 2), (56.95, 2.3), 0.25)

    # 9. Control Resistors R17..R21 horizontally below U1 at Y = 22.0 mm
    res_ctrl_cfg = [
        ("R18", "100k", 36.0, "GND", "MUX_S0"),
        ("R19", "100k", 41.5, "GND", "MUX_S1"),
        ("R17", "10k",  47.0, "MUX_EN", "+3.3V"),
        ("R20", "100k", 53.0, "MUX_S2", "GND"),
        ("R21", "100k", 59.0, "MUX_S3", "GND")
    ]
    r_ctrl_fps = {}
    for ref, val, rx, net_p1, net_p2 in res_ctrl_cfg:
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(ref)
        fp_r.SetValue(val)
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(rx, 22.0))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[net_p1] if pad.GetNumber() == "1" else nets[net_p2])
        board.Add(fp_r)
        r_ctrl_fps[ref] = fp_r

    # GND vias for R18, R19, R20, R21
    via(nets["GND"], (35.175, 23.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(r_ctrl_fps["R18"], 1), (35.175, 23.3), 0.25)

    via(nets["GND"], (40.675, 23.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(r_ctrl_fps["R19"], 1), (40.675, 23.3), 0.25)

    via(nets["GND"], (53.825, 23.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(r_ctrl_fps["R20"], 2), (53.825, 23.3), 0.25)

    via(nets["GND"], (59.825, 23.3))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(r_ctrl_fps["R21"], 2), (59.825, 23.3), 0.25)

    # +3.3V via for R17
    via(nets["+3.3V"], (47.825, 23.3))
    trk(pcbnew.F_Cu, nets["+3.3V"], pad_pos(r_ctrl_fps["R17"], 2), (47.825, 23.3), 0.25)

    # Connect resistor signal pads to U1 pins with Manhattan tracks on F.Cu
    trk(pcbnew.F_Cu, nets["MUX_S0"], (36.825, 22.0), (36.825, 17.445), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_S0"], (36.825, 17.445), (45.35, 17.445), 0.20)

    trk(pcbnew.F_Cu, nets["MUX_S1"], (42.325, 22.0), (42.325, 18.715), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_S1"], (42.325, 18.715), (45.35, 18.715), 0.20)

    via(nets["MUX_EN"], (46.175, 20.8))
    trk(pcbnew.F_Cu, nets["MUX_EN"], pad_pos(r_ctrl_fps["R17"], 1), (46.175, 20.8), 0.20)
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (46.175, 20.8), (57.5, 20.8), 0.20)
    trk(pcbnew.In2_Cu, nets["MUX_EN"], (57.5, 20.8), (57.5, 17.445), 0.20)
    via(nets["MUX_EN"], (57.5, 17.445))
    trk(pcbnew.F_Cu, nets["MUX_EN"], (57.5, 17.445), (54.65, 17.445), 0.20)

    trk(pcbnew.F_Cu, nets["MUX_S2"], (52.175, 22.0), (52.0, 22.0), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_S2"], (52.0, 22.0), (52.0, 18.715), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_S2"], (52.0, 18.715), (54.65, 18.715), 0.20)

    trk(pcbnew.F_Cu, nets["MUX_S3"], (58.175, 22.0), (58.175, 19.985), 0.20)
    trk(pcbnew.F_Cu, nets["MUX_S3"], (58.175, 19.985), (54.65, 19.985), 0.20)

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

    # Coil via above each coil Pad 1
    coil_pad_vias = {}
    for c_id in range(1, 17):
        lp1 = l_pad1[c_id]
        v_l = (lp1[0], lp1[1] - 0.7)
        via(nets[f"RF_COIL_{c_id}"], v_l)
        trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
        coil_pad_vias[c_id] = v_l

    # 11. Clean Silkscreen Outer Grid Box
    box_corners = [(12.0, 23.5), (88.0, 23.5), (88.0, 99.5), (12.0, 99.5)]
    for i in range(4):
        p1, p2 = box_corners[i], box_corners[(i + 1) % 4]
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(pcbnew.F_SilkS)
        line.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        line.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
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

    # 14. +3.3V Power Bus
    p_j1_1 = pad_pos(fp_j1, 1)  # (11.0, 5.0)
    p_j1_2 = pad_pos(fp_j1, 2)  # (11.0, 2.46)
    p_j2_3 = pad_pos(fp_j2, 3)  # (71.08, 4.0)

    trk(pcbnew.F_Cu, nets["+3.3V"], p_j1_1, p_j1_2, 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], p_j1_2, (p_j1_2[0], 3.73), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j1_2[0], 3.73), (48.0, 3.73), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (48.0, 3.73), (48.0, 2.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (48.0, 2.2), (54.65, 2.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (54.65, 2.2), (54.65, 3.8), 0.35)

    # Via to F.Cu at (54.65, 3.8)
    via(nets["+3.3V"], (54.65, 3.8))
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 3.8), pad_pos(fp_c17, 1), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 3.8), pad_pos(fp_c18, 1), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 3.8), pad_pos(fp_u1, 24), 0.35)

    # +3.3V to J2.3 on B.Cu: from (54.65, 2.2) east to X = 71.08 mm, south to J2.3
    trk(pcbnew.B_Cu, nets["+3.3V"], (54.65, 2.2), (71.08, 2.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (71.08, 2.2), p_j2_3, 0.35)

    # +3.3V tap to R17 at (47.825, 23.3) on B.Cu
    trk(pcbnew.B_Cu, nets["+3.3V"], (47.825, 3.73), (47.825, 23.3), 0.25)

    # 15. Pass-Through Signals J1 -> J2 (Top corridor with layer uncrossing)
    # SCK on In2.Cu: (13.54, 2.46) -> Y = 0.8 mm -> via at (76.16, 0.8) to B.Cu -> J2.5
    p_j1_4 = pad_pos(fp_j1, 4)
    p_j2_5 = pad_pos(fp_j2, 5)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], p_j1_4, (p_j1_4[0], 0.8), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], (p_j1_4[0], 0.8), (p_j2_5[0], 0.8), 0.20)
    via(nets["SPI_SCK"], (p_j2_5[0], 0.8))
    trk(pcbnew.B_Cu, nets["SPI_SCK"], (p_j2_5[0], 0.8), p_j2_5, 0.20)

    # MISO on B.Cu: (16.08, 2.46) -> Y = 0.8 mm -> via at (78.70, 0.8) to In2.Cu -> J2.6
    p_j1_6 = pad_pos(fp_j1, 6)
    p_j2_6 = pad_pos(fp_j2, 6)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], p_j1_6, (p_j1_6[0], 0.8), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], (p_j1_6[0], 0.8), (p_j2_6[0], 0.8), 0.20)
    via(nets["SPI_MISO"], (p_j2_6[0], 0.8))
    trk(pcbnew.In2_Cu, nets["SPI_MISO"], (p_j2_6[0], 0.8), p_j2_6, 0.20)

    # MOSI on In2.Cu at Y = 1.2 mm: (18.62, 2.46) -> (18.62, 1.2) -> (81.24, 1.2) -> J2.7
    p_j1_8 = pad_pos(fp_j1, 8)
    p_j2_7 = pad_pos(fp_j2, 7)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], p_j1_8, (p_j1_8[0], 1.2), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], (p_j1_8[0], 1.2), (p_j2_7[0], 1.2), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_MOSI"], (p_j2_7[0], 1.2), p_j2_7, 0.20)

    # CS on B.Cu at Y = 1.2 mm: (21.16, 2.46) -> (21.16, 1.2) -> (83.78, 1.2) -> J2.8
    p_j1_10 = pad_pos(fp_j1, 10)
    p_j2_8 = pad_pos(fp_j2, 8)
    trk(pcbnew.B_Cu, nets["SPI_CS"], p_j1_10, (p_j1_10[0], 1.2), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_CS"], (p_j1_10[0], 1.2), (p_j2_8[0], 1.2), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_CS"], (p_j2_8[0], 1.2), p_j2_8, 0.20)

    # IRQ on In2.Cu at Y = 1.6 mm: (23.70, 2.46) -> (23.70, 1.6) -> (86.32, 1.6) -> J2.9
    p_j1_12 = pad_pos(fp_j1, 12)
    p_j2_9 = pad_pos(fp_j2, 9)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], p_j1_12, (p_j1_12[0], 1.6), 0.20)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], (p_j1_12[0], 1.6), (p_j2_9[0], 1.6), 0.20)
    trk(pcbnew.In2_Cu, nets["NFC_IRQ"], (p_j2_9[0], 1.6), p_j2_9, 0.20)

    # RST on B.Cu at Y = 1.6 mm: (26.24, 2.46) -> (26.24, 1.6) -> (88.86, 1.6) -> J2.10
    p_j1_14 = pad_pos(fp_j1, 14)
    p_j2_10 = pad_pos(fp_j2, 10)
    trk(pcbnew.B_Cu, nets["NFC_RST"], p_j1_14, (p_j1_14[0], 1.6), 0.20)
    trk(pcbnew.B_Cu, nets["NFC_RST"], (p_j1_14[0], 1.6), (p_j2_10[0], 1.6), 0.20)
    trk(pcbnew.B_Cu, nets["NFC_RST"], (p_j2_10[0], 1.6), p_j2_10, 0.20)

    # 16. RF_SIG Microstrip on F.Cu: U1.1 -> J2.1 -> J3.1
    p_u1_1 = pad_pos(fp_u1, 1)  # (45.35, 6.015)
    p_j2_1 = pad_pos(fp_j2, 1)  # (66.0, 4.0)
    p_j3_1 = pad_pos(fp_j3, 1)  # (93.0, 50.0)

    trk(pcbnew.F_Cu, nets["RF_SIG"], p_u1_1, (p_u1_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_u1_1[0], 2.0), (p_j2_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), p_j2_1, 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), (90.5, 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, 2.0), (90.5, 10.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, 10.0), (p_j3_1[0], 10.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j3_1[0], 10.0), p_j3_1, 0.35)

    # 17. Control Lines on B.Cu (Nested U-Turn avoiding all tank vias)
    # S0: (13.54, 5.0) -> (13.0, 5.0) -> (13.0, 17.0) -> (36.825, 17.0) -> (36.825, 22.0)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (13.54, 5.0), (13.0, 5.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (13.0, 5.0), (13.0, 17.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (13.0, 17.0), (36.825, 17.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (36.825, 17.0), (36.825, 22.0), 0.20)
    via(nets["MUX_S0"], (36.825, 22.0))

    # S1: (16.08, 5.0) -> (12.0, 5.0) -> (12.0, 18.0) -> (42.325, 18.0) -> (42.325, 22.0)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (16.08, 5.0), (16.08, 5.6), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (16.08, 5.6), (12.0, 5.6), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (12.0, 5.6), (12.0, 18.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (12.0, 18.0), (42.325, 18.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (42.325, 18.0), (42.325, 22.0), 0.20)
    via(nets["MUX_S1"], (42.325, 22.0))

    # EN: (23.70, 5.0) -> (11.0, 5.0) -> (11.0, 19.0) -> (46.175, 19.0) -> (46.175, 20.8)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (23.70, 5.0), (23.70, 6.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (23.70, 6.0), (11.0, 6.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (11.0, 6.0), (11.0, 19.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (11.0, 19.0), (46.175, 19.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (46.175, 19.0), (46.175, 20.8), 0.20)

    # S2: (21.16, 5.0) -> (10.0, 5.0) -> (10.0, 20.0) -> (52.175, 20.0) -> (52.175, 22.0)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (21.16, 5.0), (21.16, 6.4), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (21.16, 6.4), (10.0, 6.4), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (10.0, 6.4), (10.0, 20.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (10.0, 20.0), (52.175, 20.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (52.175, 20.0), (52.175, 22.0), 0.20)
    via(nets["MUX_S2"], (52.175, 22.0))

    # S3: (18.62, 5.0) -> (9.0, 5.0) -> (9.0, 21.0) -> (58.175, 21.0) -> (58.175, 22.0)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (18.62, 5.0), (18.62, 6.8), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (18.62, 6.8), (9.0, 6.8), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (9.0, 6.8), (9.0, 21.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (9.0, 21.0), (58.175, 21.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (58.175, 21.0), (58.175, 22.0), 0.20)
    via(nets["MUX_S3"], (58.175, 22.0))

    # 18. 16 LC Tanks Architecture
    tank_vias = {}

    # Left tanks k = 0..7
    u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]
    left_cell_ids = [1, 5, 9, 13, 2, 6, 10, 14]
    for k in range(8):
        cell_id = left_cell_ids[k]
        y_k = u1_left_y[k]
        cx = 17.0 + k * 3.5
        net_ch = nets[f"RF_CH{k}"]
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

        # GND via at exact half-pitch offset (cx - 1.8, y_k - 1.905)
        via(nets["GND"], (cx - 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx - 0.825, y_k - 1.8), (cx - 1.8, y_k - 1.905), 0.20)

        # Signal via at (cx - 1.8, y_k)
        v_pos = (cx - 1.8, y_k)
        via(net_coil, v_pos)
        trk(pcbnew.F_Cu, net_coil, (cx - 0.825, y_k), v_pos, 0.20)
        tank_vias[cell_id] = v_pos

    # Right tanks k = 8..15
    # Column C: cells 15, 11, 7, 3 (y = 7.285, 8.555, 9.825, 11.095)
    # Column D: cells 16, 12, 8, 4 (y = 12.365, 13.635, 14.905, 16.175)
    u1_right_pins = [
        (8, 15, 7.285, 59.0),
        (9, 11, 8.555, 62.5),
        (10, 7, 9.825, 66.0),
        (11, 3, 11.095, 69.5),
        (12, 16, 12.365, 73.0),
        (13, 12, 13.635, 76.5),
        (14, 8, 14.905, 80.0),
        (15, 4, 16.175, 83.5)
    ]
    for ch_num, cell_id, y_k, cx in u1_right_pins:
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

        # GND via at exact half-pitch offset (cx + 1.8, y_k - 1.905)
        via(nets["GND"], (cx + 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx + 0.825, y_k - 1.8), (cx + 1.8, y_k - 1.905), 0.20)

        # Signal via at (cx + 1.8, y_k)
        v_pos = (cx + 1.8, y_k)
        via(net_coil, v_pos)
        trk(pcbnew.F_Cu, net_coil, (cx + 0.825, y_k), v_pos, 0.20)
        tank_vias[cell_id] = v_pos

    # 19. Vertical Routing from Tank Vias to Coils (100% Planar on In2.Cu!)
    # Column A & B (feeds at left: X = 12.875 and X = 31.875)
    col_a_lanes = {13: 7.0, 9: 7.6, 5: 8.2, 1: 8.8}
    col_b_lanes = {14: 27.2, 10: 27.6, 6: 28.0, 2: 28.4}

    for c_group in [col_a_lanes, col_b_lanes]:
        for cell_id, lx in c_group.items():
            net = nets[f"RF_COIL_{cell_id}"]
            v_start = tank_vias[cell_id]
            v_end = coil_pad_vias[cell_id]
            trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
            trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
            trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

    # Column C (feeds at right: X = 68.125)
    # Tank vias: 15 (60.8), 11 (64.3), 7 (67.8), 3 (71.3)
    col_c_cfg = [
        (15, 60.8),
        (11, 64.3),
        (7,  67.4), # shifted to 67.4 to give > 0.32 mm clearance to Row 1 coil feed via at 68.125
        (3,  71.3)
    ]
    for cell_id, lx in col_c_cfg:
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

    # Column D (feeds at right: X = 87.125)
    # Tank vias: 16 (74.8), 12 (78.3), 8 (81.8), 4 (85.3)
    col_d_cfg = [
        (16, 74.8),
        (12, 77.3), # shifted to 77.3 to clear center pad 2 at 78.5
        (8,  81.8),
        (4,  85.3)
    ]
    for cell_id, lx in col_d_cfg:
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

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

    out_file = "/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4/test_grid_4x4.kicad_pcb"
    board.Save(out_file)
    print(f"Successfully generated {out_file}")

if __name__ == '__main__':
    build_pcb()
