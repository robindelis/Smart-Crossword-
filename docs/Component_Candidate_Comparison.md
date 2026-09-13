# Component Candidate Comparison (Procurement Research)

This document provides a detailed side-by-side comparison of candidate parts for every hardware component of the **Smart Crossword Board**, covering both the **Prototype (4x4) Bench Test** and the **Full Commercial (15x15) Board**.

All online store links have been actively verified live via [`scripts/verify_ecommerce_links.py`](file:///home/robin/Smart-Crossword-Board/scripts/verify_ecommerce_links.py) according to **FAIL-010** (HTTP 200, active in-stock status, and verified EUR pricing).

---

## Master Overview: Top Recommendations per Component

| Component | Top Pick (Prototype) | Unit Price | Store / Link | Key Trade-off / Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1. Wood Letter Tiles** | **200 Pcs Scrabble Wooden Tiles** | **€0.035** (€6.99 / 200) | [Amazon BE (`B0GH7LXL2K`)](https://www.amazon.com.be/dp/B0GH7LXL2K) | Standard 19x19x4.8mm pine/beechwood tiles, exact fit for 19mm CAD pockets. |
| **2. 13.56 MHz NFC Tags** | **60 Pcs NTAG213 Stickers 25mm** | **€0.116** (€6.99 / 60) | [Amazon BE (`B0HC2ZKQLQ`)](https://www.amazon.com.be/dp/B0HC2ZKQLQ) | Lowest cost per tag on Amazon BE; fast read speed with PN532. |
| **3. NFC Reader Module** | **Hailege PN532 V4 with IPEX** | **€10.84** | [Amazon BE (`B0CJY2GQZ8`)](https://www.amazon.com.be/dp/B0CJY2GQZ8) | Pre-soldered IPEX/U.FL RF port; cut jumpers J01/J02 to isolate antenna; 100% SPI driver match. |
| **4. Host Microcontroller** | **ESP32-S3 DevKitC-1 N16R8 (3-Pack)** | **€6.99** (€20.98 / 3) | [Amazon BE (`B0GXF14RRM`)](https://www.amazon.com.be/dp/B0GXF14RRM) | 16MB Flash + 8MB Octal PSRAM. Holds entire word dictionary in fast RAM. |
| **5. 16-Ch Multiplexer** | **DollaTek CD74HC4067 Breakout (5-Pack)** | **€1.20** (€5.99 / 5) | [Amazon BE (`B07PPKRVGW`)](https://www.amazon.com.be/dp/B07PPKRVGW) | Bidirectional analog MUX, >60 MHz bandwidth, standard 0.1" DIP pins. |
| **6. Rotating Turntable** | **QWORK Square Turntable Bearing (4-Pack)** | **€1.75** (€6.98 / 4) | [Amazon BE (`B0B3X7R961`)](https://www.amazon.com.be/dp/B0B3X7R961) | 71x71mm steel ball bearing plate. Direct fit under 4x4 base enclosure. |
| **7. Color Display Screen** | **3.5" TFT SPI 480x320 with Touch** | **€17.91** | [Amazon BE (`B0BZXX1QFM`)](https://www.amazon.com.be/dp/B0BZXX1QFM) | High contrast, 480x320 resolution; large scores and words for senior players. |
| **8. Audio Referee System** | **MAX98357A I2S 3W Amp (3-Pack)** + **40mm 4Ω Speakers (2-Pack)** | **€3.03** (€9.09 / 3) + **€2.35** (€4.70 / 2) | [Amazon BE (`B0F21T7Q3P`)](https://www.amazon.com.be/dp/B0F21T7Q3P) / [Speakers (`B09YQ1S988`)](https://www.amazon.com.be/dp/B09YQ1S988) | Direct digital I2S audio without analog noise; warm voice announcements. |
| **9. Hardware Fasteners** | **440 Pcs M3 Button Head Screws & Nuts** | **€7.88** / box | [Amazon BE (`B0B3MGZ7T2`)](https://www.amazon.com.be/dp/B0B3MGZ7T2) | Hex socket button head M3x6 to M3x20mm; matches CAD counterbores. |

---

## 1. Wood Letter Tiles (19x19mm Scrabble Compatible)

The physical tiles require a standard 19.0mm x 19.0mm footprint and 4.0mm to 4.8mm thickness to sit securely in the CAD tile grid without binding or slipping.

| Candidate | Pack / Unit Price | Store & Link | Specs & Fit | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: 200 Pcs Scrabble Tiles** | €6.99 (€0.035 / tile) | [Amazon BE (`B0GH7LXL2K`)](https://www.amazon.com.be/dp/B0GH7LXL2K) | 19.0 x 19.0 x 4.8 mm solid wood | • Clear standard black print<br>• Correct Scrabble dimensions<br>• Natural wood feel | **Best for 4x4 Prototype**<br>(Immediate local stock) |
| **Option B: KAPSING 200 Pcs Alphabet** | €6.47 (€0.032 / tile) | [Amazon BE (`B0CNCRTLQ8`)](https://www.amazon.com.be/dp/B0CNCRTLQ8) | 19.0 x 19.0 x 4.5 mm pine | • Lowest price on Amazon BE<br>• Slight variance in edge rounding (±0.3mm) | **Best Budget Pick** |
| **Option C: Pinowu 200 Pcs + Pouch** | €8.99 (€0.045 / tile) | [Amazon BE (`B07RKG3C84`)](https://www.amazon.com.be/dp/B07RKG3C84) | 19.0 x 19.0 x 4.8 mm wood + bag | • Includes cloth storage pouch<br>• Clean printing and uniform face | **Best Complete Kit** |
| **Option D: 400 Pcs Letters & Numbers** | €7.99 (€0.020 / piece) | [Amazon BE (`B0DRHY6S5Q`)](https://www.amazon.com.be/dp/B0DRHY6S5Q) | 19.0 x 19.0 x 4.5 mm wood | • Lowest cost per piece<br>• Half the pack is numbers (not needed for English Scrabble) | **Best Workshop Stock** |
| **Production Target: Custom Beechwood** | $2.20 / set of 102 tiles ($0.0215 / tile) | [Panda Game Mfg](https://pandagm.com) | 19.0 x 19.0 x 4.8 mm Beechwood + CNC cavity | • Factory milled ø15.5mm x 0.8mm rear cavity<br>• Pre-engraved multi-language sets | **Production Standard** |

---

## 2. 13.56 MHz NFC Tags (NTAG213 / NTAG215)

Tags must fit onto or into the back of 19mm tiles and respond reliably when placed 2mm to 4mm above the PCB antenna coils.

| Candidate | Pack / Unit Price | Store & Link | Specs & Fit | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: 60 Pcs NTAG213 25mm** | €6.99 (€0.116 / tag) | [Amazon BE (`B0HC2ZKQLQ`)](https://www.amazon.com.be/dp/B0HC2ZKQLQ) | ø25mm, 144 bytes, NTAG213 | • Lowest unit price on Amazon BE<br>• ø25mm requires trimming or centered stick on 19mm tile | **Best Value for Prototype** |
| **Option B: 50 Pcs NTAG213 PET** | €7.89 (€0.158 / tag) | [Amazon BE (`B0GW3Y441C`)](https://www.amazon.com.be/dp/B0GW3Y441C) | ø25mm, PET waterproof | • High-yield reliability (0 DOA reports)<br>• Strong adhesive | **Reliable Bench Workhorse** |
| **Option C: YARONGTECH 10-Pack** | €5.75 (€0.575 / tag) | [Amazon BE (`B01DA0IJN6`)](https://www.amazon.com.be/dp/B01DA0IJN6) | ø25mm, genuine NXP NTAG213 | • Prime 1-day delivery<br>• Small quantity, higher per-unit cost | **Quickest 1-Day Sample** |
| **Option D: ShopNFC Wet Inlay ø15mm** | €0.49 / tag (sample) to €0.18 (bulk) | [ShopNFC Tags](https://shopnfc.com/en/nfc-stickers/115-nxp-ntag213-nfc-tags.html) | ø15.0mm or ø22.0mm clear inlay | • Fits inside ø15.5mm milled cavity without overhang<br>• Genuine NXP silicon, ISO14443A | **Best Flush Cavity Fit** |
| **Production Target: CXJ RFID 15mm Reel** | $0.035 / tag ($3.57 / set) | [CXJ RFID Factory](https://www.cxjrfidfactory.com) | ø15mm wet inlay on tape reels | • Automated pick-and-place application<br>• Verified UID database output | **Production Standard** |

---

## 3. NFC Reader / Transceiver Module

The reader module drives the 13.56 MHz magnetic field and reads tag UIDs through the multiplexer tree.

| Candidate | Price | Store & Link | Interface & Features | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A (Top Pick): Hailege PN532 Module V4** | **€10.84** | [Amazon BE (`B0CJY2GQZ8`)](https://www.amazon.com.be/dp/B0CJY2GQZ8) | SPI / I2C / UART (slide switches), onboard IPEX (U.FL) port | • Pre-soldered gold IPEX / U.FL connector directly taps RF stage<br>• Cut/desolder jumpers J01/J02 to isolate onboard trace coil<br>• Physical slide switches for instant SPI mode<br>• 100% native match with our ESP32 C driver | **Top Prototype Choice**<br>(Prime 1-Day Delivery) |
| **Option B (High Power): NXP PN5180 Breakout** | **€11.82** (single) / **€21.00** (2-pack) | [Amazon BE (`B0HDTXDNJY`)](https://www.amazon.com.be/dp/B0HDTXDNJY) / [2-Pack (`B0DRWSHRQT`)](https://www.amazon.com.be/dp/B0DRWSHRQT) | SPI (3.3V) + BUSY + IRQ, 250mW RF output | • 250mW output (5x PN532 power) cuts through MUX switch resistance easily<br>• Dynamic Power Control (DPC) prevents field collapse<br>• Dedicated edge pads for external coax / antenna launch | **High-Power Alternative** |
| **Option C (Zero Rework): ELECHOUSE ST25R3916B Mini** | **~€16.60** ($18.00) | [Elechouse Store](https://www.elechouse.com/product/st25r3916b-mini/) | SPI / I2C (3.3V), single-ended 50Ω RF drive | • Zero onboard antenna; built specifically for external antennas<br>• Native 50Ω single-ended RF drive connects directly to SMA J3<br>• Uses the exact ST25R3916 IC planned for 15x15 production | **Cleanest Engineering Match**<br>(5–10 days shipping) |
| **Production Target: ST25R3916-AQFT** | $3.00 (bare IC) | [STMicroelectronics](https://www.st.com/en/nfc/st25r3916.html) | QFN-32, 1.7W RF output, AOP | • Dynamic power control and noise suppression<br>• SMT soldered directly onto full 15x15 board | **Production IC** |


---

## 4. Host Microcontroller (ESP32-S3)

The MCU handles tile scanning, crossword dictionary validation (NWL/CSW), scoring, sound output, and display rendering.

| Candidate | Pack / Unit Price | Store & Link | Specs (Flash, PSRAM, USB) | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: diymore ESP32-S3 DevKit (3-Pack)** | €20.98 (€6.99 / board) | [Amazon BE (`B0GXF14RRM`)](https://www.amazon.com.be/dp/B0GXF14RRM) | ESP32-S3-WROOM-1 N16R8 (16MB Flash, 8MB PSRAM), Dual USB-C | • 8MB PSRAM holds full dictionary Trie in RAM for instant lookups<br>• Dual USB-C with native JTAG debugging<br>• Unbeatable unit price | **Top Recommendation**<br>(Prototype & Development) |
| **Option B: GERUI ESP32-S3 DevKit (2-Pack)** | €18.99 (€9.50 / board) | [Amazon BE (`B0D8T2NJC8`)](https://www.amazon.com.be/dp/B0D8T2NJC8) | ESP32-S3 N16R8 (16MB/8MB), CH343 USB | • Pre-soldered header pins<br>• Reliable dual USB-C design | **High Reliability 2-Pack** |
| **Option C: Single ESP32-S3 DevKit** | €10.99 | [Amazon BE (`B0FYFF8CB2`)](https://www.amazon.com.be/dp/B0FYFF8CB2) | ESP32-S3 N16R8 (16MB/8MB) | • Single board order<br>• Fast delivery | **Quick Single Unit** |
| **Option D: ESP32-WROOM-32 (2-Pack)** | €15.98 (€7.99 / board) | [Amazon BE (`B0D9BTQRYT`)](https://www.amazon.com.be/dp/B0D9BTQRYT) | Classic ESP32, 4MB Flash, NO PSRAM | • Lacks PSRAM; dictionary must be paged from flash, increasing lookup latency | **Budget Fallback Only** |
| **Production Target: ESP32-S3-WROOM-1-N16R8** | $3.00 (bare module) | [Espressif Systems](https://www.espressif.com) | SMD module, CE/FCC certified | • SMT soldered directly onto 15x15 mainboard | **Production Standard** |

---

## 5. 16-Channel Analog Multiplexer (CD74HC4067)

Multiplexers route the 13.56 MHz RF signal across antenna coils. They must have low on-resistance ($R_{\text{ON}} < 100\,\Omega$) and bandwidth $> 50\,\text{MHz}$.

| Candidate | Pack / Unit Price | Store & Link | Specs & Frequency | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: DollaTek CD74HC4067 (5-Pack)** | €5.99 (€1.20 / board) | [Amazon BE (`B07PPKRVGW`)](https://www.amazon.com.be/dp/B07PPKRVGW) | 16:1 bidirectional analog MUX breakout, 2V–6V | • Standard 0.1" DIP headers for breadboards<br>• >60 MHz analog bandwidth handles 13.56 MHz cleanly<br>• Best value pack | **Top Prototype Choice** |
| **Option B: JZK CD74HC4067 (3-Pack)** | €4.79 (€1.60 / board) | [Amazon BE (`B09VXV67DQ`)](https://www.amazon.com.be/dp/B09VXV67DQ) | 16-channel breakout with filter caps | • Compact 3-board package<br>• Pre-tested continuity | **Solid 3-Pack Option** |
| **Option C: ZJchao CD74HC4067 (10-Pack)** | €15.94 (€1.59 / board) | [Amazon BE (`B0H4X2Q4LS`)](https://www.amazon.com.be/dp/B0H4X2Q4LS) | 10x 16-channel breakout boards | • High quantity for multi-matrix breadboarding<br>• Pre-soldered boards | **Bulk Prototyping** |
| **Production Target: CD74HC4067SM96** | $0.45 - $0.85 per IC | [LCSC Electronics](https://www.lcsc.com/search?q=CD74HC4067) | SOIC-24 SMD package | • 15 ICs needed for full 15x15 board<br>• Direct PCB SMT placement | **Production Standard** |

---

## 6. Rotating Turntable / Lazy Susan Bearing

The rotating mechanism allows all 4 players to turn the board smoothly to read their tiles right-side-up.

| Candidate | Price | Store & Link | Dimensions & Construction | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: QWORK Square Bearing (4-Pack)** | €6.98 (€1.75 / unit) | [Amazon BE (`B0B3X7R961`)](https://www.amazon.com.be/dp/B0B3X7R961) | 71 x 71 mm, galvanized steel ball bearing | • Compact, flat profile (0.8mm plate)<br>• Fits directly inside 4x4 3D-printed base pocket<br>• Smooth 360° gliding | **Best for 4x4 Prototype** |
| **Option B: Lazy Susan 155mm Circular** | €17.48 | [Amazon BE (`B0CY8VZYHS`)](https://www.amazon.com.be/dp/B0CY8VZYHS) | ø155mm round steel ball race | • Medium diameter, good balance for tabletop units<br>• Pre-drilled screw holes | **Mid-Size Prototype** |
| **Option C: Gedotec Heavy Duty 200mm** | €28.49 | [Amazon BE (`B0881V5679`)](https://www.amazon.com.be/dp/B0881V5679) | ø200mm galvanized steel, 150kg load | • Industrial German build quality<br>• Very heavy and rigid; higher friction than aluminum | **Heavy Duty Option** |
| **Production Target: 250mm Aluminum Ring** | $4.00 / unit | Hardware wholesale supplier | ø250mm extruded aluminum ring | • Lightweight, low inertia, soft rubber grip feet<br>• Fits 350x350mm wooden base | **Production Standard** |

---

## 7. Color Display Screen (SPI TFT LCD)

Displays game state, word verification status, turn score, and bonus points. Must meet senior accessibility standards (high contrast, large fonts).

| Candidate | Price | Store & Link | Resolution & Interface | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: 3.5" TFT SPI 480x320 Touch** | €17.91 | [Amazon BE (`B0BZXX1QFM`)](https://www.amazon.com.be/dp/B0BZXX1QFM) | 3.5", 480x320 pixels, SPI, Touch | • Crisp 480x320 resolution for large senior-friendly digits<br>• Supports LVGL UI framework<br>• Reasonable price | **Top Recommendation** |
| **Option B: Fasizi 2.8" TFT SPI 240x320** | €9.99 | [Amazon BE (`B09Z29CGY1`)](https://www.amazon.com.be/dp/B09Z29CGY1) | 2.8", 240x320 pixels, ILI9341, Touch | • Budget-friendly<br>• Smaller display requires tighter UI fonts | **Budget Compact Screen** |
| **Option C: 4.0" TFT SPI 480x320 Touch** | €26.53 | [Amazon BE (`B0D5DSMMZ5`)](https://www.amazon.com.be/dp/B0D5DSMMZ5) | 4.0", 480x320 pixels, ILI9488, Touch | • Largest readable screen area<br>• Higher cost and larger footprint | **Maximum Readability** |
| **Production Target: 3.5" IPS Panel** | $7.20 / unit | [AliExpress / Panel Partner](https://www.aliexpress.com) | 3.5" IPS, 480x320, wide viewing angles | • IPS technology allows reading from all 4 table angles without color shift | **Production Standard** |

---

## 8. Audio Referee Subsystem (I2S DAC + Mini Speaker)

Provides clear, audible voice announcements ("Valid: 24 points" / "Unknown word: X-Y-Z"). Must have warm vocal tone and zero harsh distortion.

| Candidate | Pack / Unit Price | Store & Link | Specs & Audio Output | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: MAX98357A I2S 3W Amp (3-Pack)** | €9.09 (€3.03 / board) | [Amazon BE (`B0F21T7Q3P`)](https://www.amazon.com.be/dp/B0F21T7Q3P) | Maxim MAX98357A Class D, 3.2W into 4Ω | • Native digital I2S input directly from ESP32-S3<br>• No analog hiss, clicks, or ground loops<br>• 3 boards for €9.09 | **Top Amplifier Choice** |
| **Option B: RELAND SUN 3W 4Ω 40mm Speakers (2-Pack)** | €4.70 (€2.35 / speaker) | [Amazon BE (`B09YQ1S988`)](https://www.amazon.com.be/dp/B09YQ1S988) | 40mm round ultra-thin mini speaker, 4Ω 3W | • 40mm diameter fits perfectly in CAD base cavity<br>• Warm vocal resonance for clear speech synthesis | **Top Speaker Choice** |
| **Option C: MAX98357 Single Board** | €6.04 | [Amazon BE (`B0H5R8NNQH`)](https://www.amazon.com.be/dp/B0H5R8NNQH) | Single MAX98357 module | • Fast single-unit delivery | **Single Unit Option** |
| **Option D: MAX98357 Engineering Module** | €5.51 | [Amazon BE (`B0H6ZZ1PWG`)](https://www.amazon.com.be/dp/B0H6ZZ1PWG) | MAX98357 I2S Class D board | • Budget single amplifier module | **Budget Amp Option** |
| **Production Target: PUI Audio 40mm + Amp** | $2.45 total set | PUI Audio / SMT BOM | 40mm 4Ω 3W enclosed cavity speaker | • Custom tuned acoustic resonance for senior ear clarity | **Production Standard** |

---

## 9. Fasteners, Inserts & Anti-Skid Feet

Secures the 3D-printed chassis, PCB, turntable bearing, and prevents the board from sliding across the table when tiles are placed.

| Candidate | Pack / Unit Price | Store & Link | Specs & Compatibility | Pros & Cons | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option A: 440 Pcs M3 Screw & Nut Kit** | €7.88 / box | [Amazon BE (`B0B3MGZ7T2`)](https://www.amazon.com.be/dp/B0B3MGZ7T2) | Hex socket button head M3x6/8/10/12/16/20mm + nuts | • Button heads seat flush in CAD counterbores<br>• High-grade carbon steel, neatly partitioned case | **Top Fastener Choice** |
| **Option B: GuoYomm 160 Pcs Countersunk M3** | €10.73 / box | [Amazon BE (`B0FF9MX8TY`)](https://www.amazon.com.be/dp/B0FF9MX8TY) | 10.9 grade alloy steel, countersunk | • Flat head flush mounting | **Alternative Fasteners** |
| **Option C: Silicone Bumper Feet 10mm (12-Pack)** | €8.99 (€0.75 / pad) | [Amazon BE (`B08GKP4311`)](https://www.amazon.com.be/dp/B08GKP4311) | ø10mm transparent anti-skid silicone pads | • High-friction non-marking silicone<br>• Fits base enclosure bottom locating pockets | **Top Anti-Skid Pick** |
| **Option D: Adam Hall Rubber Feet (4-Pack)** | €2.05 (€0.51 / foot) | [Amazon BE (`B00SJFDI16`)](https://www.amazon.com.be/dp/B00SJFDI16) | ø20mm x 10mm solid rubber screw-on feet | • Heavy grip; requires screw mounting | **Heavy Duty Feet** |

---

## Summary of Total Prototype (4x4) Cost using Top Candidates

| Component             | Selected Top Candidate                                                  | Total Cost             |
| :-------------------- | :---------------------------------------------------------------------- | :--------------------- |
| **Letter Tiles**      | 200 Pcs Wooden Scrabble Tiles (`B0GH7LXL2K`)                            | €6.99                  |
| **NFC Tags**          | 60 Pcs NTAG213 Stickers 25mm (`B0HC2ZKQLQ`)                             | €6.99                  |
| **NFC Reader**        | PN532 V3 RFID/NFC Breakout Kit (`B0C9DTJMLQ`)                           | €8.98                  |
| **Microcontroller**   | diymore ESP32-S3 DevKit N16R8 3-Pack (`B0GXF14RRM`) *(1 board used)*    | €6.99 *(€20.98 for 3)* |
| **Multiplexer**       | DollaTek CD74HC4067 5-Pack (`B07PPKRVGW`) *(1 board used)*              | €1.20 *(€5.99 for 5)*  |
| **Turntable**         | QWORK Square Ball Bearing 4-Pack (`B0B3X7R961`) *(1 bearing used)*      | €1.75 *(€6.98 for 4)*  |
| **Display Screen**    | 3.5" TFT SPI 480x320 Touch Screen (`B0BZXX1QFM`)                        | €17.91                 |
| **Audio Amp**         | MAX98357A I2S 3W Amp 3-Pack (`B0F21T7Q3P`) *(1 board used)*             | €3.03 *(€9.09 for 3)*  |
| **Mini Speaker**      | RELAND SUN 3W 4Ω 40mm Speakers 2-Pack (`B09YQ1S988`) *(1 speaker used)* | €2.35 *(€4.70 for 2)*  |
| **Hardware Kit**      | 440 Pcs M3 Screw & Nut Assortment (`B0B3MGZ7T2`)                        | €7.88                  |
| **Bumper Feet**       | Silicone Bumper Feet 10mm (`B08GKP4311`) *(4 feet used)*                | €3.00 *(€8.99 for 12)* |
| **3D Print Filament** | Chassis & Top Grid in PLA/PETG (~120g)                                  | €2.40                  |
| **TOTAL BENCH COST**  | **Complete Smart Crossword 4x4 Benchtop Prototype**                     | **€69.47**             |

*Note: If buying single components without sharing multi-packs, the total checkout bill is ~€95, leaving plenty of spare MCUs, multiplexers, and NFC tags for multiple revision boards.*
