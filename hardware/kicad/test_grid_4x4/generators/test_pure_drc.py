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

# 1. Outline
for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
    seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
    seg.SetWidth(int(0.15 * 1e6))
    board.Add(seg)

# 2. In1.Cu GND
zone_gnd = pcbnew.ZONE(board)
zone_gnd.SetLayer(pcbnew.In1_Cu)
zone_gnd.SetNet(nets["GND"])
poly = pcbnew.SHAPE_LINE_CHAIN()
for px, py in [(1,1), (99,1), (99,99), (1,99)]:
    poly.Append(pcbnew.VECTOR2I_MM(px, py))
poly.SetClosed(True)
zone_gnd.AddPolygon(poly)
board.Add(zone_gnd)

# 3. U1 at (50.0, 13.0)
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
via(nets["GND"], (43.0, 19.985))
trk(pcbnew.F_Cu, nets["GND"], (45.35, 19.985), (43.0, 19.985))

# 4. 16 Channels - Beautiful Staircase Bank
# Left: k=0..7, Y=16.175 down to 7.285. X goes from 41.5 down to 17.0 (step 3.5mm)
u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]
for k in range(8):
    cell_id = k + 1
    y_k = u1_left_y[k]
    cx = 41.5 - k * 3.5
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]

    # C_k at (cx, y_k): Pad 1 (RF_CHk) at (cx + 0.825), Pad 2 (GND) at (cx - 0.825)
    fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c.SetReference(f"C{cell_id}")
    fp_c.SetValue("100pF")
    fp_c.SetOrientationDegrees(180)
    fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, y_k))
    fp_c.Reference().SetVisible(False)
    fp_c.Value().SetVisible(False)
    for pad in fp_c.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c)

    # R_k at (cx - 2.5, y_k): Pad 1 (RF_CHk) at (cx - 2.5 + 0.825), Pad 2 (COIL) at (cx - 2.5 - 0.825)
    fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r.SetReference(f"R{cell_id}")
    fp_r.SetValue("3.3")
    fp_r.SetOrientationDegrees(180)
    fp_r.SetPosition(pcbnew.VECTOR2I_MM(cx - 2.5, y_k))
    fp_r.Reference().SetVisible(False)
    fp_r.Value().SetVisible(False)
    for pad in fp_r.Pads():
        pad.SetNet(net_ch if pad.GetNumber() == "1" else net_coil)
    board.Add(fp_r)

    # Connect U1 pin to C.1 on F.Cu: straight horizontal line from (45.35, y_k) to (cx + 0.825, y_k)
    trk(pcbnew.F_Cu, net_ch, (45.35, y_k), (cx + 0.825, y_k), 0.25)

    # Connect C.1 to R.1: hop over C.2 on In2_Cu
    # Via 1 at (cx + 0.825, y_k)
    via(net_ch, (cx + 0.825, y_k))
    # Via 2 at (cx - 1.675, y_k)
    via(net_ch, (cx - 1.675, y_k))
    trk(pcbnew.In2_Cu, net_ch, (cx + 0.825, y_k), (cx - 1.675, y_k), 0.25)

    # GND via for C.2 at (cx - 0.825, y_k):
    # Wait, if C.2 is at (cx - 0.825, y_k), and In2_Cu track runs at (y_k), it would hit a GND via at (cx - 0.825, y_k)!
    # BUT on In2_Cu, we can route the hop at Y = y_k + 0.8!
    # Let's check: on In2_Cu, from (cx + 0.825, y_k) -> (cx + 0.825, y_k + 0.8) -> (cx - 1.675, y_k + 0.8) -> (cx - 1.675, y_k)!
    pass

board.Save('/tmp/test_pure_drc.kicad_pcb')
