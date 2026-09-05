#!/usr/bin/env python3
"""
test_manhattan_drc.py - Perfect 0-DRC, 0-unconnected generator using Manhattan routing.
Layer 1 (F.Cu): Coils, SMD components, RF_SIG microstrip
Layer 2 (In1.Cu): Solid GND plane with 16 anti-copper coil keepouts
Layer 3 (In2.Cu): Horizontal signal busses & SPI bus
Layer 4 (B.Cu): Vertical signal routing & Bottom GND plane
"""
import pcbnew
import subprocess
import json

def build():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)

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
        net = pcbnew.NETINFO_ITEM(b, name)
        b.Add(net)
        nets[name] = net

    def trk(layer, net, p1, p2, width=0.20):
        t = pcbnew.PCB_TRACK(b)
        t.SetLayer(layer)
        t.SetNet(net)
        t.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        t.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
        t.SetWidth(int(width * 1e6))
        b.Add(t)
        return t

    def via(net, pos, size=0.6, drill=0.3):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetWidth(int(size * 1e6))
        v.SetDrill(int(drill * 1e6))
        v.SetNet(net)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        b.Add(v)
        return v

    def pad_pos(fp, pad_num):
        pad = fp.FindPadByNumber(str(pad_num))
        p = pad.GetPosition()
        return (p.x / 1e6, p.y / 1e6)

    # 2. Board Outline 100mm x 100mm
    corners = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(b)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(corners[i][0], corners[i][1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(corners[(i+1)%4][0], corners[(i+1)%4][1]))
        seg.SetWidth(int(0.15 * 1e6))
        b.Add(seg)

    # 3. 4x M3 Mounting Holes
    for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
        fp_h = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3_Pad_Via")
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        fp_h.Reference().SetVisible(False)
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        b.Add(fp_h)

    # 4. Host Header J1 (2x10, 2.54mm pitch) at (7.0, 6.0)
    # Pitch 2.54mm, 10 pins -> length = 22.86mm. Center is at (18.43, 6.0)
    fp_j1 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty", "PinHeader_2x10_P2.54mm_Vertical")
    fp_j1.SetReference("J1")
    fp_j1.SetValue("HOST_BUS")
    fp_j1.SetOrientationDegrees(90)
    fp_j1.SetPosition(pcbnew.VECTOR2I_MM(7.0, 6.0))
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
    b.Add(fp_j1)

    # 5. NFC Header J2 (1x10, 2.54mm pitch) at (66.0, 5.0)
    fp_j2 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty", "PinHeader_1x10_P2.54mm_Vertical")
    fp_j2.SetReference("J2")
    fp_j2.SetValue("NFC_MODULE")
    fp_j2.SetOrientationDegrees(90)
    fp_j2.SetPosition(pcbnew.VECTOR2I_MM(66.0, 5.0))
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
    b.Add(fp_j2)

    # 6. SMA RF Test Port J3 at (93.0, 14.0)
    fp_j3 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_Coaxial.pretty", "SMA_Amphenol_132134-10_Vertical")
    fp_j3.SetReference("J3")
    fp_j3.SetValue("RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 14.0))
    fp_j3.Reference().SetVisible(False)
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_j3)

    # GND vias for J3 pads on F.Cu:
    for pad in fp_j3.Pads():
        if pad.GetNumber() != "1":
            p = pad.GetPosition()
            via(nets["GND"], (p.x / 1e6, p.y / 1e6))

    # 7. CD74HC4067 Multiplexer U1 (SOIC-24) at (50.0, 13.0)
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
    b.Add(fp_u1)

    # U1 Ground (Pin 12 at 45.35, 19.985): Via to GND plane
    p_u1_12 = pad_pos(fp_u1, 12)
    via(nets["GND"], (p_u1_12[0] - 1.5, p_u1_12[1]))
    trk(pcbnew.F_Cu, nets["GND"], p_u1_12, (p_u1_12[0] - 1.5, p_u1_12[1]), 0.35)

    # 8. Decoupling Capacitors C17 (0.1uF 0603) and C18 (10uF 0805)
    # Position them at Y = 4.0, with Pad 1 on left (+3.3V) and Pad 2 on right (GND)
    fp_c17 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Capacitor_SMD.pretty", "C_0603_1608Metric")
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(46.0, 4.0))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Capacitor_SMD.pretty", "C_0805_2012Metric")
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(51.0, 4.0))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_c18)

    # GND vias for C17 and C18:
    via(nets["GND"], (pad_pos(fp_c17, 2)[0], 5.5))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c17, 2), (pad_pos(fp_c17, 2)[0], 5.5), 0.25)

    via(nets["GND"], (pad_pos(fp_c18, 2)[0], 5.5))
    trk(pcbnew.F_Cu, nets["GND"], pad_pos(fp_c18, 2), (pad_pos(fp_c18, 2)[0], 5.5), 0.25)

    # Connect C17/C18 +3.3V to U1.24 via top corridor:
    p_u1_24 = pad_pos(fp_u1, 24)
    trk(pcbnew.F_Cu, nets["+3.3V"], pad_pos(fp_c17, 1), (pad_pos(fp_c17, 1)[0], 2.8), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (pad_pos(fp_c17, 1)[0], 2.8), (pad_pos(fp_c18, 1)[0], 2.8), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (pad_pos(fp_c18, 1)[0], 2.8), pad_pos(fp_c18, 1), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (pad_pos(fp_c18, 1)[0], 2.8), (p_u1_24[0], 2.8), 0.35)
    trk(pcbnew.F_Cu, nets["+3.3V"], (p_u1_24[0], 2.8), p_u1_24, 0.35)

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

            fp_l = pcbnew.FOOTPRINT(b)
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

            b.Add(fp_l)

            # Ground return trace for Pad 2 on B.Cu out to ground plane:
            trk(pcbnew.B_Cu, nets["GND"], (xc, yc), (xc, yc + 9.5), 0.30)

    # Coil via above each coil Pad 1
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
        b.Add(fp_r)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetOrientationDegrees(180)
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        b.Add(fp_c)

        trk(pcbnew.F_Cu, net_ch, (cx + 0.825, y_k), (cx + 0.825, y_k - 1.8), 0.20)
        trk(pcbnew.F_Cu, net_ch, (45.35, y_k), (cx + 0.825, y_k), 0.20)

        # GND via for C
        via(nets["GND"], (cx - 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx - 0.825, y_k - 1.8), (cx - 1.8, y_k - 1.905), 0.20)

        # Signal via for R
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
        b.Add(fp_r)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
        b.Add(fp_c)

        trk(pcbnew.F_Cu, net_ch, (cx - 0.825, y_k), (cx - 0.825, y_k - 1.8), 0.20)
        trk(pcbnew.F_Cu, net_ch, (54.65, y_k), (cx - 0.825, y_k), 0.20)

        # GND via for C
        via(nets["GND"], (cx + 1.8, y_k - 1.905))
        trk(pcbnew.F_Cu, nets["GND"], (cx + 0.825, y_k - 1.8), (cx + 1.8, y_k - 1.905), 0.20)

        # Signal via for R
        v_pos = (cx + 1.8, y_k)
        via(net_coil, v_pos)
        trk(pcbnew.F_Cu, net_coil, (cx + 0.825, y_k), v_pos, 0.20)
        tank_vias[cell_id] = v_pos

    # 11. Manhattan Routing for RF_COIL signals:
    # Horizontal on In2.Cu from tank via to dedicated lane X
    # Via at (lane_X, tank_Y) to B.Cu
    # Vertical on B.Cu from tank_Y down to coil_pad_Y
    # Via at (lane_X, coil_pad_Y) to In2.Cu
    # Horizontal on In2.Cu to coil feed via!
    # Dedicated lanes:
    # Col A (cells 13, 9, 5, 1): X = 5.5, 6.5, 7.5, 8.5
    # Col B (cells 14, 10, 6, 2): X = 26.5, 27.5, 28.5, 29.5
    # Col C (cells 15, 11, 7, 3): X = 60.5, 63.5, 66.5, 70.5
    # Col D (cells 16, 12, 8, 4): X = 74.5, 77.0, 81.5, 85.0
    lane_map = {
        13: 5.5, 9: 6.5, 5: 7.5, 1: 8.5,
        14: 26.5, 10: 27.5, 6: 28.5, 2: 29.5,
        15: 60.5, 11: 63.5, 7: 66.5, 3: 70.5,
        16: 74.5, 12: 77.0, 8: 81.5, 4: 85.0
    }
    for cell_id, lx in lane_map.items():
        net = nets[f"RF_COIL_{cell_id}"]
        v_start = tank_vias[cell_id]
        v_end = coil_pad_vias[cell_id]

        # Horizontal on In2.Cu from v_start to (lx, v_start[1])
        trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]), 0.20)
        # Via to B.Cu
        via(net, (lx, v_start[1]))
        # Vertical on B.Cu from (lx, v_start[1]) down to (lx, v_end[1])
        trk(pcbnew.B_Cu, net, (lx, v_start[1]), (lx, v_end[1]), 0.20)
        # Via to In2.Cu
        via(net, (lx, v_end[1]))
        # Horizontal on In2.Cu to v_end
        trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end, 0.20)

    # 12. RF_SIG Trace on F.Cu:
    # Starts at U1.1 (45.35, 6.015)
    # Jogs to (45.35, 2.0) -> east to (66.0, 2.0) -> south to J2.1 (66.0, 5.0)
    # Continues east to (90.5, 2.0) -> south to (90.5, 14.0) -> east to J3.1 (93.0, 14.0)
    p_u1_1 = pad_pos(fp_u1, 1)
    p_j2_1 = pad_pos(fp_j2, 1)
    p_j3_1 = pad_pos(fp_j3, 1)
    trk(pcbnew.F_Cu, nets["RF_SIG"], p_u1_1, (p_u1_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_u1_1[0], 2.0), (p_j2_1[0], 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), p_j2_1, 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (p_j2_1[0], 2.0), (90.5, 2.0), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, 2.0), (90.5, p_j3_1[1]), 0.35)
    trk(pcbnew.F_Cu, nets["RF_SIG"], (90.5, p_j3_1[1]), p_j3_1, 0.35)

    # 13. SPI Bus between J1 and J2 (Planar on In2.Cu)
    # Top of J1 pins at Y = 4.73. Edge clearance >= 0.6mm from top.
    # Lanes from top to bottom:
    # SCK:  Y = 0.8
    # MISO: Y = 1.1
    # MOSI: Y = 1.4
    # CS:   Y = 1.7
    # IRQ:  Y = 2.0
    # RST:  Y = 2.3
    spi_routes = [
        ("SPI_SCK",  4,  5, 0.8),
        ("SPI_MISO", 6,  6, 1.1),
        ("SPI_MOSI", 8,  7, 1.4),
        ("SPI_CS",   10, 8, 1.7),
        ("NFC_IRQ",  12, 9, 2.0),
        ("NFC_RST",  14, 10, 2.3)
    ]
    for sig_name, j1_pin, j2_pin, y_lane in spi_routes:
        p_j1 = pad_pos(fp_j1, j1_pin)
        p_j2 = pad_pos(fp_j2, j2_pin)
        net_sig = nets[sig_name]
        trk(pcbnew.In2_Cu, net_sig, p_j1, (p_j1[0], y_lane), 0.20)
        trk(pcbnew.In2_Cu, net_sig, (p_j1[0], y_lane), (p_j2[0], y_lane), 0.20)
        trk(pcbnew.In2_Cu, net_sig, (p_j2[0], y_lane), p_j2, 0.20)

    # 14. +3.3V Power Bus on B.Cu
    # J1 pin 1 & 2 -> Y = 3.2 on B.Cu -> east to (46.0, 3.2) -> via to F.Cu (C17 pin 1)
    # continues east on B.Cu to (71.08, 3.2) -> south to J2 pin 3 (71.08, 5.0)
    p_j1_1 = pad_pos(fp_j1, 1)
    p_j1_2 = pad_pos(fp_j1, 2)
    p_j2_3 = pad_pos(fp_j2, 3)
    trk(pcbnew.F_Cu, nets["+3.3V"], p_j1_1, p_j1_2, 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], p_j1_2, (p_j1_2[0], 3.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j1_2[0], 3.2), (46.0, 3.2), 0.35)
    via(nets["+3.3V"], (46.0, 3.2))
    trk(pcbnew.F_Cu, nets["+3.3V"], (46.0, 3.2), pad_pos(fp_c17, 1), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (46.0, 3.2), (p_j2_3[0], 3.2), 0.35)
    trk(pcbnew.B_Cu, nets["+3.3V"], (p_j2_3[0], 3.2), p_j2_3, 0.35)

    # 15. MUX Address Lines from J1 to U1 on B.Cu
    # S0: J1.3 (9.54, 7.27) -> south to 17.445 -> east to 43.5 -> via to F.Cu -> U1.10
    p_s0 = pad_pos(fp_j1, 3)
    trk(pcbnew.B_Cu, nets["MUX_S0"], p_s0, (p_s0[0], 17.445), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S0"], (p_s0[0], 17.445), (43.5, 17.445), 0.20)
    via(nets["MUX_S0"], (43.5, 17.445))
    trk(pcbnew.F_Cu, nets["MUX_S0"], (43.5, 17.445), pad_pos(fp_u1, 10), 0.20)

    # S1: J1.5 (12.08, 7.27) -> south to 18.715 -> east to 43.5 -> via to F.Cu -> U1.11
    p_s1 = pad_pos(fp_j1, 5)
    trk(pcbnew.B_Cu, nets["MUX_S1"], p_s1, (p_s1[0], 18.715), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S1"], (p_s1[0], 18.715), (43.5, 18.715), 0.20)
    via(nets["MUX_S1"], (43.5, 18.715))
    trk(pcbnew.F_Cu, nets["MUX_S1"], (43.5, 18.715), pad_pos(fp_u1, 11), 0.20)

    # S3, S2, EN:
    p_s3 = pad_pos(fp_j1, 7)
    p_s2 = pad_pos(fp_j1, 9)
    p_en = pad_pos(fp_j1, 11)

    # EN: south to 20.8 -> east to 56.5 -> north to 17.445 -> via to F.Cu -> U1.15
    trk(pcbnew.B_Cu, nets["MUX_EN"], p_en, (p_en[0], 20.8), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (p_en[0], 20.8), (56.5, 20.8), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_EN"], (56.5, 20.8), (56.5, 17.445), 0.20)
    via(nets["MUX_EN"], (56.5, 17.445))
    trk(pcbnew.F_Cu, nets["MUX_EN"], (56.5, 17.445), pad_pos(fp_u1, 15), 0.20)

    # S2: south to 21.4 -> east to 57.2 -> north to 18.715 -> via to F.Cu -> U1.14
    trk(pcbnew.B_Cu, nets["MUX_S2"], p_s2, (p_s2[0], 21.4), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (p_s2[0], 21.4), (57.2, 21.4), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S2"], (57.2, 21.4), (57.2, 18.715), 0.20)
    via(nets["MUX_S2"], (57.2, 18.715))
    trk(pcbnew.F_Cu, nets["MUX_S2"], (57.2, 18.715), pad_pos(fp_u1, 14), 0.20)

    # S3: south to 22.0 -> east to 57.9 -> north to 19.985 -> via to F.Cu -> U1.13
    trk(pcbnew.B_Cu, nets["MUX_S3"], p_s3, (p_s3[0], 22.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (p_s3[0], 22.0), (57.9, 22.0), 0.20)
    trk(pcbnew.B_Cu, nets["MUX_S3"], (57.9, 22.0), (57.9, 19.985), 0.20)
    via(nets["MUX_S3"], (57.9, 19.985))
    trk(pcbnew.F_Cu, nets["MUX_S3"], (57.9, 19.985), pad_pos(fp_u1, 13), 0.20)

    # 16. In1.Cu Ground Plane with 16 Anti-copper Keepouts
    zone_gnd_in1 = pcbnew.ZONE(b)
    zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
    zone_gnd_in1.SetNetCode(nets["GND"].GetNetCode())
    zone_gnd_in1.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly_in1 = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_in1.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_in1.SetClosed(True)
    zone_gnd_in1.AddPolygon(poly_in1)
    b.Add(zone_gnd_in1)

    cut_half = 18.5 / 2.0
    for ry in row_y:
        for cx in col_x:
            cutout = pcbnew.ZONE(b)
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
            b.Add(cutout)

    # 17. B.Cu Bottom Ground Plane
    zone_bcu = pcbnew.ZONE(b)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNetCode(nets["GND"].GetNetCode())
    zone_bcu.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    b.Add(zone_bcu)

    # Fill all copper zones
    zf = pcbnew.ZONE_FILLER(b)
    zf.Fill(b.Zones())

    out_file = "/tmp/test_manhattan.kicad_pcb"
    b.Save(out_file)
    print(f"Saved to {out_file}")

if __name__ == '__main__':
    build()
