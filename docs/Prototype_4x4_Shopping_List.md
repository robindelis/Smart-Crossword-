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
| **NFC Reader Module (1 needed)**     | Hailege PN532 NFC Module V4 with IPEX (1 board)     | **€10.84** | €10.84      | [Amazon BE (`B0CJY2GQZ8`)](https://www.amazon.com.be/dp/B0CJY2GQZ8)            |
| **Host Microcontroller (1 needed)**  | diymore ESP32-S3 DevKit N16R8 *(3-pack @ €20.98)*   | **€6.99**  | €20.98      | [Amazon BE (`B0GXF14RRM`)](https://www.amazon.com.be/dp/B0GXF14RRM)            |
| **3D Print Chassis & Grid (1 set)**  | PLA / PETG Spool Allocation (~120g filament)        | **€2.40**  | €19.99      | [3D CAD Models](file:///home/robin/Smart-Crossword-Board/hardware/cad/output/) |
| **TOTAL BENCH PROTOTYPE COST**       | **Essential bench items to test 4x4 matrix**        | **€34.21** | **€65.79**  | *(Multi-pack checkout provides ample spares)*                                  |

<!-- TBLFM: @>$3=sum(@I..@-1) -->

> 🔍 **Multi-Candidate Analysis**: To inspect alternative vendors, bulk options, or comparison trade-offs across all hardware categories (including display, audio, fasteners, and turntables for the complete game), refer to [[Component_Candidate_Comparison|Component Candidate Comparison]].

---

### ⚠️ PCB Assembly & Bench Wiring Notes (FAIL-011)

1. **Multiplexer (CD74HC4067)**:
   * The custom 4-layer PCB (`hardware/kicad/test_grid_4x4/`) uses an SMD **SOIC-24** footprint (`CD74HC4067SM96`, LCSC `C496123`, $0.28) ordered with PCBA SMT assembly from JLCPCB.
2. **NFC Reader Connection (Hailege PN532 V4 with IPEX)**:
   * The Hailege PN532 module (`B0CJY2GQZ8`) features an onboard IPEX (U.FL) coaxial socket and antenna isolation solder jumpers (`J01`/`J02`).
   * **Antenna Isolation**: Desolder or cut jumpers `J01`/`J02` above the IPEX socket to disconnect the onboard trace antenna so 100% of the RF signal routes to the external grid.
   * **RF Connection**: Connect a miniature U.FL-to-SMA pigtail cable from the onboard IPEX port directly to SMA port `J3` on the 4x4 test grid (or solder mini coax directly to `J2` Pin 1 `RF_SIG` and Pin 2 `GND`).
   * **Mode Selection**: Set hardware slide switches to SPI mode (`SET0 = L, SET1 = H`).
   * **SPI Host Link**: Connect SPI lines (SCK, MISO, MOSI, NSS/CS, RST, IRQ, 3.3V, GND) to header `J2` or host ESP32-S3.
3. **ESP32-S3 Host Connection**:
   * Connect the ESP32-S3 DevKit (`B0GXF14RRM`) to header `J1` using Dupont jumpers according to the pinout map in [[hardware/kicad/test_grid_4x4/README|Phase 1 4x4 NFC Test Board README]].

