# Hall Effect Board vs. Full-Grid RFID Architecture Evaluation

This document details the engineering, firmware, ergonomic, and commercial evaluation of the proposal:
> *"Use magnets in the board (simple digital Hall effect with small magnets underneath the tiles) and only use RFID in the player's rack to detect letters."*

---

## 1. Quick Summary & Recommendation

| Criteria | Full RFID Board (Baseline) | Hall Board + RFID Rack (Proposal) | Verdict |
| :--- | :--- | :--- | :--- |
| **Tile Identity on Board** | Reads exact letter & UID on every square | Binary 1/0 presence only (square occupied / empty) | **RFID Board Wins** |
| **Anagram Disambiguation** | 100% deterministic (reads letters directly) | Ambiguous (cannot distinguish *STOP*, *POST*, *SPOT*) | **RFID Board Wins** |
| **Senior Play Ergonomics** | 100% natural (play 4 tiles at once, shuffle) | Rigid (fails if tiles are held in palm or table) | **RFID Board Wins** |
| **Remote Move Verification** | Board verifies physical letter placed by senior | Board cannot verify letter (silent desync risk) | **RFID Board Wins** |
| **Tile Handling in Bag** | Free-floating wooden tiles | 100 tiles clump together due to neodymium magnets | **RFID Board Wins** |
| **Tile Construction** | 1 flat adhesive NFC sticker ($0.05) | 1 RFID tag + 1 magnet + polarity check ($0.08) | **RFID Board Wins** |
| **Player Rack** | 100% passive solid wood ($1.50) | Active electronic device (battery, BLE, 7 coils) ($10.40) | **RFID Board Wins** |
| **Turntable Integration** | 360° rotation with zero rack wires | Wire wraps turntable OR rack needs battery charging | **RFID Board Wins** |
| **Total Sensor BOM Cost** | **~$24.62** | **~$40.30 – $50.70** | **RFID Board is $15–$25 Cheaper** |

**Final Recommendation**: **Retain the Full 15x15 RFID Board architecture.**

---

## 2. The Core Firmware Problem: The Anagram Trap

### What the Sensors Report
* **Player Rack (7 RFID coils)**: Detects letters leaving the rack (e.g., `{S, T, O, P}`).
* **Board (225 Hall sensors)**: Detects that four squares just turned from `0` to `1` (e.g., `(7,7)`, `(7,8)`, `(7,9)`, `(7,10)`).

### Why the Engine Gets Stuck
Hall sensors have no letter identification. When multiple letters are placed in one turn:
* The letters `{S, T, O, P}` can form: **STOP**, **POST**, **SPOT**, **POTS**, and **TOPS**.
* All 5 are valid tournament words in the dictionary.
* The game engine has **no physical way** to know which word the player spelled.

To resolve this without board RFID, the product would be forced to:
1. **Force robotic sequential play**: Make Grandma place Letter 1, wait for a beep, place Letter 2, wait for a beep. (Violates natural Scrabble habits).
2. **Interrupt on screen**: Pop up a dialog: *"Did you spell STOP, POST, or SPOT?"* (Violates our screen-free senior accessibility standard).

---

## 3. Senior Ergonomics & Real-World Play

1. **The Handful Grab**:
   Seniors do not pick up tiles one by one. They grab 3 or 4 tiles in their fingers, test arrangements on the table, swap them, and then place them. The rack registers all tiles leaving at once, breaking any timestamp-based correlation.
2. **Magnetic Clumping in the Tile Bag**:
   If 100 tiles each contain an N35/N52 neodymium magnet, reaching into the fabric bag results in a heavy, clumping mass of magnets snapping together. Drawing 7 tiles becomes awkward and frustrating.
3. **Silent Desynchronization on Remote Moves**:
   When a grandchild plays `QUIZ` from a smartphone, Grandma physically places `Q`, `U`, `I`, `Z` onto the board.
   * With board RFID: If Grandma accidentally grabs an `O` instead of a `Q`, the board speaks up immediately: *"That's an O on square H8; Lucas played a Q."*
   * With Hall sensors: The board only sees a magnet and assumes it is a `Q`. The physical board and cloud game state permanently diverge, breaking future cross-word validation.

---

## 4. Hardware & Electrical Reality

1. **Main Board Savings**:
   * Changing the 380x380mm PCB from 4-layer (RF antennas) to 2-layer (DC Hall traces) saves ~$12–$17 in bare PCB fabrication.
   * However, 225 discrete Hall effect ICs ($11.25) plus SMT assembly fees ($2.50) plus 29 shift registers ($1.45) offset almost all PCB savings.
2. **The Active Rack Penalty**:
   * Because the board cannot identify letters, the player rack must do so.
   * To read 7 slots reliably without tag shadowing, the rack requires 7 individual coils multiplexed via a 74HC4051.
   * Because the board spins 360° on a turntable, a wired cable wraps around the pedestal and snags.
   * Making the rack wireless requires an ESP32-C3 MCU, lithium battery, TP4056 charger, and USB-C port, adding **+$10.40 per rack**.
   * Now Grandma has to remember to plug in and charge her tile racks in addition to the board.
3. **RF Eddy Currents in Tiles**:
   * Neodymium is an electrical conductor. Placing a metal magnet inside a 19mm tile alongside a 13.56 MHz RFID inlay induces eddy currents that detune the resonant coil unless ferrite shielding or vertical separation is added.

---

## 5. Side-by-Side BOM Cost Breakdown

| Component | Full RFID Board | Hall Board + 1 Wireless RFID Rack | Hall Board + 2 Wireless RFID Racks |
| :--- | :--- | :--- | :--- |
| **Board PCB** | $12.00 (4-layer RF panel) | $8.00 (2-layer DC panel) | $8.00 (2-layer DC panel) |
| **Board ICs & Sensors** | $4.32 (1x ST25R3916 + 4x 74HC4067) | $12.70 (225x Hall switches + 29x 74HC165) | $12.70 |
| **Passives / Capacitors** | $1.80 (450x C0G caps) | $1.20 | $1.20 |
| **Tile Inlays & Magnets (100 pcs)** | $6.50 (100x NTAG213) | $8.00 (100x NTAG213 + 100x magnets) | $8.00 |
| **Player Racks** | $1.50 (Passive carved wood) | $10.40 (1x Active RFID + BLE + battery) | $20.80 (2x Active racks) |
| **Total Sensing BOM** | **~$26.12** | **~$40.30** | **~$50.70** |

---

## 6. Conclusion

The full 15x15 RFID antenna board remains the most elegant, senior-friendly, and cost-effective design. It allows Grandma to play completely naturally, keeps the wooden racks 100% wireless and battery-free, prevents anagram ambiguities, and saves $15–$25 on total manufacturing costs.
