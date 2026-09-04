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

# Left channels (CH0..CH7): pins at Y = 16.175 down to 7.285
u1_left_y = [16.175, 14.905, 13.635, 12.365, 11.095, 9.825, 8.555, 7.285]
for k in range(8):
    cell_id = k + 1
    y_k = u1_left_y[k]
    net_ch = nets[f"RF_CH{k}"]
    net_coil = nets[f"RF_COIL_{cell_id}"]
    # Staircase position: k=0 is at X=41.5, k=7 is at X=17.0 (step 3.5mm)
    cx = 41.5 - k * 3.5

    # C_k at (cx, y_k): Pad 1 at (cx + 0.825, y_k), Pad 2 (GND) at (cx - 0.825, y_k)
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

    # R_k at (cx - 2.8, y_k): Pad 1 at (cx - 2.8 + 0.825, y_k), Pad 2 (COIL) at (cx - 2.8 - 0.825, y_k)
    # Pad 1 of R is at cx - 1.975. Pad 2 of C (GND) is at cx - 0.825.
    # To avoid crossing Pad 2 of C: C is placed vertically!
    pass

board.Save('/tmp/test_staircase.kicad_pcb')
