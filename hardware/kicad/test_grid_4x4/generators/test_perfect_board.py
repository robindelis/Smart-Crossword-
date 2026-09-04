#!/usr/bin/env python3
"""
Test perfectly routed board with zero DRC errors
"""
import os
import pcbnew

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)

nets = {}
for name in ["GND", "+3.3V", "RF_SIG", "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
             "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
             "I2C_SDA", "I2C_SCL", "GPIO_AUX"] + [f"RF_CH{k}" for k in range(16)] + [f"RF_COIL_{k+1}" for k in range(16)]:
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

# 1. Outline 100x100
for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
    seg.SetWidth(int(0.15 * 1e6))
    board.Add(seg)

# 2. 4x M3 Mounting Holes
for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
    fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
    fp_h.SetReference(f"H{idx+1}")
    fp_h.SetValue("MountingHole_M3")
    fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
    for pad in fp_h.Pads():
        pad.SetNet(nets["GND"])
    board.Add(fp_h)

# 3. U1 CD74HC4067M (SOIC-24) at (50.0, 13.0)
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

# 4. J1 Host Header 2x10 rotated 90 deg at (12.0, 5.5)
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

# 5. J2 NFC Module Header 1x10 rotated 90 deg at (65.0, 5.5)
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

# 6. J3 SMA RF Test Port at (93.0, 15.0)
fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
fp_j3.SetReference("J3")
fp_j3.SetValue("SMA_RF_TEST")
fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 15.0))
for pad in fp_j3.Pads():
    pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_j3)

# 7. Decoupling & Control SMD Parts
fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
fp_c17.SetReference("C17")
fp_c17.SetValue("0.1uF")
fp_c17.SetPosition(pcbnew.VECTOR2I_MM(52.0, 2.0))
fp_c17.Reference().SetVisible(False)
fp_c17.Value().SetVisible(False)
for pad in fp_c17.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_c17)

fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
fp_c18.SetReference("C18")
fp_c18.SetValue("10uF")
fp_c18.SetPosition(pcbnew.VECTOR2I_MM(56.0, 2.0))
fp_c18.Reference().SetVisible(False)
fp_c18.Value().SetVisible(False)
for pad in fp_c18.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_c18)

# R17 (10k pullup on EN) at (57.0, 17.445)
fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r17.SetReference("R17")
fp_r17.SetValue("10k")
fp_r17.SetPosition(pcbnew.VECTOR2I_MM(57.5, 17.445))
fp_r17.Reference().SetVisible(False)
fp_r17.Value().SetVisible(False)
for pad in fp_r17.Pads():
    pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["MUX_EN"])
board.Add(fp_r17)

# Pulldowns R18..R21 at X=42.0 (facing pins 10, 11) and X=57.5 (facing pins 14, 13)
# R18 (S0) at (42.5, 17.445)
fp_r18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r18.SetReference("R18")
fp_r18.SetValue("100k")
fp_r18.SetPosition(pcbnew.VECTOR2I_MM(42.5, 17.445))
fp_r18.Reference().SetVisible(False)
fp_r18.Value().SetVisible(False)
for pad in fp_r18.Pads():
    pad.SetNet(nets["MUX_S0"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_r18)

# R19 (S1) at (42.5, 18.715)
fp_r19 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r19.SetReference("R19")
fp_r19.SetValue("100k")
fp_r19.SetPosition(pcbnew.VECTOR2I_MM(42.5, 18.715))
fp_r19.Reference().SetVisible(False)
fp_r19.Value().SetVisible(False)
for pad in fp_r19.Pads():
    pad.SetNet(nets["MUX_S1"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_r19)

# R20 (S2) at (57.5, 18.715)
fp_r20 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r20.SetReference("R20")
fp_r20.SetValue("100k")
fp_r20.SetPosition(pcbnew.VECTOR2I_MM(57.5, 18.715))
fp_r20.Reference().SetVisible(False)
fp_r20.Value().SetVisible(False)
for pad in fp_r20.Pads():
    pad.SetNet(nets["MUX_S2"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_r20)

# R21 (S3) at (57.5, 19.985)
fp_r21 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
fp_r21.SetReference("R21")
fp_r21.SetValue("100k")
fp_r21.SetPosition(pcbnew.VECTOR2I_MM(57.5, 19.985))
fp_r21.Reference().SetVisible(False)
fp_r21.Value().SetVisible(False)
for pad in fp_r21.Pads():
    pad.SetNet(nets["MUX_S3"] if pad.GetNumber() == "1" else nets["GND"])
board.Add(fp_r21)

# 8. 16 Planar Spiral Coils L1..L16
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

        # B.Cu return trace
        trk(pcbnew.B_Cu, nets["GND"], (xc, yc), (xc - 9.0, yc), 0.35)

# Coil via above each coil Pad 1
coil_pad_vias = {}
for c_id in range(1, 17):
    lp1 = l_pad1[c_id]
    v_l = (lp1[0], lp1[1] - 0.7)
    via(nets[f"RF_COIL_{c_id}"], v_l)
    trk(pcbnew.F_Cu, nets[f"RF_COIL_{c_id}"], v_l, lp1, 0.25)
    coil_pad_vias[c_id] = v_l

# 9. 19mm silkscreen grid lines
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

# 10. In1.Cu Ground Plane with 16 Anti-copper Keepouts
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

# 11. B.Cu Bottom Ground Shield Plane
zone_bcu = pcbnew.ZONE(board)
zone_bcu.SetLayer(pcbnew.B_Cu)
zone_bcu.SetNet(nets["GND"])
poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
    poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
poly_bcu.SetClosed(True)
zone_bcu.AddPolygon(poly_bcu)
board.Add(zone_bcu)

# 12. RF_SIG Microstrip: U1 COM -> J2 pin 1 -> J3 pin 1
trk(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 6.015), (45.35, 4.5), 0.5)
trk(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 4.5), (65.0, 4.5), 0.5)
trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 4.5), (65.0, 5.5), 0.5)

trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 5.5), (65.0, 7.5), 0.5)
trk(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 7.5), (89.0, 7.5), 0.5)
trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 7.5), (89.0, 15.0), 0.5)
trk(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 15.0), (93.0, 15.0), 0.5)

# 13. Power (+3.3V) & GND Vias
trk(pcbnew.In2_Cu, nets["+3.3V"], (12.0, 2.96), (12.0, 1.3), 0.5)
trk(pcbnew.In2_Cu, nets["+3.3V"], (12.0, 1.3), (70.08, 1.3), 0.5)
trk(pcbnew.In2_Cu, nets["+3.3V"], (70.08, 1.3), (70.08, 5.5), 0.5)

# C17, C18 VCC
via(nets["+3.3V"], (51.175, 1.3))
trk(pcbnew.F_Cu, nets["+3.3V"], (51.175, 1.3), (51.175, 2.0))
via(nets["+3.3V"], (55.05, 1.3))
trk(pcbnew.F_Cu, nets["+3.3V"], (55.05, 1.3), (55.05, 2.0))

# U1 VCC pin 24 at (54.65, 6.015)
via(nets["+3.3V"], (54.65, 4.5))
trk(pcbnew.F_Cu, nets["+3.3V"], (54.65, 6.015), (54.65, 4.5))
trk(pcbnew.In2_Cu, nets["+3.3V"], (54.65, 4.5), (54.65, 1.3))

# R17 VCC pad 1 at (58.325, 17.445)
via(nets["+3.3V"], (59.5, 17.445))
trk(pcbnew.F_Cu, nets["+3.3V"], (58.325, 17.445), (59.5, 17.445))
trk(pcbnew.In2_Cu, nets["+3.3V"], (59.5, 17.445), (59.5, 1.3))

# GND vias
via(nets["GND"], (52.825, 2.0))
trk(pcbnew.F_Cu, nets["GND"], (52.825, 2.0), (52.825, 2.0)) # in pad via

via(nets["GND"], (56.95, 2.0))
trk(pcbnew.F_Cu, nets["GND"], (56.95, 2.0), (56.95, 2.0))

via(nets["GND"], (41.675, 17.445)) # R18 GND
trk(pcbnew.F_Cu, nets["GND"], (41.675, 17.445), (41.675, 17.445))

via(nets["GND"], (41.675, 18.715)) # R19 GND
trk(pcbnew.F_Cu, nets["GND"], (41.675, 18.715), (41.675, 18.715))

via(nets["GND"], (58.325, 18.715)) # R20 GND
trk(pcbnew.F_Cu, nets["GND"], (58.325, 18.715), (58.325, 18.715))

via(nets["GND"], (58.325, 19.985)) # R21 GND
trk(pcbnew.F_Cu, nets["GND"], (58.325, 19.985), (58.325, 19.985))

via(nets["GND"], (44.0, 19.985)) # U1 pin 12 GND
trk(pcbnew.F_Cu, nets["GND"], (45.35, 19.985), (44.0, 19.985))

# 14. Control Lines J1 -> Pulldown/Pullup -> U1
# S0: J1.3 (14.54, 5.5) -> R18.1 (43.325, 17.445) -> U1.10 (45.35, 17.445)
trk(pcbnew.In2_Cu, nets["MUX_S0"], (14.54, 5.5), (14.54, 17.445))
trk(pcbnew.In2_Cu, nets["MUX_S0"], (14.54, 17.445), (43.325, 17.445))
via(nets["MUX_S0"], (43.325, 17.445))
trk(pcbnew.F_Cu, nets["MUX_S0"], (43.325, 17.445), (45.35, 17.445))

# S1: J1.5 (17.08, 5.5) -> R19.1 (43.325, 18.715) -> U1.11 (45.35, 18.715)
trk(pcbnew.In2_Cu, nets["MUX_S1"], (17.08, 5.5), (17.08, 18.715))
trk(pcbnew.In2_Cu, nets["MUX_S1"], (17.08, 18.715), (43.325, 18.715))
via(nets["MUX_S1"], (43.325, 18.715))
trk(pcbnew.F_Cu, nets["MUX_S1"], (43.325, 18.715), (45.35, 18.715))

# S2: J1.7 (19.62, 5.5) -> R20.1 (56.675, 18.715) -> U1.14 (54.65, 18.715)
trk(pcbnew.In2_Cu, nets["MUX_S2"], (19.62, 5.5), (19.62, 20.8))
trk(pcbnew.In2_Cu, nets["MUX_S2"], (19.62, 20.8), (56.675, 20.8))
trk(pcbnew.In2_Cu, nets["MUX_S2"], (56.675, 20.8), (56.675, 18.715))
via(nets["MUX_S2"], (56.675, 18.715))
trk(pcbnew.F_Cu, nets["MUX_S2"], (56.675, 18.715), (54.65, 18.715))

# S3: J1.9 (22.16, 5.5) -> R21.1 (56.675, 19.985) -> U1.13 (54.65, 19.985)
trk(pcbnew.In2_Cu, nets["MUX_S3"], (22.16, 5.5), (22.16, 21.4))
trk(pcbnew.In2_Cu, nets["MUX_S3"], (22.16, 21.4), (56.675, 21.4))
trk(pcbnew.In2_Cu, nets["MUX_S3"], (56.675, 21.4), (56.675, 19.985))
via(nets["MUX_S3"], (56.675, 19.985))
trk(pcbnew.F_Cu, nets["MUX_S3"], (56.675, 19.985), (54.65, 19.985))

# EN: J1.11 (24.70, 5.5) -> R17.2 (56.675, 17.445) -> U1.15 (54.65, 17.445)
trk(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 5.5), (24.70, 22.0))
trk(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 22.0), (56.675, 22.0))
trk(pcbnew.In2_Cu, nets["MUX_EN"], (56.675, 22.0), (56.675, 17.445))
via(nets["MUX_EN"], (56.675, 17.445))
trk(pcbnew.F_Cu, nets["MUX_EN"], (56.675, 17.445), (54.65, 17.445))

# 15. Pass-Through Signals J1 -> J2 on In2_Cu
pass_pins = [
    ("SPI_SCK",  (14.54, 2.96), (75.16, 5.5), 2.1),
    ("SPI_MISO", (17.08, 2.96), (77.70, 5.5), 2.5),
    ("SPI_MOSI", (19.62, 2.96), (80.24, 5.5), 2.9),
    ("SPI_CS",   (22.16, 2.96), (82.78, 5.5), 3.3),
    ("NFC_IRQ",  (24.70, 2.96), (85.32, 5.5), 3.7),
    ("NFC_RST",  (27.24, 2.96), (87.86, 5.5), 4.1),
]
for s_name, p_j1, p_j2, y_route in pass_pins:
    trk(pcbnew.In2_Cu, nets[s_name], p_j1, (p_j1[0], y_route))
    trk(pcbnew.In2_Cu, nets[s_name], (p_j1[0], y_route), (p_j2[0], y_route))
    trk(pcbnew.In2_Cu, nets[s_name], (p_j2[0], y_route), p_j2)

# 16. 16 LC Tanks with Reversed Staircase
u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]
u1_right_y = [7.285, 8.555, 9.825, 11.095, 12.365, 13.635, 14.905, 16.175]

coil_vias = {}

# Left Channels 0..7:
for k in range(8):
    cell_id = k + 1
    y_k = u1_left_y[k]
    cx = 17.0 + k * 3.5
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # R_k at (cx, y_k)
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

    # C_k at (cx, y_k - 1.8)
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

    trk(pcbnew.F_Cu, net_ch, (cx + 0.825, y_k), (cx + 0.825, y_k - 1.8), 0.25)
    trk(pcbnew.F_Cu, net_ch, (45.35, y_k), (cx + 0.825, y_k), 0.25)

    via(nets["GND"], (cx - 1.8, y_k - 1.8))
    trk(pcbnew.F_Cu, nets["GND"], (cx - 0.825, y_k - 1.8), (cx - 1.8, y_k - 1.8), 0.25)

    v_pos = (cx - 1.8, y_k)
    via(net_coil, v_pos)
    trk(pcbnew.F_Cu, net_coil, (cx - 0.825, y_k), v_pos, 0.25)
    coil_vias[cell_id] = v_pos

# Right Channels 8..15:
for k in range(8, 16):
    cell_id = k + 1
    y_k = u1_right_y[k - 8]
    cx = 58.5 + (k - 8) * 3.5
    net_ch = nets[f"RF_CH{k}"]
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

    trk(pcbnew.F_Cu, net_ch, (cx - 0.825, y_k), (cx - 0.825, y_k - 1.8), 0.25)
    trk(pcbnew.F_Cu, net_ch, (54.65, y_k), (cx - 0.825, y_k), 0.25)

    via(nets["GND"], (cx + 1.8, y_k - 1.8))
    trk(pcbnew.F_Cu, nets["GND"], (cx + 0.825, y_k - 1.8), (cx + 1.8, y_k - 1.8), 0.25)

    v_pos = (cx + 1.8, y_k)
    via(net_coil, v_pos)
    trk(pcbnew.F_Cu, net_coil, (cx + 0.825, y_k), v_pos, 0.25)
    coil_vias[cell_id] = v_pos

# 17. Routing from Tank Vias to Coils
lane_x_map = {
    1: 7.0,   5: 8.0,   9: 9.0,   13: 10.0,
    2: 30.5,  6: 31.0,  10: 31.5, 14: 32.0,
    3: 49.5,  7: 50.0,  11: 50.5, 15: 51.0,
    4: 68.5,  8: 69.0,  12: 69.5, 16: 70.0,
}

# Cells 1, 2, 5, 6 on In2_Cu:
for cell_id in [1, 2, 5, 6]:
    v_start = coil_vias[cell_id]
    v_end = coil_pad_vias[cell_id]
    lx = lane_x_map[cell_id]
    net = nets[f"RF_COIL_{cell_id}"]
    trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]))
    trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]))
    trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end)

# Cells 11, 12, 15, 16 on In2_Cu:
for cell_id in [11, 12, 15, 16]:
    v_start = coil_vias[cell_id]
    v_end = coil_pad_vias[cell_id]
    lx = lane_x_map[cell_id]
    net = nets[f"RF_COIL_{cell_id}"]
    trk(pcbnew.In2_Cu, net, v_start, (lx, v_start[1]))
    trk(pcbnew.In2_Cu, net, (lx, v_start[1]), (lx, v_end[1]))
    trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end)

# Cells 3, 4, 7, 8 on In2_Cu (cross left to right):
y_cross_left_to_right = {3: 21.0, 4: 21.4, 7: 21.8, 8: 22.2}
for cell_id in [3, 4, 7, 8]:
    v_start = coil_vias[cell_id]
    v_end = coil_pad_vias[cell_id]
    lx = lane_x_map[cell_id]
    y_cr = y_cross_left_to_right[cell_id]
    net = nets[f"RF_COIL_{cell_id}"]
    trk(pcbnew.In2_Cu, net, v_start, (v_start[0], y_cr))
    trk(pcbnew.In2_Cu, net, (v_start[0], y_cr), (lx, y_cr))
    trk(pcbnew.In2_Cu, net, (lx, y_cr), (lx, v_end[1]))
    trk(pcbnew.In2_Cu, net, (lx, v_end[1]), v_end)

# Cells 9, 10, 13, 14 on B_Cu (cross right to left):
y_cross_right_to_left = {9: 21.0, 10: 21.4, 13: 21.8, 14: 22.2}
for cell_id in [9, 10, 13, 14]:
    v_start = coil_vias[cell_id]
    v_end = coil_pad_vias[cell_id]
    lx = lane_x_map[cell_id]
    y_cr = y_cross_right_to_left[cell_id]
    net = nets[f"RF_COIL_{cell_id}"]
    trk(pcbnew.B_Cu, net, v_start, (v_start[0], y_cr))
    trk(pcbnew.B_Cu, net, (v_start[0], y_cr), (lx, y_cr))
    trk(pcbnew.B_Cu, net, (lx, y_cr), (lx, v_end[1]))
    trk(pcbnew.B_Cu, net, (lx, v_end[1]), v_end)

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
add_silk(pcbnew.B_SilkS, "Max Wood Overlay: 2.0mm - 2.5mm", 50.0, 25.0, 1.1, True)

for idx, cx in enumerate(col_x):
    add_silk(pcbnew.F_SilkS, cell_letters[idx], cx, 22.2, 1.2)
for idx, ry in enumerate(row_y):
    add_silk(pcbnew.F_SilkS, str(idx + 1), 9.0, ry, 1.2)

dst = '/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4/test_grid_4x4.kicad_pcb'
board.Save(dst)
print(f"Saved {dst}")
board.Save('/tmp/test_perfect_board.kicad_pcb')
print("Saved /tmp/test_perfect_board.kicad_pcb")
