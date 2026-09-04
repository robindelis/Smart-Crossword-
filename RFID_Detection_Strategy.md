# RFID Piece Detection Strategy & 4x4 Test Board

This document explains the physical sensor design that lets the wooden board detect all letters on the 15x15 grid through solid wood.

---

## 1. How It Works (Passive Magnetic Induction)

* **No Batteries in Tiles**: Each wooden letter tile has a 12mm passive NFC tag (NTAG213) glued into a shallow 1mm pocket underneath.
* **Under-Board Coils**: Under each 19mm x 19mm square on the board is an etched copper spiral antenna on a circuit board.
* **Wireless Power**: When an antenna coil sends out a 13.56 MHz magnetic pulse, it passes through the wood into the tile. By basic electromagnetic induction (Faraday's law), this creates a small electric current that wakes up the tile's microchip.
* **Reading the Letter**: The powered chip answers back with its unique 7-byte ID code (e.g. `04:A1:3B:5C:7F:8E:10`) by subtly varying its electrical load. The board reader detects this and looks up which letter was placed.
* **Speed**: Reading one tile takes **2.0 to 2.5 milliseconds**.

---

## 2. Scanning 225 Squares with 1 Reader Chip

To keep costs low, we do not use 225 reader chips. We use **one central reader chip** and **electronic multiplexer switches**:

* **Reader Chip**: STMicroelectronics ST25R3916 or NXP PN532.
* **Analog Switches**: 74HC4067 16-channel switches.
* **Full Board Scan Time**:
  $$225 \text{ squares} \times 2.5\text{ms} = 562.5\text{ms}$$
  When Grandma presses the physical "Submit Move" button, the board scans all 225 squares in **about half a second**.
* **Idle Scanning**: During normal play, the board only checks empty squares next to existing words, cutting power by 90%.

---

## 3. Critical Wood Thickness Rule

> [!IMPORTANT]
> **Wood Thickness Limit: Under 2.5mm**
> 13.56 MHz coils of 15mm diameter have a magnetic read range of **6mm to 8mm**.
> The wooden top plate directly above the circuit board must be **$\le 2.0\text{mm} - 2.5\text{mm}$ thick**.
> If the wood is 4mm or thicker, tags will fail to read or drop out intermittently.

---

## 4. Cost Budget (BOM Target)

| Part | Description | Qty | Cost |
| :--- | :--- | :--- | :--- |
| **NFC Reader** | ST25R3916 or PN532 transceiver | 1 | $3.20 |
| **Multiplexers** | 74HC4067 16-channel switches | 4 | $1.12 |
| **Tuning Caps** | NPO/C0G 5% ceramic capacitors | 450 | $1.80 |
| **Tile Tags** | 12mm NTAG213 inlays ($0.065 ea) | 120 | $7.80 |
| **4-Layer PCB** | 15x15 coil panel (JLCPCB) | 1 | $12.00 |
| **Total Sensor Cost** | | | **~$25.92** |

This leaves ~$55 for the ESP32 compute, screen, wood chassis, battery, and speaker to stay under the $100 ceiling.

---

## 5. Phase 1 Prototype: 4x4 Test Grid (16 Squares)

Before ordering a full 380mm x 380mm circuit board, we build and bench test a **4x4 test grid**:
1. **16-Coil Test Board**: 16 squares (19mm pitch) with 1x 74HC4067 multiplexer.
2. **Wood Penetration Bench Test**: Test reading tags through 1.5mm, 2.0mm, 2.5mm, and 3.0mm wood veneer samples.
3. **Crosstalk Check**: Place 4 tiles side-by-side to verify neighboring coils do not create false readings.
4. **Driver Link**: Feed raw tag IDs directly into `crossword_engine.c`.
