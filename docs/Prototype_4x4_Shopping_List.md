# 🛒 Prototype (4x4) Shopping List

This shopping list reflects the top-recommended components selected from the multi-candidate market evaluation in [[Component_Candidate_Comparison|Component Candidate Comparison]]. All e-commerce links are actively verified live on Amazon Belgium (`amazon.com.be`) per **FAIL-010**.

### Interactive Dynamic Spreadsheet (DataLoom)
![[Prototype_4x4_Shopping_List.loom]]

---

### Master Quick-Reference Table

| Item / Component                     | Top Candidate Pack Details                          | Bench Cost | Pack Price  | Store Link                                                                     |
| :----------------------------------- | :-------------------------------------------------- | :--------- | :---------- | :----------------------------------------------------------------------------- |
| **Letter Tiles (16 needed)**         | 200 Pcs Wooden Scrabble Tiles                       | **€6.99**  | €6.99       | [Amazon BE (`B0GH7LXL2K`)](https://www.amazon.com.be/dp/B0GH7LXL2K)            |
| **13.56 MHz NFC Tags (16 needed)**   | 60 Pcs NTAG213 Stickers 25mm                        | **€6.99**  | €6.99       | [Amazon BE (`B0HC2ZKQLQ`)](https://www.amazon.com.be/dp/B0HC2ZKQLQ)            |
| **NFC Reader Module (1 needed)**     | NXP PN5180 High-Power Breakout                      | **€11.82** | €11.82      | [Amazon BE (`B0HDTXDNJY`)](https://www.amazon.com.be/dp/B0HDTXDNJY)            |
| **Host Microcontroller (1 needed)**  | ESP32-S3 DevKit N16R8 *(3-pack @ €20.98)*           | **€6.99**  | €20.98      | [Amazon BE (`B0GXF14RRM`)](https://www.amazon.com.be/dp/B0GXF14RRM)            |
| **16-Ch Multiplexer (1 needed)**     | DollaTek CD74HC4067 Breakout *(5-pack @ €5.99)*     | **€1.20**  | €5.99       | [Amazon BE (`B07PPKRVGW`)](https://www.amazon.com.be/dp/B07PPKRVGW)            |
| **Rotating Turntable (1 needed)**    | QWORK Square Bearing 71x71mm *(4-pack @ €6.98)*     | **€1.75**  | €6.98       | [Amazon BE (`B0B3X7R961`)](https://www.amazon.com.be/dp/B0B3X7R961)            |
| **Color Display Screen (1 needed)**  | 3.5" TFT SPI 480x320 with Touch                     | **€17.91** | €17.91      | [Amazon BE (`B0BZXX1QFM`)](https://www.amazon.com.be/dp/B0BZXX1QFM)            |
| **Audio Referee DAC Amp (1 needed)** | MAX98357A I2S 3W Amp *(3-pack @ €9.09)*             | **€3.03**  | €9.09       | [Amazon BE (`B0F21T7Q3P`)](https://www.amazon.com.be/dp/B0F21T7Q3P)            |
| **Mini Speaker 40mm (1 needed)**     | RELAND SUN 3W 4Ω Speakers *(2-pack @ €4.70)*        | **€2.35**  | €4.70       | [Amazon BE (`B09YQ1S988`)](https://www.amazon.com.be/dp/B09YQ1S988)            |
| **Hardware Fasteners Kit**           | 440 Pcs M3 Button Head Screws & Nuts Box            | **€7.88**  | €7.88       | [Amazon BE (`B0B3MGZ7T2`)](https://www.amazon.com.be/dp/B0B3MGZ7T2)            |
| **Anti-Skid Bumper Feet (4 needed)** | Silicone Bumper Feet 10mm *(12-pack @ €8.99)*       | **€3.00**  | €8.99       | [Amazon BE (`B08GKP4311`)](https://www.amazon.com.be/dp/B08GKP4311)            |
| **3D Print Chassis & Grid (1 set)**  | PLA / PETG Spool Allocation (~120g filament)        | **€2.40**  | €19.99      | [3D CAD Models](file:///home/robin/Smart-Crossword-Board/hardware/cad/output/) |
| **TOTAL BENCH PROTOTYPE COST**       | **All components to build 1 fully functional unit** | **€72.31** | **€128.31** | *(Multi-pack checkout provides ample spares)*                                  |

<!-- TBLFM: @>$3=sum(@I..@-1) -->

> 🔍 **Multi-Candidate Analysis**: To inspect alternative vendors, bulk options, or comparison trade-offs across all 9 hardware categories, refer to [[Component_Candidate_Comparison|Component Candidate Comparison]].

---

### ⚠️ PCB Assembly & Bench Wiring Notes (FAIL-011)

1. **Multiplexer Footprint (CD74HC4067)**:
   * The custom 4-layer PCB (`hardware/kicad/test_grid_4x4/`) uses an SMD **SOIC-24** footprint (`CD74HC4067SM96`, LCSC `C7406`, $0.28).
   * The DollaTek breakout pack listed above is a 24-pin DIP board module for breadboard bench testing.
   * When fabricating the custom PCB via JLCPCB, select SMT assembly (PCBA) to have U1 and all 0603 passive components factory-soldered.
2. **NFC Reader Connection (NXP PN5180)**:
   * The NXP PN5180 breakout kit (`B0HDTXDNJY`) delivers 250mW RF output (5x PN532 power) with Dynamic Power Control (DPC).
   * Connect digital SPI lines (SCK, MISO, MOSI, NSS/CS, BUSY, IRQ, 3.3V, GND) to the host / header `J2` using female-to-female Dupont jumper wires.
   * Connect the RF output stage to SMA port `J3` (or `J2` Pin 1 `RF_SIG`) via a short 50Ω coaxial cable.
3. **ESP32-S3 Host Connection**:
   * Connect the ESP32-S3 DevKit (`B0GXF14RRM`) to header `J1` using a standard 2x10 2.54mm IDC ribbon cable or Dupont jumpers according to the pinout map in [[hardware/kicad/test_grid_4x4/README|Phase 1 4x4 NFC Test Board README]].

