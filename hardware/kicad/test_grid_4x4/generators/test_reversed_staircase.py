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

# U1 GND pin 12
via(nets["GND"], (43.0, 19.985))
trk(pcbnew.F_Cu, nets["GND"], (45.35, 19.985), (43.0, 19.985))

# Left channels (k=0..7):
# k=7 (Y=7.285) is closest to U1 at X=41.5
# k=0 (Y=16.175) is furthest at X=17.0
u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]
for k in range(8):
    cell_id = k + 1
    y_k = u1_left_y[k]
    # k=7 -> cx = 41.5; k=0 -> cx = 17.0
    cx = 17.0 + k * 3.5
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # R_k at (cx, y_k): Pad 1 (RF_CHk) at cx+0.825, Pad 2 (COIL) at cx-0.825
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

    # C_k at (cx, y_k - 1.8): Pad 1 (RF_CHk) at cx+0.825, Pad 2 (GND) at cx-0.825
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

    # Vertical track connecting R.1 and C.1 at X = cx + 0.825
    trk(pcbnew.F_Cu, net_ch, (cx + 0.825, y_k), (cx + 0.825, y_k - 1.8), 0.25)

    # Horizontal track from U1 pin (45.35, y_k) to (cx + 0.825, y_k)
    trk(pcbnew.F_Cu, net_ch, (45.35, y_k), (cx + 0.825, y_k), 0.25)

    # GND via for C.2 at (cx - 1.8, y_k - 1.8)
    via(nets["GND"], (cx - 1.8, y_k - 1.8))
    trk(pcbnew.F_Cu, nets["GND"], (cx - 0.825, y_k - 1.8), (cx - 1.8, y_k - 1.8), 0.25)

    # Signal via for R.2 at (cx - 1.8, y_k)
    via(net_coil, (cx - 1.8, y_k))
    trk(pcbnew.F_Cu, net_coil, (cx - 0.825, y_k), (cx - 1.8, y_k), 0.25)

# Right channels (k=8..15):
# k=8 (Y=7.285) is closest to U1 at X=58.5
# k=15 (Y=16.175) is furthest at X=83.0
u1_right_y = [7.285, 8.555, 9.825, 11.095, 12.365, 13.635, 14.905, 16.175]
for k in range(8, 16):
    cell_id = k + 1
    y_k = u1_right_y[k - 8]
    # (k-8)=0 -> cx = 58.5; (k-8)=7 -> cx = 83.0
    cx = 58.5 + (k - 8) * 3.5
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # R_k at (cx, y_k): Pad 1 (RF_CHk) at cx-0.825, Pad 2 (COIL) at cx+0.825
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k))
    fp_r.Reference().SetVisible(False)
    fp_r.Value().SetVisible(False)
    for pad in fp_r.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
    board.Add(fp_r)

    # C_k at (cx, y_k - 1.8): Pad 1 (RF_CHk) at cx-0.825, Pad 2 (GND) at cx+0.825
    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k - 1.8))
    fp_c.Reference().SetVisible(False)
    fp_c.Value().SetVisible(False)
    for pad in fp_c.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c)

    # Vertical track connecting R.1 and C.1 at X = cx - 0.825
    trk(pcbnew.F_Cu, net_ch, (cx - 0.825, y_k), (cx - 0.825, y_k - 1.8), 0.25)

    # Horizontal track from U1 pin (54.65, y_k) to (cx - 0.825, y_k)
    trk(pcbnew.F_Cu, net_ch, (54.65, y_k), (cx - 0.825, y_k), 0.25)

    # GND via for C.2 at (cx + 1.8, y_k - 1.8)
    via(nets["GND"], (cx + 1.8, y_k - 1.8))
    trk(pcbnew.F_Cu, nets["GND"], (cx + 0.825, y_k - 1.8), (cx + 1.8, y_k - 1.8), 0.25)

    # Signal via for R.2 at (cx + 1.8, y_k)
    via(net_coil, (cx + 1.8, y_k))
    trk(pcbnew.F_Cu, net_coil, (cx + 0.825, y_k), (cx + 1.8, y_k), 0.25)

board.Save('/tmp/test_reversed_staircase.kicad_pcb')
print("Saved /tmp/test_reversed_staircase.kicad_pcb")
