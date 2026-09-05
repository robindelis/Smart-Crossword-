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
