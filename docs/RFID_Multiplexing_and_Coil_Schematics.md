# RFID Detection: PCB Coils, Load Modulation & 225-Square Multiplexing

This document explains the physical and electrical architecture of the RFID sensor system, how the PCB coils work, how passive tags communicate back, and how we scale from 16 to 225 squares.

---

## 1. Physical Layer Stackup

Each of the 225 squares on the wooden crossword board has a flat copper spiral etched into the circuit board directly underneath it.

```text
┌────────────────────────────────────────────────────────┐
│               WOODEN LETTER TILE (4.0mm)               │
│                                                        │
│       ┌────────────────────────────────────────┐       │
│       │  NTAG213 Passive NFC Sticker (0.2mm)   │       │
└───────┴────────────────────────────────────────┴───────┘
══════════════════════════════════════════════════════════ Top Board Surface
              HARDWOOD TOP PLATE (2.0mm)
══════════════════════════════════════════════════════════ Hidden Inside Board
       ░░░░░░░░ Air Gap / Adhesive (0.2mm) ░░░░░░░░
────────────────────────────────────────────────────────── Top of PCB (L1)
  [██]  [██]  [██]   Spiral Copper Trace   [██]  [██]  [██]
────────────────────────────────────────────────────────── FR4 Substrate
                   GROUND SHIELD PLANE (L2)
──────────────────────────────────────────────────────────
```

* **No bulky spools**: The antenna is just copper tracks printed during standard PCB fabrication. It costs **$0.00** in extra components.
* **Magnetic link**: The 13.56 MHz alternating magnetic field passes through the 2.0mm wood into the tile's microchip.

---

## 2. How the Tag Talks Back (Load Modulation / "Tug on the Rope")

The tile has **no battery** and **no radio transmitter**. It cannot broadcast like Wi-Fi. Instead, it uses **Load Modulation**:

```text
┌───────────────────────┐                    ┌───────────────────────┐
│     BOARD READER      │                    │     TILE (PASSIVE)    │
│                       │                    │                       │
│  [13.56 MHz AC Drive] │                    │                       │
│           │           │                    │                       │
│           ▼           │   Magnetic Flux    │           ▼           │
│   ┌───────────────┐   │ ~ ~ ~ ~ ~ ~ ~ ~ ~ >│   ┌───────────────┐   │
│   │ Board Copper  │   │     (2mm wood)     │   │  Tile Antenna │   │
│   │ Antenna Coil  │   │< - - - - - - - - - │   │   Tag Coil    │   │
│   └───────┬───────┘   │   Load Modulation  │   └───────┬───────┘   │
│           │           │   (Tug on field)   │           │           │
│           ▼           │                    │           ▼           │
│    Current Sensor /   │                    │     Modulation FET    │
│     Demodulator       │                    │    (Switches load)    │
│           │           │                    │           │           │
│           ▼           │                    │           ▼           │
│     Decoded Bytes     │                    │    Microchip Logic    │
│    ("Letter = 'A'")   │                    │     (UID Memory)      │
└───────────────────────┘                    └───────────────────────┘
```

1. The board reader coil generates a 13.56 MHz magnetic field.
2. The tile coil harvests that energy to power up its chip for a few milliseconds.
3. When the chip sends data (`1`s and `0`s), it rapidly switches a tiny internal load on and off.
4. Down on the board, the reader senses this tiny change in its own electrical current (like feeling a tug on a rope).

---

## 3. The 16-Square Test Bench (Phase 1)

For our 4x4 test grid, **1 reader chip** connects to **1x CD74HC4067 (16-channel multiplexer)**:

```text
               ┌─────────────────────────────────────────────────────────┐
               │              CD74HC4067 (16-Channel Mux)                │
               │                                                         │
               │                   ┌───> Square (0,0) Antenna Coil       │
               │                   ├───> Square (0,1) Antenna Coil       │
               │  Common RF Pin    ├───> Square (0,2) Antenna Coil       │
[ PN532 / ST25 ]──────────────────>│───> ...                             │
  Reader Chip  │                   ├───> Square (3,2) Antenna Coil       │
               │                   └───> Square (3,3) Antenna Coil       │
               │                                                         │
               │  Channel Address: S0, S1, S2, S3                        │
               └─────────────▲───────▲───────▲───────▲───────────────────┘
                             │       │       │       │
                       [ ESP32 Microcontroller: 4 GPIO Pins ]
```

* The ESP32 sets `S0-S3` from binary `0000` to `1111` to scan all 16 squares.
* Each square takes **2.5 ms**. All 16 squares are read in **40 ms**.

---

## 4. Scaling to 225 Squares: The Tricks

To scale from 16 to 225 squares, you might wonder: *Do we need 15 separate reader chips or a massive nest of wires?*

**No.** We use two smart electrical engineering tricks:

### Trick 1: The 2-Stage Multiplexer Tree (Hierarchical Switching)

Instead of running 225 separate wires to the microcontroller, we organize the switches like a tree:
* **1 Master Multiplexer** selects which **Row** to talk to (Row 0 through Row 14).
* **15 Row Multiplexers** (one per row) select which **Column** square in that row to read (Col 0 through Col 14).

```text
                          [ 1 Reader Chip (ST25R3916) ]
                                        │
                                        ▼
                       ┌─────────────────────────────────┐
                       │    MASTER MUX (74HC4067)        │
                       │   Selects Active Row (0 to 14)  │
                       └─┬──────┬──────┬──────┬────────┬──┘
                         │      │      │      │        │
           ┌─────────────┘      │      │      │        └─────────────┐
           ▼                    ▼      ▼      ▼                      ▼
    ┌──────────────┐      ┌──────────────┐                    ┌──────────────┐
    │  ROW 0 MUX   │      │  ROW 1 MUX   │       ...          │  ROW 14 MUX  │
    │ (74HC4067)   │      │ (74HC4067)   │                    │ (74HC4067)   │
    └──────┬───────┘      └──────┬───────┘                    └──────┬───────┘
           │                     │                                   │
      15 Coils              15 Coils                            15 Coils
   [Col 0 ... 14]        [Col 0 ... 14]                      [Col 0 ... 14]
   (Squares 0-14)        (Squares 15-29)                    (Squares 210-224)
```

#### Why This Trick Is Brilliant:
1. **Total Chips**: $1 \text{ Master} + 15 \text{ Row Muxes} = \mathbf{16\text{ chips total}}$.
2. **Total Cost**: 16x CD74HC4067 chips @ $0.18 each = **~$2.88 total**.
3. **Microcontroller Pins**:
   * 4 GPIO pins for `Row Select` (connected to Master Mux).
   * 4 GPIO pins for `Column Select` (connected in parallel to all 15 Row Muxes).
   * **Only 8 pins from the ESP32 control all 225 squares!**

---

### Trick 2: Why Not a Keyboard Matrix (Rows & Columns)?

In computer keyboards, 15 rows and 15 columns only need 30 wires with diodes. Why don't we use a simple cross-point matrix for RFID?

* **Sneak Paths & High Frequency RF**: At 13.56 MHz, RF alternating current leaks through adjacent unselected coils in parallel ("sneak paths").
* **Detuning**: A passive cross-matrix turns all neighboring coils into resonant parasitic loads, absorbing the signal.
* **Multiplexers eliminate this**: The 74HC4067 physical analog switches physically disconnect the unselected coils, keeping RF isolation clean (>40 dB) and resonance sharp ($Q \ge 20$).

---

### Trick 3: Firmware Differential Scanning (Power & Speed)

The engine does not need to blast all 225 squares every second:

1. **Idle Play (Differential Scan)**:
   * Only scan empty squares immediately adjacent to already played words.
   * Scans 15–30 squares instead of 225. Takes **~50 ms**; saves 85% battery.
2. **Submit Move (Full-Board Sweep)**:
   * When the player presses the big tactile "Submit Word" button, the board performs one complete sweep across all 225 squares:
     $$225 \text{ squares} \times 2.5\text{ms} = \mathbf{562.5\text{ms}}$$
   * In roughly **half a second**, the board verifies the entire physical grid.
