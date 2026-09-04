#!/usr/bin/env python3
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

# Outline
for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
    seg.SetWidth(int(0.15 * 1e6))
    board.Add(seg)

# In1.Cu GND
zone_gnd = pcbnew.ZONE(board)
zone_gnd.SetLayer(pcbnew.In1_Cu)
zone_gnd.SetNet(nets["GND"])
poly = pcbnew.SHAPE_LINE_CHAIN()
for px, py in [(1,1), (99,1), (99,99), (1,99)]:
    poly.Append(pcbnew.VECTOR2I_MM(px, py))
poly.SetClosed(True)
zone_gnd.AddPolygon(poly)
board.Add(zone_gnd)

# U1 at (50.0, 13.0)
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

# U1 GND pin 12 at (45.35, 19.985)
via(nets["GND"], (44.0, 19.985))
trk(pcbnew.F_Cu, nets["GND"], (45.35, 19.985), (44.0, 19.985))

# Fanout Y coordinates with pitch 2.3 mm:
fanned_left_y = [20.5, 18.2, 15.9, 13.6, 11.3, 9.0, 6.7, 4.4]
u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]

fanned_right_y = [4.4, 6.7, 9.0, 11.3, 13.6, 15.9, 18.2, 20.5]
u1_right_y = [7.285, 8.555, 9.825, 11.095, 12.365, 13.635, 14.905, 16.175]

# Left side
for k in range(8):
    cell_id = k + 1
    y_u = u1_left_y[k]
    y_f = fanned_left_y[k]
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # C_k at (36.0, y_f): Pad 1 at (36.0 + 0.825, y_f), Pad 2 (GND) at (36.0 - 0.825, y_f)
    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetOrientationDegrees(180)
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(36.0, y_f))
    fp_c.Reference().SetVisible(False)
    fp_c.Value().SetVisible(False)
    for pad in fp_c.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c)

    # R_k at (30.0, y_f): Pad 1 at (30.0 + 0.825, y_f), Pad 2 (COIL) at (30.0 - 0.825, y_f)
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetOrientationDegrees(180)
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(30.0, y_f))
    fp_r.Reference().SetVisible(False)
    fp_r.Value().SetVisible(False)
    for pad in fp_r.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
    board.Add(fp_r)

    # Fanout from U1 pin (45.35, y_u) to (42.0, y_f) to C.1 (36.825, y_f)
    trk(pcbnew.F_Cu, net_ch, (45.35, y_u), (42.0, y_f), 0.25)
    trk(pcbnew.F_Cu, net_ch, (42.0, y_f), (36.825, y_f), 0.25)

    # Connect C.1 (36.825, y_f) to R.1 (30.825, y_f) on In2_Cu:
    # Drop via at (38.0, y_f), route on In2_Cu to (32.0, y_f), pop up at (32.0, y_f) to R.1
    # Notice: In2_Cu route is at the EXACT same Y=y_f, so it never crosses any other channel!
    via(net_ch, (38.0, y_f))
    trk(pcbnew.F_Cu, net_ch, (36.825, y_f), (38.0, y_f), 0.25)
    via(net_ch, (32.0, y_f))
    trk(pcbnew.In2_Cu, net_ch, (38.0, y_f), (32.0, y_f), 0.25)
    trk(pcbnew.F_Cu, net_ch, (32.0, y_f), (30.825, y_f), 0.25)

    # GND via for C.2 at (34.0, y_f)
    via(nets["GND"], (34.0, y_f))
    trk(pcbnew.F_Cu, nets["GND"], (35.175, y_f), (34.0, y_f), 0.25)

    # Signal via for R.2 at (28.0, y_f)
    via(net_coil, (28.0, y_f))
    trk(pcbnew.F_Cu, net_coil, (29.175, y_f), (28.0, y_f), 0.25)

# Right side
for k in range(8, 16):
    cell_id = k + 1
    y_u = u1_right_y[k - 8]
    y_f = fanned_right_y[k - 8]
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # C_k at (64.0, y_f): Pad 1 at (63.175, y_f), Pad 2 (GND) at (64.825, y_f)
    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(64.0, y_f))
    fp_c.Reference().SetVisible(False)
    fp_c.Value().SetVisible(False)
    for pad in fp_c.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c)

    # R_k at (70.0, y_f): Pad 1 at (69.175, y_f), Pad 2 (COIL) at (70.825, y_f)
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(70.0, y_f))
    fp_r.Reference().SetVisible(False)
    fp_r.Value().SetVisible(False)
    for pad in fp_r.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
    board.Add(fp_r)

    # Fanout from U1 pin (54.65, y_u) to (58.0, y_f) to C.1 (63.175, y_f)
    trk(pcbnew.F_Cu, net_ch, (54.65, y_u), (58.0, y_f), 0.25)
    trk(pcbnew.F_Cu, net_ch, (58.0, y_f), (63.175, y_f), 0.25)

    # Connect C.1 to R.1 on In2_Cu:
    via(net_ch, (62.0, y_f))
    trk(pcbnew.F_Cu, net_ch, (63.175, y_f), (62.0, y_f), 0.25)
    via(net_ch, (68.0, y_f))
    trk(pcbnew.In2_Cu, net_ch, (62.0, y_f), (68.0, y_f), 0.25)
    trk(pcbnew.F_Cu, net_ch, (68.0, y_f), (69.175, y_f), 0.25)

    # GND via for C.2 at (66.0, y_f)
    via(nets["GND"], (66.0, y_f))
    trk(pcbnew.F_Cu, nets["GND"], (64.825, y_f), (66.0, y_f), 0.25)

    # Signal via for R.2 at (72.0, y_f)
    via(net_coil, (72.0, y_f))
    trk(pcbnew.F_Cu, net_coil, (70.825, y_f), (72.0, y_f), 0.25)

board.Save('/tmp/test_exact_clearance.kicad_pcb')
print("Saved /tmp/test_exact_clearance.kicad_pcb")
