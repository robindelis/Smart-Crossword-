#!/usr/bin/env python3
"""
Test clean board DRC
"""
import pcbnew
import os

b = pcbnew.BOARD()
b.SetCopperLayerCount(4)

nets = {}
for name in ["GND", "+3.3V", "RF_SIG", "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
             "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
             "I2C_SDA", "I2C_SCL", "GPIO_AUX"] + [f"RF_CH{k}" for k in range(16)] + [f"RF_COIL_{k+1}" for k in range(16)]:
    net = pcbnew.NETINFO_ITEM(b, name)
    b.Add(net)
    nets[name] = net

# Board outline 100x100
for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
    seg = pcbnew.PCB_SHAPE(b)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
    seg.SetWidth(int(0.15 * 1e6))
    b.Add(seg)

# 4 Mounting holes
for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
    fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
    fp_h.SetReference(f"H{idx+1}")
    fp_h.SetValue("MountingHole_M3")
    fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
    for pad in fp_h.Pads():
        pad.SetNet(nets["GND"])
    b.Add(fp_h)

# U1 CD74HC4067 at (50.0, 13.5)
fp_u1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Package_SO.pretty', 'SOIC-24W_7.5x15.4mm_P1.27mm')
fp_u1.SetReference("U1")
fp_u1.SetValue("CD74HC4067M")
fp_u1.SetPosition(pcbnew.VECTOR2I_MM(50.0, 13.5))
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

# J1 Host Header (2x10) rotated 90 degrees at (8.0, 6.0)
fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
fp_j1.SetReference("J1")
fp_j1.SetValue("Host_Header_2x10")
fp_j1.SetOrientationDegrees(90)
fp_j1.SetPosition(pcbnew.VECTOR2I_MM(8.0, 6.0))
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
b.Add(fp_j1)

# J2 NFC Transceiver Header (1x10) rotated 90 degrees at (72.0, 6.0)
fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
fp_j2.SetReference("J2")
fp_j2.SetValue("NFC_Module_Header")
fp_j2.SetOrientationDegrees(90)
fp_j2.SetPosition(pcbnew.VECTOR2I_MM(72.0, 6.0))
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
b.Add(fp_j2)

# J3 SMA RF Port at (63.0, 3.5)
fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
fp_j3.SetReference("J3")
fp_j3.SetValue("SMA_RF_TEST")
fp_j3.SetPosition(pcbnew.VECTOR2I_MM(63.0, 3.5))
for pad in fp_j3.Pads():
    pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
b.Add(fp_j3)

# C17 (0.1uF 0603) and C18 (10uF 0805)
fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
fp_c17.SetReference("C17")
fp_c17.SetValue("0.1uF")
fp_c17.SetPosition(pcbnew.VECTOR2I_MM(50.0, 2.5))
for pad in fp_c17.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
b.Add(fp_c17)

fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
fp_c18.SetReference("C18")
fp_c18.SetValue("10uF")
fp_c18.SetPosition(pcbnew.VECTOR2I_MM(45.0, 2.5))
for pad in fp_c18.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
b.Add(fp_c18)

# R17 (10k) pullup on EN at (55.0, 2.5)
fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r17.SetReference("R17")
fp_r17.SetValue("10k")
fp_r17.SetPosition(pcbnew.VECTOR2I_MM(55.0, 2.5))
for pad in fp_r17.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["MUX_EN"])
b.Add(fp_r17)

# R18..R21 pulldowns on S0..S3
for idx, s_name in enumerate(["MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3"]):
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{18+idx}")
    fp_r.SetValue("100k")
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(45.5 + idx * 3.0, 21.0))
    for pad in fp_r.Pads():
        pad.SetNet(nets[s_name] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_r)

# 16 Tuning Capacitors and 16 Damping Resistors
# Left Corridor: X = 33.0 to 42.0 mm, Y = 6.5 to 19.0 mm
for k in range(8):
    cell_id = k + 1
    cy = 7.0 + k * 1.5
    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(34.5, cy))
    for pad in fp_c.Pads():
        pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_c)

    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(38.5, cy))
    for pad in fp_r.Pads():
        pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
    b.Add(fp_r)

# Right Corridor: X = 58.0 to 67.0 mm, Y = 6.5 to 19.0 mm
for k in range(8, 16):
    cell_id = k + 1
    cy = 7.0 + (k - 8) * 1.5
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(58.5, cy))
    for pad in fp_r.Pads():
        pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
    b.Add(fp_r)

    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(62.5, cy))
    for pad in fp_c.Pads():
        pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
    b.Add(fp_c)

# 16 Coils
col_x = [21.5, 40.5, 59.5, 78.5]
row_y = [33.0, 52.0, 71.0, 90.0]
cell_letters = ["A", "B", "C", "D"]

for r_idx in range(4):
    for c_idx in range(4):
        k = r_idx * 4 + c_idx
        cell_id = k + 1
        xc = col_x[c_idx]
        yc = row_y[r_idx]
        cell_name = f"{cell_letters[c_idx]}{r_idx+1}"

        fp_l = pcbnew.FOOTPRINT(b)
        fp_l.SetReference(f"L{cell_id}")
        fp_l.SetValue("1.26uH")
        fp_l.AddNetTiePadGroup('1, 2')
        fp_l.SetPosition(pcbnew.VECTOR2I_MM(xc, yc))

        # Pad 1 (SMD F.Cu at top-left)
        p1 = pcbnew.PAD(fp_l)
        p1.SetNumber("1")
        p1.SetShape(pcbnew.PAD_SHAPE_RECT)
        p1.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        p1.SetLayerSet(p1.SMDMask())
        p1.SetSize(pcbnew.VECTOR2I_MM(0.8, 0.8))
        p1.SetPosition(pcbnew.VECTOR2I_MM(xc - 8.625, yc - 8.625))
        p1.SetNet(nets[f"RF_COIL_{cell_id}"])
        fp_l.Add(p1)

        # Pad 2 (PTH at center)
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

        # 7-turn spiral
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

        # 19mm boundary on F_SilkS
        s19 = 19.0 / 2.0
        for pA, pB in [((-s19, -s19), (s19, -s19)), ((s19, -s19), (s19, s19)),
                      ((s19, s19), (-s19, s19)), ((-s19, s19), (-s19, -s19))]:
            line = pcbnew.PCB_SHAPE(fp_l)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetLayer(pcbnew.F_SilkS)
            line.SetStart(pcbnew.VECTOR2I_MM(xc + pA[0], yc + pA[1]))
            line.SetEnd(pcbnew.VECTOR2I_MM(xc + pB[0], yc + pB[1]))
            line.SetWidth(int(0.12 * 1e6))
            fp_l.Add(line)

        txt = pcbnew.PCB_TEXT(fp_l)
        txt.SetText(f"{cell_name} (I{k})")
        txt.SetLayer(pcbnew.F_SilkS)
        txt.SetPosition(pcbnew.VECTOR2I_MM(xc, yc + 2.5))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(1.2, 1.2))
        fp_l.Add(txt)

        b.Add(fp_l)

        # B.Cu return trace
        ret_trk = pcbnew.PCB_TRACK(b)
        ret_trk.SetStart(pcbnew.VECTOR2I_MM(xc, yc))
        ret_trk.SetEnd(pcbnew.VECTOR2I_MM(xc - 9.0, yc))
        ret_trk.SetWidth(int(0.35 * 1e6))
        ret_trk.SetLayer(pcbnew.B_Cu)
        ret_trk.SetNet(nets["GND"])
        b.Add(ret_trk)

# In1.Cu Ground Plane with 16 Cutouts
zone_gnd_in1 = pcbnew.ZONE(b)
zone_gnd_in1.SetLayer(pcbnew.In1_Cu)
zone_gnd_in1.SetNet(nets["GND"])
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
        cut_poly = pcbnew.SHAPE_LINE_CHAIN()
        for cdx, cdy in [(-cut_half, -cut_half), (cut_half, -cut_half),
                         (cut_half, cut_half), (-cut_half, cut_half)]:
            cut_poly.Append(pcbnew.VECTOR2I_MM(cx + cdx, ry + cdy))
        cut_poly.SetClosed(True)
        cutout.AddPolygon(cut_poly)
        b.Add(cutout)

# In2.Cu Power Rail
zone_vcc_in2 = pcbnew.ZONE(b)
zone_vcc_in2.SetLayer(pcbnew.In2_Cu)
zone_vcc_in2.SetNet(nets["+3.3V"])
poly_in2 = pcbnew.SHAPE_LINE_CHAIN()
for px, py in [(10.0, 1.0), (90.0, 1.0), (90.0, 22.0), (10.0, 22.0)]:
    poly_in2.Append(pcbnew.VECTOR2I_MM(px, py))
poly_in2.SetClosed(True)
zone_vcc_in2.AddPolygon(poly_in2)
b.Add(zone_vcc_in2)

# B.Cu Bottom Ground Shield
zone_bcu = pcbnew.ZONE(b)
zone_bcu.SetLayer(pcbnew.B_Cu)
zone_bcu.SetNet(nets["GND"])
poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
    poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
poly_bcu.SetClosed(True)
zone_bcu.AddPolygon(poly_bcu)
b.Add(zone_bcu)

b.Save('/tmp/test_clean_board.kicad_pcb')
print('Board saved to /tmp/test_clean_board.kicad_pcb')
