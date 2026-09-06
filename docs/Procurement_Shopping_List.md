# Procurement & Shopping List

This master procurement document lists all validated component references and procurement items required for the Smart Crossword Board project, split into the **Prototype (4x4) Bench Test** and the **Full Commercial (15x15) Board**.

All online store links have been verified live per **Invariant FAIL-010** using [`scripts/verify_ecommerce_links.py`](file:///home/robin/Smart-Crossword-Board/scripts/verify_ecommerce_links.py).

---

## 1. Prototype (4x4) Benchtop Shopping List

### Interactive Dynamic Spreadsheet (DataLoom)
![[Prototype_4x4_Shopping_List.loom]]

### Quick Reference Table
| Item / Component | Top Candidate Pack Details | Bench Cost | Pack Price | Store Link |
| :--- | :--- | :--- | :--- | :--- |
| **Letter Tiles (16 needed)** | 200 Pcs Wooden Scrabble Tiles | **€6.99** | €6.99 | [Amazon BE (`B0GH7LXL2K`)](https://www.amazon.com.be/dp/B0GH7LXL2K) |
| **13.56 MHz NFC Tags (16 needed)** | 60 Pcs NTAG213 Stickers 25mm | **€6.99** | €6.99 | [Amazon BE (`B0HC2ZKQLQ`)](https://www.amazon.com.be/dp/B0HC2ZKQLQ) |
| **NFC Reader Module (1 needed)** | NXP PN5180 High-Power Breakout | **€11.82** | €11.82 | [Amazon BE (`B0HDTXDNJY`)](https://www.amazon.com.be/dp/B0HDTXDNJY) |
| **Host Microcontroller (1 needed)** | ESP32-S3 DevKit N16R8 *(3-pack @ €20.98)* | **€6.99** | €20.98 | [Amazon BE (`B0GXF14RRM`)](https://www.amazon.com.be/dp/B0GXF14RRM) |
| **16-Ch Multiplexer (1 needed)** | DollaTek CD74HC4067 Breakout *(5-pack @ €5.99)* | **€1.20** | €5.99 | [Amazon BE (`B07PPKRVGW`)](https://www.amazon.com.be/dp/B07PPKRVGW) |
| **Rotating Turntable (1 needed)** | QWORK Square Bearing 71x71mm *(4-pack @ €6.98)* | **€1.75** | €6.98 | [Amazon BE (`B0B3X7R961`)](https://www.amazon.com.be/dp/B0B3X7R961) |
| **Color Display Screen (1 needed)** | 3.5" TFT SPI 480x320 with Touch | **€17.91** | €17.91 | [Amazon BE (`B0BZXX1QFM`)](https://www.amazon.com.be/dp/B0BZXX1QFM) |
| **Audio Referee DAC Amp (1 needed)** | MAX98357A I2S 3W Amp *(3-pack @ €9.09)* | **€3.03** | €9.09 | [Amazon BE (`B0F21T7Q3P`)](https://www.amazon.com.be/dp/B0F21T7Q3P) |
| **Mini Speaker 40mm (1 needed)** | RELAND SUN 3W 4Ω Speakers *(2-pack @ €4.70)* | **€2.35** | €4.70 | [Amazon BE (`B09YQ1S988`)](https://www.amazon.com.be/dp/B09YQ1S988) |
| **Hardware Fasteners Kit** | 440 Pcs M3 Button Head Screws & Nuts Box | **€7.88** | €7.88 | [Amazon BE (`B0B3MGZ7T2`)](https://www.amazon.com.be/dp/B0B3MGZ7T2) |
| **Anti-Skid Bumper Feet (4 needed)** | Silicone Bumper Feet 10mm *(12-pack @ €8.99)* | **€3.00** | €8.99 | [Amazon BE (`B08GKP4311`)](https://www.amazon.com.be/dp/B08GKP4311) |
| **3D Print Chassis & Grid (1 set)** | PLA / PETG Spool Allocation (~120g filament) | **€2.40** | €19.99 | [3D CAD Models](file:///home/robin/Smart-Crossword-Board/hardware/cad/output/) |
| **TOTAL PROTOTYPE BENCH COST** | **All components to build 1 bench unit** | **€72.31** | **€128.31** | *(Checkout total provides ample spares)* |

<!-- TBLFM: @>$3=sum(@I..@-1) -->

> 🔍 **Multi-Candidate Research**: See [[Component_Candidate_Comparison|Component Candidate Comparison]] for detailed candidate comparisons across all 9 categories (tiles, NFC tags, reader modules, MCUs, multiplexers, turntables, displays, audio DAC/speakers, and fasteners) with verified live links and trade-off verdicts.

---

## 2. Full Game (15x15) Commercial Production Sourcing

### Interactive Dynamic Spreadsheet (DataLoom)
![[Production_15x15_Sourcing_List.loom]]

### Quick Reference Table
| Item / Component | Supplier & Specification | Unit BOM ($) | Batch MOQ / Basis | Supplier / Reference Link |
| :--- | :--- | :--- | :--- | :--- |
| **Beechwood Letter Tiles (102 needed)** | Panda Game Mfg *(19x19x4.8mm + ø15.5mm cavity)* | **$2.20 / set** | 1,000 sets | [Panda Game Mfg](https://pandagm.com) |
| **15mm NTAG213 Tags on Reels (102 needed)** | CXJ RFID Factory *(ø15mm wet inlay reels)* | **$3.57 / set** | 2,000-tag reels ($0.035/tag) | [CXJ RFID Factory](https://www.cxjrfidfactory.com) |
| **Factory Tag Placement & Mapping** | Board Game Assembly Partner *(Pick & place + UID)* | **$0.75 / set** | 1,000 sets | [Panda Game Mfg](https://pandagm.com) |
| **15x15 Main Circuit Board (1 board)** | JLCPCB / PCBWay *(320×320mm 4-layer FR4)* | **$17.50 / board** | 1,000 boards | [JLCPCB](https://jlcpcb.com) |
| **NFC Transceiver IC (1 IC)** | STMicroelectronics *(ST25R3916-AQFT QFN-32)* | **$3.00** | Tape & reel | [ST25R3916 (STMicro)](https://www.st.com/en/nfc/st25r3916.html) |
| **Rotating Turntable 250mm Ring (1 unit)** | Hardware Wholesale Partner *(Aluminum lazy susan)* | **$4.00** | 1,000 units | [Alibaba Sourcing](https://www.alibaba.com) |
| **3.5" IPS Color Screen (1 panel)** | ST7796 / Panel Partner *(480×320 wide angle)* | **$7.20** | 1,000 panels | [AliExpress / Panel Partner](https://www.aliexpress.com) |
| **Audio Voice Referee Subsystem (1 set)** | PUI Audio / SMT BOM *(MAX98357A + 40mm 4Ω 3W)* | **$2.45** | 1,000 sets | [PUI Audio](https://www.puiaudio.com) |
| **Host Microcontroller Module (1 module)** | Espressif Systems *(ESP32-S3-WROOM-1-N16R8)* | **$3.00** | SMD reels | [Espressif Systems](https://www.espressif.com) |
| **Battery & Power Management (1 set)** | Custom Battery Supplier *(3500mAh LiPo + BMS + Mag cable)* | **$6.20** | 1,000 packs | [Alibaba Sourcing](https://www.alibaba.com) |
| **Wood Housing & Grid Frame (1 set)** | Wood Tooling Partner *(CNC base tray + top grid)* | **$14.00** | 1,000 sets | [Wood Tooling Partner](https://pandagm.com) |
| **Packaging, Foam Tray & Guide (1 set)** | Packaging Fabricator *(Rigid gift box + EVA foam)* | **$4.00** | 1,000 boxes | [Packaging Partner](https://pandagm.com) |
| **TOTAL PRODUCTION BOM / UNIT** | **Complete Smart Crossword Board (1,000 unit run)** | **$67.87** | **Under $70–$100 Target** | *(Commercial Viability Target Achieved)* |

<!-- TBLFM: @>$3=sum(@I..@-1) -->

---

## 3. How DataLoom Works Here

Both spreadsheets ([`Prototype_4x4_Shopping_List.loom`](file:///home/robin/Smart-Crossword-Board/Prototype_4x4_Shopping_List.loom) and [`Production_15x15_Sourcing_List.loom`](file:///home/robin/Smart-Crossword-Board/Production_15x15_Sourcing_List.loom)) are live in your Obsidian vault:
* **Interactive Editing**: Click any cell to edit prices or names directly like Excel.
* **Automatic Sum Calculation**: The cost columns have calculation set to **Sum** with currency formatting (€ for Prototype, $ for Production).
* **Instant Recalculation**: Change any value or add new rows — the footer total recalculates dynamically without touching markdown syntax.
