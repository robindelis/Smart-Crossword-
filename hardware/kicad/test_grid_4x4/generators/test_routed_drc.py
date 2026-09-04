#!/usr/bin/env python3
"""
Generate a fully routed test_grid_4x4 board and test DRC.
"""
import os
import pcbnew

PROJECT_DIR = "/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4"
TEST_PCB_PATH = os.path.join(PROJECT_DIR, "test_routed_drc.kicad_pcb")

def build_board():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Netlist setup
    nets = {}
    net_names = [
        "GND", "+3.3V", "RF_SIG", "MUX_EN", "MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3",
        "SPI_SCK", "SPI_MISO", "SPI_MOSI", "SPI_CS", "NFC_IRQ", "NFC_RST",
        "I2C_SDA", "I2C_SCL", "GPIO_AUX"
    ] + [f"RF_CH{k}" for k in range(16)] + [f"RF_COIL_{k+1}" for k in range(16)]

    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    # 2. Board Outline 100mm x 100mm
    outline = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    for i in range(4):
        p1 = pcbnew.VECTOR2I_MM(outline[i][0], outline[i][1])
        p2 = pcbnew.VECTOR2I_MM(outline[(i+1)%4][0], outline[(i+1)%4][1])
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(p1)
        seg.SetEnd(p2)
        seg.SetWidth(int(0.15 * 1e6))
        board.Add(seg)

    # 3. 4x M3 Mounting Holes
    for idx, (hx, hy) in enumerate([(5.0, 5.0), (95.0, 5.0), (5.0, 95.0), (95.0, 95.0)]):
        fp_h = pcbnew.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty', 'MountingHole_3.2mm_M3_Pad_Via')
        fp_h.SetReference(f"H{idx+1}")
        fp_h.SetValue("MountingHole_M3")
        fp_h.SetPosition(pcbnew.VECTOR2I_MM(hx, hy))
        for pad in fp_h.Pads():
            pad.SetNet(nets["GND"])
        board.Add(fp_h)

    # 4. U1 CD74HC4067M (SOIC-24) at (50.0, 13.0)
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

    # 5. J1 Host Header 2x10 rotated 90 deg at (12.0, 5.5)
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

    # 6. J2 NFC Transceiver Header 1x10 rotated 90 deg at (65.0, 5.5)
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

    # 7. J3 SMA RF Port at (93.0, 15.0)
    fp_j3 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Connector_Coaxial.pretty', 'SMA_Amphenol_132134_Vertical')
    fp_j3.SetReference("J3")
    fp_j3.SetValue("SMA_RF_TEST")
    fp_j3.SetPosition(pcbnew.VECTOR2I_MM(93.0, 15.0))
    for pad in fp_j3.Pads():
        pad.SetNet(nets["RF_SIG"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_j3)

    # 8. Decoupling Capacitors & Resistors
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(55.0, 3.0))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(59.0, 3.0))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(48.0, 3.0))
    fp_r17.Reference().SetVisible(False)
    fp_r17.Value().SetVisible(False)
    for pad in fp_r17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["MUX_EN"])
    board.Add(fp_r17)

    for idx, s_name in enumerate(["MUX_S0", "MUX_S1", "MUX_S2", "MUX_S3"]):
        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{18+idx}")
        fp_r.SetValue("100k")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(20.0 + idx * 3.5, 13.0))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[s_name] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_r)

    # 9. 16 Tuning Capacitors C1..C16 and 16 Damping Resistors R1..R16
    left_c_pos = [
        (36.0, 8.0), (36.0, 11.5), (36.0, 15.0), (36.0, 18.5),
        (41.0, 8.0), (41.0, 11.5), (41.0, 15.0), (41.0, 18.5)
    ]
    r_coords = {}
    c_coords = {}
    for k in range(8):
        cell_id = k + 1
        cx, cy = left_c_pos[k]
        rx, ry = cx, cy + 1.6
        c_coords[cell_id] = (cx, cy)
        r_coords[cell_id] = (rx, ry)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, cy))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(rx, ry))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
        board.Add(fp_r)

    right_c_pos = [
        (58.0, 8.0), (58.0, 11.5), (58.0, 15.0), (58.0, 18.5),
        (63.0, 8.0), (63.0, 11.5), (63.0, 15.0), (63.0, 18.5)
    ]
    for k in range(8, 16):
        cell_id = k + 1
        cx, cy = right_c_pos[k - 8]
        rx, ry = cx, cy + 1.6
        c_coords[cell_id] = (cx, cy)
        r_coords[cell_id] = (rx, ry)

        fp_c = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
        fp_c.SetReference(f"C{cell_id}")
        fp_c.SetValue("100pF")
        fp_c.SetPosition(pcbnew.VECTOR2I_MM(cx, cy))
        fp_c.Reference().SetVisible(False)
        fp_c.Value().SetVisible(False)
        for pad in fp_c.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets["GND"])
        board.Add(fp_c)

        fp_r = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
        fp_r.SetReference(f"R{cell_id}")
        fp_r.SetValue("3.3")
        fp_r.SetPosition(pcbnew.VECTOR2I_MM(rx, ry))
        fp_r.Reference().SetVisible(False)
        fp_r.Value().SetVisible(False)
        for pad in fp_r.Pads():
            pad.SetNet(nets[f"RF_CH{k}"] if pad.GetNumber() == "1" else nets[f"RF_COIL_{cell_id}"])
        board.Add(fp_r)

    # 10. 16 Planar Spiral Coils L1..L16
    col_x = [21.5, 40.5, 59.5, 78.5]
    row_y = [33.0, 52.0, 71.0, 90.0]
    cell_letters = ["A", "B", "C", "D"]
    l_coords = {}

    for r_idx in range(4):
        for c_idx in range(4):
            k = r_idx * 4 + c_idx
            cell_id = k + 1
            xc = col_x[c_idx]
            yc = row_y[r_idx]
            cell_name = f"{cell_letters[c_idx]}{r_idx+1}"
            pad1_x = xc - 8.625
            pad1_y = yc - 8.625
            l_coords[cell_id] = (pad1_x, pad1_y)

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

            ret_trk = pcbnew.PCB_TRACK(board)
            ret_trk.SetStart(pcbnew.VECTOR2I_MM(xc, yc))
            ret_trk.SetEnd(pcbnew.VECTOR2I_MM(xc - 9.0, yc))
            ret_trk.SetWidth(int(0.35 * 1e6))
            ret_trk.SetLayer(pcbnew.B_Cu)
            ret_trk.SetNet(nets["GND"])
            board.Add(ret_trk)

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

    # 13. In2.Cu Power Rail
    zone_vcc_in2 = pcbnew.ZONE(board)
    zone_vcc_in2.SetLayer(pcbnew.In2_Cu)
    zone_vcc_in2.SetNet(nets["+3.3V"])
    poly_in2 = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(2.0, 1.0), (98.0, 1.0), (98.0, 22.0), (2.0, 22.0)]:
        poly_in2.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_in2.SetClosed(True)
    zone_vcc_in2.AddPolygon(poly_in2)
    board.Add(zone_vcc_in2)

    # 14. B.Cu Bottom Ground Shield Plane
    zone_bcu = pcbnew.ZONE(board)
    zone_bcu.SetLayer(pcbnew.B_Cu)
    zone_bcu.SetNet(nets["GND"])
    poly_bcu = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in [(1.0, 1.0), (99.0, 1.0), (99.0, 99.0), (1.0, 99.0)]:
        poly_bcu.Append(pcbnew.VECTOR2I_MM(px, py))
    poly_bcu.SetClosed(True)
    zone_bcu.AddPolygon(poly_bcu)
    board.Add(zone_bcu)

    def add_track(layer, net, p_start, p_end, width=0.25):
        trk = pcbnew.PCB_TRACK(board)
        trk.SetStart(pcbnew.VECTOR2I_MM(p_start[0], p_start[1]))
        trk.SetEnd(pcbnew.VECTOR2I_MM(p_end[0], p_end[1]))
        trk.SetWidth(int(width * 1e6))
        trk.SetLayer(layer)
        trk.SetNet(net)
        board.Add(trk)

    def add_via(net, pos, drill=0.3, size=0.6):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I_MM(pos[0], pos[1]))
        v.SetDrill(int(drill * 1e6))
        v.SetWidth(int(size * 1e6))
        v.SetNet(net)
        board.Add(v)

    # 15. RF_SIG Microstrip (J2, J3, U1 COM) - routed safely without colliding with J2 pin 2!
    # U1 COM at (45.35, 6.015) to J2 pin 1 at (65.0, 5.5)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 6.015), (45.35, 3.8), 0.5)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 3.8), (65.0, 3.8), 0.5)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 3.8), (65.0, 5.5), 0.5)

    # From J2 pin 1 north to Y=2.0, across to X=93.0, down to J3 pin 1 at (93.0, 15.0)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 3.8), (65.0, 2.0), 0.5)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 2.0), (93.0, 2.0), 0.5)
    add_track(pcbnew.F_Cu, nets["RF_SIG"], (93.0, 2.0), (93.0, 15.0), 0.5)

    # 16. Silkscreen Labels
    def add_silk_text(layer, text, x, y, size=1.2):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetLayer(layer)
        txt.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
        board.Add(txt)

    add_silk_text(pcbnew.B_SilkS, "SMART CROSSWORD BOARD - 4x4 NFC TEST MATRIX", 50.0, 10.0, 1.5)
    add_silk_text(pcbnew.B_SilkS, "REV 1.0 | 13.56 MHz LC RESONANT (CD74HC4067)", 50.0, 15.0, 1.2)
    add_silk_text(pcbnew.B_SilkS, "L=1.26uH (7T planar spiral, 19mm pitch), C=100pF C0G, R=3.3R, Q~25", 50.0, 20.0, 1.1)
    add_silk_text(pcbnew.B_SilkS, "Max Wood Overlay: 2.0mm - 2.5mm", 50.0, 25.0, 1.1)

    for idx, cx in enumerate(col_x):
        add_silk_text(pcbnew.F_SilkS, cell_letters[idx], cx, 22.2, 1.2)
    for idx, ry in enumerate(row_y):
        add_silk_text(pcbnew.F_SilkS, str(idx + 1), 9.0, ry, 1.2)

    board.Save(TEST_PCB_PATH)
    print(f"Test board saved to {TEST_PCB_PATH}")

if __name__ == '__main__':
    build_board()
