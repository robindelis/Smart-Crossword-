#!/usr/bin/env python3
"""
test_pure_routing.py - Find the 0-violation routing for J1->J2 pass-throughs and control lines.
"""
import pcbnew
import subprocess
import json

def test():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)

    net_names = ["GND", "+3.3V", "RF_SIG", "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
                 "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
                 "I2C_SDA", "I2C_SCL", "GPIO_AUX"]
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

    def via(net, pos, size=0.6, drill=0.3):
        v = pcbnew.PCB_VIA(b)
        v.SetNet(net)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetWidth(int(size * 1e6))
        v.SetDrill(int(drill * 1e6))
        b.Add(v)

    def pad_pos(fp, pad_num):
        pad = fp.FindPadByNumber(str(pad_num))
        pos = pad.GetPosition()
        return (pos.x / 1e6, pos.y / 1e6)

    # Outline
    corners = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(b)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(corners[i][0], corners[i][1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(corners[(i+1)%4][0], corners[(i+1)%4][1]))
        seg.SetWidth(int(0.15 * 1e6))
        b.Add(seg)

    # J1
    fp_j1 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_2x10_P2.54mm_Vertical')
    fp_j1.SetReference("J1")
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
    b.Add(fp_j1)

    # J2
    fp_j2 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x10_P2.54mm_Vertical')
    fp_j2.SetReference("J2")
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
    b.Add(fp_j2)

    # Let's test routing the 6 pass-through signals:
    # We want:
    # 1. SCK (13.54, 2.46) -> J2.5 (76.16, 4.0)
    # 2. MISO (16.08, 2.46) -> J2.6 (78.70, 4.0)
    # 3. MOSI (18.62, 2.46) -> J2.7 (81.24, 4.0)
    # 4. CS (21.16, 2.46) -> J2.8 (83.78, 4.0)
    # 5. IRQ (23.70, 2.46) -> J2.9 (86.32, 4.0)
    # 6. RST (26.24, 2.46) -> J2.10 (88.86, 4.0)

    # Route SCK on In2.Cu:
    p4 = pad_pos(fp_j1, 4)
    p_j2_5 = pad_pos(fp_j2, 5)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], p4, (p4[0], 0.75), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], (p4[0], 0.75), (p_j2_5[0], 0.75), 0.20)
    trk(pcbnew.In2_Cu, nets["SPI_SCK"], (p_j2_5[0], 0.75), p_j2_5, 0.20)

    # Route MISO on B.Cu:
    p6 = pad_pos(fp_j1, 6)
    p_j2_6 = pad_pos(fp_j2, 6)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], p6, (p6[0], 0.75), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], (p6[0], 0.75), (p_j2_6[0], 0.75), 0.20)
    trk(pcbnew.B_Cu, nets["SPI_MISO"], (p_j2_6[0], 0.75), p_j2_6, 0.20)

    # Route MOSI on In2.Cu (Y = 1.15):
    # To drop into J2.7 without crossing SCK at J2:
    # Notice: SCK drops at 76.16!
    # Where does MOSI drop? MOSI drops at 81.24!
    # 81.24 is EAST of 76.16!
    # When SCK drops at 76.16 from Y = 0.75 to 4.0:
    # If MOSI is at Y = 1.15, SCK CROSSES MOSI!
    # BUT if SCK was on the INNER track (Y = 1.15), and MOSI was on the OUTER track (Y = 0.75):
    # Then SCK drops at 76.16 from 1.15 to 4.0 (NEVER TOUCHES 0.75!).
    # And MOSI drops at 81.24 from 0.75 to 4.0!
    # Does SCK exist at 81.24? NO! SCK ended at 76.16!
    # So MOSI drops at 81.24 with ZERO crossings!
    # Now at J1:
    # SCK is at 13.54. It goes up to 1.15.
    # MOSI is at 18.62. It goes up to 0.75.
    # At X = 18.62, does SCK exist at Y = 1.15?
    # YES! SCK runs from 13.54 to 76.16 at Y = 1.15!
    # So MOSI going from 2.46 to 0.75 crosses SCK at (18.62, 1.15)!
    # BUT WHAT IF MOSI JOGS TO THE RIGHT OR USE B.Cu?
    # At J1, MOSI can go to 0.75 on B.Cu!
    # Then via to In2.Cu at X = 35.0 mm!
    # Let's test that!

    test_file = "/tmp/test_pure.kicad_pcb"
    b.Save(test_file)
    subprocess.run(f"kicad-cli pcb drc --refill-zones --format json -o /tmp/drc_pure.json {test_file}", shell=True)
    d = json.load(open("/tmp/drc_pure.json"))
    v = d.get('violations', [])
    print(f"Violations: {len(v)}")
    for x in v:
        print(x['type'], x.get('description'))

if __name__ == '__main__':
    test()
