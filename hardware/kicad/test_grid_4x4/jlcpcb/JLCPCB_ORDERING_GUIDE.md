# JLCPCB 4x4 Test Board Ordering Guide

This guide walks you through ordering the 4x4 NFC test circuit board on [JLCPCB.com](https://jlcpcb.com/).

---

## 1. Quick File Reference

All required manufacturing files are located in this repository:

| File | Purpose | Location |
| :--- | :--- | :--- |
| **Gerber Archive** | Board fabrication (traces, drills, copper, mask) | [`test_grid_4x4_gerbers.zip`](../test_grid_4x4_gerbers.zip) |
| **BOM File** | SMT component list with LCSC part numbers | [`bom_jlcpcb.csv`](bom_jlcpcb.csv) |
| **CPL File** | Component placement & rotation (Pick and Place) | [`cpl_jlcpcb.csv`](cpl_jlcpcb.csv) |

---

## 2. Choosing Your Assembly Method

You have two options when ordering on JLCPCB:

### Option A: SMT Assembly (Recommended)
* **Estimated Cost**: ~$25–$35 for 2 to 5 assembled boards.
* **What JLCPCB does**: Solders all 32 SMD capacitors (100pF C0G), 16 resistors (3.3Ω), power decoupling caps, and the SOIC-24 CD74HC4067 multiplexer.
* **What you solder at home**: Only the 3 through-hole pin headers (J1 2x10, J2 1x10, and J3 SMA socket) using a standard soldering iron in 2 minutes.

### Option B: Bare PCB Only (Hand Soldering)
* **Estimated Cost**: ~$4–$5 for 5 bare boards (+ shipping).
* **What JLCPCB does**: Manufactures the bare 4-layer PCB only.
* **What you solder at home**: All surface-mount 0603 parts, SOIC-24 chip, and headers. (Requires a fine soldering tip, tweezers, flux, or hot air).

---

## 3. Step-by-Step Order Walkthrough on JLCPCB

### Step 1: Upload Gerbers
1. Go to [https://jlcpcb.com/quote](https://jlcpcb.com/quote).
2. Click **"Add Gerber file"** and select `test_grid_4x4_gerbers.zip`.
3. JLCPCB will automatically parse the board dimensions (**100 mm x 100 mm**).

### Step 2: Configure PCB Parameters
Set the following settings (most are default):
* **Layers**: `4 Layers` *(automatically detected)*
* **PCB Qty**: `5`
* **PCB Thickness**: `1.6 mm`
* **PCB Color**: Green (or your preferred color)
* **Surface Finish**: `HASL with lead` or `LeadFree HASL`
* **Copper Weight**: `1 oz` (outer and inner)
* **Layer Stackup**: `JLC04161H-7628` (Standard 4-layer stackup)
* **Impedance Control**: `No`
* **Remove Order Number**: `Specify a location` or `No`

### Step 3: Enable SMT Assembly (If choosing Option A)
1. Scroll down to **"PCB Assembly"** and toggle it **ON**.
2. **Assembly Side**: `Top Side`.
3. **PCBA Qty**: `2` or `5`.
4. Click **"Confirm"** / **"Next"**.

### Step 4: Upload BOM and CPL
1. On the SMT page, upload:
   * **BOM**: `bom_jlcpcb.csv`
   * **CPL**: `cpl_jlcpcb.csv`
2. Click **"Next"**. JLCPCB will match the 5 component types:
   * `C14665`: 100pF 50V C0G (Qty: 16) — Basic part (YAGEO `CC0603JRNPO9BN101`)
   * `C22979`: 3.3Ω 1% (Qty: 16) — Basic/Standard part (UNI-ROYAL `0603WAF330KT5E`)
   * `C14663`: 0.1µF 50V X7R (Qty: 1) — Basic part
   * `C15850`: 10µF 10V X5R (Qty: 1) — Basic part
   * `C496123`: CD74HC4067SM96 SOIC-24 (Qty: 1) — Extended part (Texas Instruments `CD74HC4067M96`)
   *(Note: If C496123 is out of stock on JLCPCB, uncheck U1 to hand-solder it from the Amazon DIP breakout / bare IC, while JLCPCB assembles all 32 capacitors and 16 resistors).*
3. Click **"Next"** to review component placement on the 2D preview. All footprints are aligned centered on the pads.
4. Click **"Save to Cart"**.

---

## 4. Bench Parts to Order in Parallel (Amazon BE)

While JLCPCB fabricates your board (approx. 5–8 business days), order these verified bench prototype parts from [`docs/Prototype_4x4_Shopping_List.md`](../../../docs/Prototype_4x4_Shopping_List.md):

1. **Wooden Scrabble Tiles**: [200 Pcs Wooden Tiles](https://www.amazon.com.be/dp/B0GH7LXL2K) (€6.99)
2. **13.56 MHz NTAG213 Tags**: [60 Pcs 25mm Stickers](https://www.amazon.com.be/dp/B0HC2ZKQLQ) (€11.99)
3. **ESP32-S3 Host**: [ESP32-S3 DevKitC-1 N16R8](https://www.amazon.com.be/dp/B0GXF14RRM) (€14.99)
4. **NFC Reader Breakout**: [PN532 V3 Breakout Kit](https://www.amazon.com.be/dp/B0C9DTJMLQ) (€11.99)
5. **M3 Screws & Nuts**: [440 Pcs M3 Hardware](https://www.amazon.com.be/dp/B0B3MGZ7T2) (€12.99)
6. **Turntable Bearing**: [QWORK 71x71mm Ball Bearing](https://www.amazon.com.be/dp/B0B3X7R961) (€8.59)
