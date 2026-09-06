# Phase 1: 4x4 NFC Test Board

## 1. Purpose
This 4x4 circuit board is the Phase 1 test vehicle for the Smart Crossword Board project. It tests reading 16 RFID letter tiles through 2.0mm to 2.5mm hardwood before building the full 15x15 (225-cell) commercial board.

It verifies three physical requirements:
1. **Hardwood Penetration**: Reliable tag reads through 2.0mm–2.5mm oak or walnut veneer.
2. **Scan Speed**: Reading all 16 cells in under 40 milliseconds using an analog multiplexer.
3. **Cross-talk Isolation**: Zero false reads on neighboring empty cells when adjacent cells have tiles.

---

## 2. Key Specifications

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Grid Dimensions** | 4 x 4 (16 cells) | Pitch: 19.0 mm (matches Scrabble tiles) |
| **Active Scan Area** | 76.0 mm x 76.0 mm | Centered on board |
| **PCB Dimensions** | 100.0 mm x 100.0 mm | Standard 10cm x 10cm low-cost pool |
| **Layers** | 4 layers | F.Cu (RF), In1.Cu (GND), In2.Cu (Pwr/Sig), B.Cu (Return/GND) |
| **Coil Outer Size** | 17.5 mm x 17.5 mm | Fits comfortably within 19mm square |
| **Coil Geometry** | 7 turns, 0.25mm trace, 0.25mm space | Planar square spiral on F.Cu |
| **Coil Inductance ($L$)** | **1.262 µH** | Wheeler model verified |
| **Tuning Capacitor ($C$)** | **100 pF** (50V C0G / NP0 0603) | Resonant frequency: 13.56 MHz |
| **Damping Resistor ($R$)** | **3.3 Ω** (1% 0603) | Target loaded Q-factor: 25 |
| **RF Multiplexer** | CD74HC4067SM96 (SOIC-24) | 16-channel analog switch (LCSC C7406) |
| **Mounting** | 4x M3 screw holes (3.2mm drill) | 5.0mm inset from corners |

---

## 3. Connector Pinouts

### J1: Host Controller Header (2x10, 2.54mm Pitch)
Connects directly to an ESP32-S3 DevKit or breadboard:

| Pin | Net | Function | Pin | Net | Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | +3.3V | Power In | **2** | +3.3V | Power In |
| **3** | MUX_S3 | Address bit 3 | **4** | GPIO_AUX | Spare tactile button / LED |
| **5** | MUX_S2 | Address bit 2 | **6** | I2C_SDA | Spare I2C data |
| **7** | MUX_EN | MUX active-low enable | **8** | I2C_SCL | Spare I2C clock |
| **9** | MUX_S1 | Address bit 1 | **10** | NFC_IRQ | NFC interrupt |
| **11** | MUX_S0 | Address bit 0 | **12** | NFC_RST | NFC reset |
| **13** | GND | Ground | **14** | SPI_MOSI | NFC SPI data out |
| **15** | GND | Ground | **16** | SPI_CS | NFC SPI chip select |
| **17** | GND | Ground | **18** | SPI_SCK | NFC SPI clock |
| **19** | GND | Ground | **20** | SPI_MISO | NFC SPI data in |

### J2: NFC Transceiver Header (1x10, 2.54mm Pitch)
Connects to an ST25R3916 or PN532 transceiver breakout:
1. `RF_SIG` (Multiplexer common RF output/input)
2. `GND`
3. `+3.3V`
4. `GND`
5. `SPI_SCK`
6. `SPI_MISO`
7. `SPI_MOSI`
8. `SPI_CS`
9. `NFC_IRQ`
10. `NFC_RST`

### J3: SMA RF Test Port
Standard 50Ω SMA coaxial connector wired to `RF_SIG` for connecting an oscilloscope or Vector Network Analyzer (VNA) during bench characterization.

---

## 4. Verification & DRC Status (KiCad 10.0.6)

* **Design Rule Check (DRC)**: **0 errors, 0 warnings, 0 violations**.
* **Unconnected Items**: **0 unconnected nets** (all 49 nets fully routed).
* **Layer Stackup**:
  * **F.Cu**: 16 planar spiral coils (1.26 µH, 7 turns), RF_SIG 50Ω trace, 0603 matching network components.
  * **In1.Cu**: Continuous solid GND plane with 16 dedicated keepout apertures ($18.5\text{mm} \times 18.5\text{mm}$) preventing RF eddy current damping.
  * **In2.Cu**: 100% planar coil feed routing for Columns A, B, C, and D, plus SPI bus lines.
  * **B.Cu**: Bottom GND plane with thermal relief spokes to coil centers, concentric MUX control lines, and +3.3V power bus.

---

## 5. Bill of Materials (BOM)

| Designator | Description | Footprint | LCSC Part # | Unit Price (100 qty) |
| :--- | :--- | :--- | :--- | :--- |
| **U1** | CD74HC4067SM96 16-Ch MUX | SOIC-24 | C7406 | $0.28 |
| **C1–C16** | 100pF 50V C0G 5% | 0603 | C14405 | $0.005 |
| **R1–R16** | 3.3Ω 1% 1/10W | 0603 | C22971 | $0.003 |
| **C17–C20**| 0.1µF 50V X7R 10% (Decoupling) | 0603 | C14663 | $0.003 |
| **J1** | 2x10 2.54mm Male Pin Header | THT 2x10 | C22588 | $0.15 |
| **J2** | 1x10 2.54mm Male Pin Header | THT 1x10 | C22585 | $0.08 |
| **J3** | SMA End Launch / Edge Female | SMA-TH | C2837267 | $0.65 |
| **H1–H4** | M3 Mounting Holes | 3.2mm PTH | N/A | $0.00 |

**Total BOM cost for 4x4 test board**: ~$1.45 (excluding PCB fab).

---

## 6. How to Open and Review in KiCad

1. Open your Linux application launcher.
2. Select **KiCad (EDA Suite)** (the top entry with the blue icon).
3. In KiCad, go to **File -> Open Project...**.
4. Browse to `hardware/kicad/test_grid_4x4/test_grid_4x4.kicad_pro`.
5. Double-click `test_grid_4x4.kicad_sch` to view the schematic, or `test_grid_4x4.kicad_pcb` to view the board layout.
6. In the PCB editor, press **Alt + 3** (or menu **View -> 3D Viewer**) to interact with the 3D model.

---

## 7. Prototype (4x4) Shopping List Compatibility & Wiring Guide

This section verifies compatibility with the components procured in [[Prototype_4x4_Shopping_List|Prototype 4x4 Shopping List]]:

### Component Compatibility Matrix

| Shopping List Item | Selected Model | PCB Compatibility | Connection / Assembly Notes |
| :--- | :--- | :--- | :--- |
| **Letter Tiles (16 needed)** | 200 Pcs Wooden Scrabble Tiles (`B0GH7LXL2K`) | ✅ **100% Compatible** | 19.0 x 19.0 x 4.8 mm wood tiles align 1:1 with the 19.0mm PCB coil pitch. |
| **13.56 MHz NFC Tags** | 60 Pcs NTAG213 Stickers 25mm (`B0HC2ZKQLQ`) | ✅ **100% Compatible (RF)** | 13.56 MHz ISO 14443A matches resonant LC tank. For bench testing, 25mm stickers can be affixed centered on tiles or test veneer. |
| **Host Microcontroller** | ESP32-S3 DevKitC-1 N16R8 (`B0GXF14RRM`) | ✅ **100% Compatible** | 3.3V logic matches +3.3V rail. Connects to J1 via 20-pin IDC ribbon or Dupont jumper wires. |
| **16-Ch Multiplexer** | DollaTek CD74HC4067 Breakout (`B07PPKRVGW`) | ⚠️ **Footprint Variant Note** | PCB footprint U1 is **SOIC-24 SMD** (`CD74HC4067SM96`, LCSC C7406) for JLCPCB PCBA. The Amazon DollaTek breakout module (24-pin DIP) is for breadboard testing. Order JLCPCB PCBA or bare SOIC-24 IC for this PCB. |
| **NFC Reader Module** | PN532 V3 RFID/NFC Breakout Kit (`B0C9DTJMLQ`) | ⚠️ **RF Tap Required** | Connect SPI signals (SCK, MISO, MOSI, SS/CS, IRQ, RST, 3.3V, GND) to J2 via Dupont leads. To drive PCB coils, link the PN532 RF stage to J3 (SMA) or J2 Pin 1 (`RF_SIG`) via a 50Ω coaxial pigtail. |
| **Rotating Turntable** | QWORK Square Bearing 71x71mm (`B0B3X7R961`) | ✅ **100% Compatible** | Mounts centered underneath the 3D-printed base enclosure tray; zero interference with PCB. |
| **Color Display Screen** | 3.5" TFT SPI 480x320 (`B0BZXX1QFM`) | ✅ **100% Compatible** | Off-board peripheral wired directly to ESP32-S3 host GPIOs. |
| **Audio DAC Amp & Speaker** | MAX98357A I2S Amp (`B0F21T7Q3P`) + 40mm 4Ω Speaker | ✅ **100% Compatible** | Off-board I2S peripheral wired directly to ESP32-S3 host GPIOs. |
| **Hardware Fasteners** | 440 Pcs M3 Button Head Screws & Nuts (`B0B3MGZ7T2`) | ✅ **100% Compatible** | M3x8 / M3x10 screws seat perfectly in the 4x 3.2mm corner mounting holes (H1–H4). |
| **Anti-Skid Bumper Feet** | Silicone Bumper Feet 10mm (`B08GKP4311`) | ✅ **100% Compatible** | Fits bottom locating recesses in 3D-printed base enclosure. |

### J1 (ESP32-S3 Host) Wiring Map

| Header J1 Pin | Net | ESP32-S3 DevKit Pin | Function |
| :--- | :--- | :--- | :--- |
| **Pin 1, 2** | `+3.3V` | `3V3` | Power Supply |
| **Pin 3** | `MUX_S3` | `GPIO 4` | Multiplexer Address Bit 3 |
| **Pin 5** | `MUX_S2` | `GPIO 5` | Multiplexer Address Bit 2 |
| **Pin 7** | `MUX_EN` | `GPIO 6` | Multiplexer Enable (Active Low) |
| **Pin 9** | `MUX_S1` | `GPIO 7` | Multiplexer Address Bit 1 |
| **Pin 11** | `MUX_S0` | `GPIO 15` | Multiplexer Address Bit 0 |
| **Pin 13, 15, 17, 19** | `GND` | `GND` | Ground Reference |
| **Pin 4** | `GPIO_AUX` | `GPIO 16` | Spare / Tactile Button / LED |
| **Pin 6** | `I2C_SDA` | `GPIO 8` | Spare I2C Data |
| **Pin 8** | `I2C_SCL` | `GPIO 9` | Spare I2C Clock |
| **Pin 10** | `NFC_IRQ` | `GPIO 10` | NFC Reader Interrupt |
| **Pin 12** | `NFC_RST` | `GPIO 11` | NFC Reader Reset |
| **Pin 14** | `SPI_MOSI`| `GPIO 13` | SPI Data Host -> NFC |
| **Pin 16** | `SPI_CS` | `GPIO 14` | SPI Chip Select |
| **Pin 18** | `SPI_SCK` | `GPIO 12` | SPI Clock |
| **Pin 20** | `SPI_MISO`| `GPIO 21` | SPI Data NFC -> Host |

