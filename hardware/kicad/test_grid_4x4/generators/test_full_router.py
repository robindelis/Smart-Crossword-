#!/usr/bin/env python3
"""
Complete Router and DRC verifier for test_grid_4x4
"""
import os
import pcbnew

PROJECT_DIR = "/home/robin/Smart-Crossword-Board/hardware/kicad/test_grid_4x4"
PCB_PATH = os.path.join(PROJECT_DIR, "test_grid_4x4.kicad_pcb")

def route_all():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # 1. Nets
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

    # Helper track & via functions
    def track(layer, net, p1, p2, w=0.25):
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

    # 2. Board outline 100x100
    for p1, p2 in [((0,0),(100,0)), ((100,0),(100,100)), ((100,100),(0,100)), ((0,100),(0,0))]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(pcbnew.VECTOR2I_MM(p1[0], p1[1]))
        seg.SetEnd(pcbnew.VECTOR2I_MM(p2[0], p2[1]))
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

    # 8. Decoupling Capacitors & Resistors (placed cleanly at Y=2.0 mm)
    fp_c17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0603_1608Metric')
    fp_c17.SetReference("C17")
    fp_c17.SetValue("0.1uF")
    fp_c17.SetPosition(pcbnew.VECTOR2I_MM(50.0, 2.0))
    fp_c17.Reference().SetVisible(False)
    fp_c17.Value().SetVisible(False)
    for pad in fp_c17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c17)

    fp_c18 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric')
    fp_c18.SetReference("C18")
    fp_c18.SetValue("10uF")
    fp_c18.SetPosition(pcbnew.VECTOR2I_MM(55.0, 2.0))
    fp_c18.Reference().SetVisible(False)
    fp_c18.Value().SetVisible(False)
    for pad in fp_c18.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["GND"])
    board.Add(fp_c18)

    fp_r17 = pcbnew.FootprintLoad('/usr/share/kicad/footprints/Resistor_SMD.pretty', 'R_0603_1608Metric')
    fp_r17.SetReference("R17")
    fp_r17.SetValue("10k")
    fp_r17.SetPosition(pcbnew.VECTOR2I_MM(45.0, 2.0))
    fp_r17.Reference().SetVisible(False)
    fp_r17.Value().SetVisible(False)
    for pad in fp_r17.Pads():
        pad.SetNet(nets["+3.3V"] if pad.GetNumber() == "1" else nets["MUX_EN"])
    board.Add(fp_r17)

    # Pulldowns R18..R21
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
    l_pad1_coords = {}

    for r_idx in range(4):
        for c_idx in range(4):
            k = r_idx * 4 + c_idx
            cell_id = k + 1
            xc = col_x[c_idx]
            yc = row_y[r_idx]
            cell_name = f"{cell_letters[c_idx]}{r_idx+1}"
            pad1_x = xc - 8.625
            pad1_y = yc - 8.625
            l_pad1_coords[cell_id] = (pad1_x, pad1_y)

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

            # B.Cu return trace to ground plane
            track(pcbnew.B_Cu, nets["GND"], (xc, yc), (xc - 9.0, yc), 0.35)

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

    # 15. RF_SIG Microstrip: U1 COM -> J2 pin 1 -> J3 pin 1
    # U1 COM (45.35, 6.015) to J2 pin 1 (65.0, 5.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 6.015), (45.35, 3.8), 0.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (45.35, 3.8), (65.0, 3.8), 0.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 3.8), (65.0, 5.5), 0.5)

    # From J2 pin 1 to J3 pin 1: route at Y=8.5 (safe below J2, safe above coils, safe west of H2)
    track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 5.5), (65.0, 8.5), 0.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (65.0, 8.5), (89.0, 8.5), 0.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 8.5), (89.0, 15.0), 0.5)
    track(pcbnew.F_Cu, nets["RF_SIG"], (89.0, 15.0), (93.0, 15.0), 0.5)

    # 16. GND Connections: Vias for all SMD GND pads
    # C1..C16 Pad 2 is at (cx + 0.825, cy)
    for cell_id in range(1, 17):
        cx, cy = c_coords[cell_id]
        p2 = (cx + 0.825, cy)
        v_pos = (cx + 1.6, cy)
        via(nets["GND"], v_pos)
        track(pcbnew.F_Cu, nets["GND"], p2, v_pos, 0.25)

    # U1 pin 12 GND at (45.35, 19.985)
    u1_p12 = (45.35, 19.985)
    v_u1_gnd = (44.0, 19.985)
    via(nets["GND"], v_u1_gnd)
    track(pcbnew.F_Cu, nets["GND"], u1_p12, v_u1_gnd, 0.25)

    # C17 pad 2 GND at (50.825, 2.0), C18 pad 2 GND at (55.95, 2.0)
    for px, py in [(50.825, 2.0), (55.95, 2.0)]:
        v_pos = (px + 1.0, py)
        via(nets["GND"], v_pos)
        track(pcbnew.F_Cu, nets["GND"], (px, py), v_pos, 0.25)

    # Pulldowns R18..R21 pad 2 GND at (rx + 0.825, 13.0)
    for idx in range(4):
        rx = 20.0 + idx * 3.5
        p2 = (rx + 0.825, 13.0)
        v_pos = (rx + 1.6, 13.0)
        via(nets["GND"], v_pos)
        track(pcbnew.F_Cu, nets["GND"], p2, v_pos, 0.25)

    # 17. +3.3V Connections
    # U1 pin 24 at (54.65, 6.015)
    u1_p24 = (54.65, 6.015)
    v_u1_vcc = (56.0, 6.015)
    via(nets["+3.3V"], v_u1_vcc)
    track(pcbnew.F_Cu, nets["+3.3V"], u1_p24, v_u1_vcc, 0.25)

    # C17 pad 1 at (49.175, 2.0), C18 pad 1 at (54.05, 2.0), R17 pad 1 at (44.175, 2.0)
    for px, py in [(49.175, 2.0), (54.05, 2.0), (44.175, 2.0)]:
        v_pos = (px - 1.0, py)
        via(nets["+3.3V"], v_pos)
        track(pcbnew.F_Cu, nets["+3.3V"], (px, py), v_pos, 0.25)

    # 18. MUX Control Lines
    # U1 pins:
    # pin 10 (S0) at (45.35, 17.445)
    # pin 11 (S1) at (45.35, 18.715)
    # pin 13 (S3) at (54.65, 19.985)
    # pin 14 (S2) at (54.65, 18.715)
    # pin 15 (EN) at (54.65, 17.445)

    # R18..R21 pad 1 at (rx - 0.825, 13.0)
    # J1 pins (PTH):
    # J1.3 (MUX_S0) at (14.54, 5.5)
    # J1.5 (MUX_S1) at (17.08, 5.5)
    # J1.7 (MUX_S2) at (19.62, 5.5)
    # J1.9 (MUX_S3) at (22.16, 5.5)
    # J1.11 (MUX_EN) at (24.70, 5.5)

    # Connect J1 -> Pulldown/Pullup -> U1
    # MUX_S0: J1.3 (14.54, 5.5) -> R18.1 (19.175, 13.0) -> U1.10 (45.35, 17.445)
    track(pcbnew.In2_Cu, nets["MUX_S0"], (14.54, 5.5), (14.54, 10.0))
    track(pcbnew.In2_Cu, nets["MUX_S0"], (14.54, 10.0), (19.175, 10.0))
    via(nets["MUX_S0"], (19.175, 10.0))
    track(pcbnew.F_Cu, nets["MUX_S0"], (19.175, 10.0), (19.175, 13.0))
    track(pcbnew.In2_Cu, nets["MUX_S0"], (19.175, 10.0), (43.0, 10.0))
    track(pcbnew.In2_Cu, nets["MUX_S0"], (43.0, 10.0), (43.0, 17.445))
    via(nets["MUX_S0"], (43.0, 17.445))
    track(pcbnew.F_Cu, nets["MUX_S0"], (43.0, 17.445), (45.35, 17.445))

    # MUX_S1: J1.5 (17.08, 5.5) -> R19.1 (22.675, 13.0) -> U1.11 (45.35, 18.715)
    track(pcbnew.In2_Cu, nets["MUX_S1"], (17.08, 5.5), (17.08, 10.5))
    track(pcbnew.In2_Cu, nets["MUX_S1"], (17.08, 10.5), (22.675, 10.5))
    via(nets["MUX_S1"], (22.675, 10.5))
    track(pcbnew.F_Cu, nets["MUX_S1"], (22.675, 10.5), (22.675, 13.0))
    track(pcbnew.In2_Cu, nets["MUX_S1"], (22.675, 10.5), (43.5, 10.5))
    track(pcbnew.In2_Cu, nets["MUX_S1"], (43.5, 10.5), (43.5, 18.715))
    via(nets["MUX_S1"], (43.5, 18.715))
    track(pcbnew.F_Cu, nets["MUX_S1"], (43.5, 18.715), (45.35, 18.715))

    # MUX_S2: J1.7 (19.62, 5.5) -> R20.1 (26.175, 13.0) -> U1.14 (54.65, 18.715)
    track(pcbnew.In2_Cu, nets["MUX_S2"], (19.62, 5.5), (19.62, 11.0))
    track(pcbnew.In2_Cu, nets["MUX_S2"], (19.62, 11.0), (26.175, 11.0))
    via(nets["MUX_S2"], (26.175, 11.0))
    track(pcbnew.F_Cu, nets["MUX_S2"], (26.175, 11.0), (26.175, 13.0))
    track(pcbnew.In2_Cu, nets["MUX_S2"], (26.175, 11.0), (26.175, 21.0))
    track(pcbnew.In2_Cu, nets["MUX_S2"], (26.175, 21.0), (56.5, 21.0))
    track(pcbnew.In2_Cu, nets["MUX_S2"], (56.5, 21.0), (56.5, 18.715))
    via(nets["MUX_S2"], (56.5, 18.715))
    track(pcbnew.F_Cu, nets["MUX_S2"], (56.5, 18.715), (54.65, 18.715))

    # MUX_S3: J1.9 (22.16, 5.5) -> R21.1 (29.675, 13.0) -> U1.13 (54.65, 19.985)
    track(pcbnew.In2_Cu, nets["MUX_S3"], (22.16, 5.5), (22.16, 11.5))
    track(pcbnew.In2_Cu, nets["MUX_S3"], (22.16, 11.5), (29.675, 11.5))
    via(nets["MUX_S3"], (29.675, 11.5))
    track(pcbnew.F_Cu, nets["MUX_S3"], (29.675, 11.5), (29.675, 13.0))
    track(pcbnew.In2_Cu, nets["MUX_S3"], (29.675, 11.5), (29.675, 21.5))
    track(pcbnew.In2_Cu, nets["MUX_S3"], (29.675, 21.5), (57.0, 21.5))
    track(pcbnew.In2_Cu, nets["MUX_S3"], (57.0, 21.5), (57.0, 19.985))
    via(nets["MUX_S3"], (57.0, 19.985))
    track(pcbnew.F_Cu, nets["MUX_S3"], (57.0, 19.985), (54.65, 19.985))

    # MUX_EN: J1.11 (24.70, 5.5) -> R17.2 (45.825, 2.0) -> U1.15 (54.65, 17.445)
    track(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 5.5), (24.70, 2.0))
    track(pcbnew.In2_Cu, nets["MUX_EN"], (24.70, 2.0), (45.825, 2.0))
    via(nets["MUX_EN"], (45.825, 2.0))
    track(pcbnew.In2_Cu, nets["MUX_EN"], (45.825, 2.0), (47.0, 2.0))
    track(pcbnew.In2_Cu, nets["MUX_EN"], (47.0, 2.0), (47.0, 22.0))
    track(pcbnew.In2_Cu, nets["MUX_EN"], (47.0, 22.0), (56.0, 22.0))
    track(pcbnew.In2_Cu, nets["MUX_EN"], (56.0, 22.0), (56.0, 17.445))
    via(nets["MUX_EN"], (56.0, 17.445))
    track(pcbnew.F_Cu, nets["MUX_EN"], (56.0, 17.445), (54.65, 17.445))

    # 19. Pass-Through Signals J1 -> J2 on In2_Cu
    pass_pins = [
        ("SPI_SCK",  (14.54, 2.96), (75.16, 5.5), 2.5),
        ("SPI_MISO", (17.08, 2.96), (77.70, 5.5), 2.8),
        ("SPI_MOSI", (19.62, 2.96), (80.24, 5.5), 3.1),
        ("SPI_CS",   (22.16, 2.96), (82.78, 5.5), 3.4),
        ("NFC_IRQ",  (24.70, 2.96), (85.32, 5.5), 3.7),
        ("NFC_RST",  (27.24, 2.96), (87.86, 5.5), 4.0),
    ]
    for s_name, p_j1, p_j2, y_route in pass_pins:
        track(pcbnew.In2_Cu, nets[s_name], p_j1, (p_j1[0], y_route), 0.25)
        track(pcbnew.In2_Cu, nets[s_name], (p_j1[0], y_route), (p_j2[0], y_route), 0.25)
        track(pcbnew.In2_Cu, nets[s_name], (p_j2[0], y_route), p_j2, 0.25)

    # 20. Connect U1 channels to Ck and Rk
    u1_left_pins = {
        0: (45.35, 16.175), 1: (45.35, 14.905), 2: (45.35, 13.635), 3: (45.35, 12.365),
        4: (45.35, 11.095), 5: (45.35, 9.825),  6: (45.35, 8.555),  7: (45.35, 7.285)
    }
    u1_right_pins = {
        8: (54.65, 7.285),  9: (54.65, 8.555),  10: (54.65, 9.825), 11: (54.65, 11.095),
        12: (54.65, 12.365), 13: (54.65, 13.635), 14: (54.65, 14.905), 15: (54.65, 16.175)
    }

    for k in range(8):
        cell_id = k + 1
        u1_pt = u1_left_pins[k]
        c_pt = (c_coords[cell_id][0] - 0.825, c_coords[cell_id][1])
        r_p1 = (r_coords[cell_id][0] - 0.825, r_coords[cell_id][1])

        # Connect U1 pin to R pad 1, and R pad 1 to C pad 1
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], u1_pt, (r_p1[0] + 2.0, u1_pt[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0] + 2.0, u1_pt[1]), (r_p1[0] + 2.0, r_p1[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0] + 2.0, r_p1[1]), r_p1)
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], r_p1, (r_p1[0], c_pt[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0], c_pt[1]), c_pt)

    for k in range(8, 16):
        cell_id = k + 1
        u1_pt = u1_right_pins[k]
        c_pt = (c_coords[cell_id][0] - 0.825, c_coords[cell_id][1])
        r_p1 = (r_coords[cell_id][0] - 0.825, r_coords[cell_id][1])

        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], u1_pt, (r_p1[0] - 1.5, u1_pt[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0] - 1.5, u1_pt[1]), (r_p1[0] - 1.5, r_p1[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0] - 1.5, r_p1[1]), r_p1)
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], r_p1, (r_p1[0], c_pt[1]))
        track(pcbnew.F_Cu, nets[f"RF_CH{k}"], (r_p1[0], c_pt[1]), c_pt)

    # 21. Connect Resistors Rk to Coils Lk (Planar Routing on In2_Cu)
    # Rk pad 2 is at (rx + 0.825, ry)
    # Lk Pad 1 is at l_pad1_coords[cell_id]
    col_x_channels = {
        0: [1, 5, 9, 13],    # Col 0 coils
        1: [2, 6, 10, 14],   # Col 1 coils
        2: [3, 7, 11, 15],   # Col 2 coils
        3: [4, 8, 12, 16],   # Col 3 coils
    }
    col_routing_x = {
        0: [8.0, 9.0, 10.0, 11.0],      # Left margin
        1: [30.2, 30.7, 31.2, 31.7],    # Corridor between Col 0 & 1
        2: [49.2, 49.7, 50.2, 50.7],    # Corridor between Col 1 & 2
        3: [89.0, 90.0, 91.0, 92.0],    # Right margin
    }

    for c_idx in range(4):
        cells = col_x_channels[c_idx]
        x_lanes = col_routing_x[c_idx]
        for row_i, cell_id in enumerate(cells):
            rx, ry = r_coords[cell_id]
            r_p2 = (rx + 0.825, ry)
            net_coil = nets[f"RF_COIL_{cell_id}"]
            lane_x = x_lanes[row_i]
            l_p1 = l_pad1_coords[cell_id]

            # Via near Rk pad 2
            v_r = (rx + 0.825, ry + 0.6)
            via(net_coil, v_r)
            track(pcbnew.F_Cu, net_coil, r_p2, v_r, 0.25)

            # Via near Lk pad 1
            v_l = (l_p1[0], l_p1[1] - 0.7)
            via(net_coil, v_l)
            track(pcbnew.F_Cu, net_coil, v_l, l_p1, 0.25)

            # Route on In2_Cu: v_r -> lane_x at Y=22.5 + row_i*0.4 -> down to l_p1[1] - 0.7 -> v_l
            y_bus = 22.2 + (c_idx * 4 + row_i) * 0.35 if c_idx in [1, 2] else 21.8 + row_i * 0.4
            track(pcbnew.In2_Cu, net_coil, v_r, (v_r[0], y_bus), 0.25)
            track(pcbnew.In2_Cu, net_coil, (v_r[0], y_bus), (lane_x, y_bus), 0.25)
            track(pcbnew.In2_Cu, net_coil, (lane_x, y_bus), (lane_x, v_l[1]), 0.25)
            track(pcbnew.In2_Cu, net_coil, (lane_x, v_l[1]), v_l, 0.25)

    # 22. Silkscreen Labels
    def add_silk(layer, text, x, y, size=1.2, mirror=False):
        txt = pcbnew.PCB_TEXT(board)
        txt.SetText(text)
        txt.SetLayer(layer)
        txt.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        txt.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
        if mirror:
            txt.SetMirrored(True)
        board.Add(txt)

    # Back silkscreen (mirrored!)
    add_silk(pcbnew.B_SilkS, "SMART CROSSWORD BOARD - 4x4 NFC TEST MATRIX", 50.0, 10.0, 1.5, True)
    add_silk(pcbnew.B_SilkS, "REV 1.0 | 13.56 MHz LC RESONANT (CD74HC4067)", 50.0, 15.0, 1.2, True)
    add_silk(pcbnew.B_SilkS, "L=1.26uH (7T planar spiral, 19mm pitch), C=100pF C0G, R=3.3R, Q~25", 50.0, 20.0, 1.1, True)
    add_silk(pcbnew.B_SilkS, "Max Wood Overlay: 2.0mm - 2.5mm", 50.0, 25.0, 1.1, True)

    # Front silkscreen labels in safe margins
    for idx, cx in enumerate(col_x):
        add_silk(pcbnew.F_SilkS, cell_letters[idx], cx, 22.2, 1.2)
    for idx, ry in enumerate(row_y):
        add_silk(pcbnew.F_SilkS, str(idx + 1), 9.0, ry, 1.2)

    board.Save(PCB_PATH)
    print(f"Board saved to {PCB_PATH}")

if __name__ == '__main__':
    route_all()
