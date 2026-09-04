# Project State: Smart Crossword Board

## Current Phase
**Phase 1: Test Board and Game Engine**

---

## Roadmap

```mermaid
gantt
    title Project Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1: Test Board & Code
    Team setup & rules                   :done, p1, 2026-09-04, 1d
    Kickstarter market plan              :done, p2, 2026-09-04, 1d
    Obsidian board & tasks               :done, p2b, 2026-09-04, 1d
    Game engine in C & WebAssembly       :done, p3, 2026-09-04, 1d
    Interactive web prototype            :done, p3b, 2026-09-04, 1d
    4x4 test circuit board               :active, p4, 2026-09-05, 7d
    1-page test website ($1 pre-orders)  :p5, 2026-09-12, 5d
    section Phase 2: Full Board & Screen
    Full 15x15 circuit board             :p6, 2026-09-20, 14d
    Screen code & speaker setup          :p7, 2026-09-27, 14d
    section Phase 3: Phone App & Launch
    Phone app & server sync              :p8, 2026-10-10, 14d
    Kickstarter launch                   :p9, 2026-10-24, 14d
```

---

## Decisions Log

| ID | Date | Topic | Decision & Reason |
| :--- | :--- | :--- | :--- |
| **ADL-001** | 2026-09-04 | Tile Sensors | **15x15 NFC sensor grid**: Reads all 100 wooden letter tiles through solid wood without wires or camera arms. |
| **ADL-002** | 2026-09-04 | Who Plays | **Parent on board, family on phone**: Lets family play together from anywhere without forcing older players to use an app. |
| **ADL-003** | 2026-09-04 | Screen & Voice | **Built-in screen & speaker**: Announces moves out loud and shows letters on screen so older players never need a phone. |
| **ADL-004** | 2026-09-04 | Power & Spin | **Turntable with battery backup**: Spins smoothly on ball bearings; stays plugged in with a magnetic cable or runs 4 hours on battery. |
| **ADL-005** | 2026-09-04 | How to Launch | **Kickstarter campaign**: Sell pre-orders to adult kids looking for a gift for their parents to fund the first production run. |
| **ADL-006** | 2026-09-04 | Checking Demand | **$1 pre-order deposits**: Get 750 $1 deposits and keep ad cost under $2.50 per email before ordering production boards. |
| **ADL-007** | 2026-09-04 | Project Tracking | **Obsidian (Canvas & Task list)**: Keeps all notes and tasks in simple Markdown files on your computer with a visual whiteboard. |
| **ADL-008** | 2026-09-04 | Game Engine Architecture | **Portable C Shared Core (WebAssembly + ESP32)**: Write core Scrabble rule checks and scoring once in clean C with zero OS dependencies; compiles to `engine.wasm` for web and compiles directly to ESP-IDF firmware for the physical board. |
| **ADL-009** | 2026-09-04 | Multi-Language Support | **5 Official Tournament Languages**: Built-in support for English (ENABLE1, 168k words), French (ODS8, 402k words), Dutch (OpenTaal, 337k words), German (Scrabble DE, 590k words), and Spanish (FISE, 635k words), with official tile distributions, language-specific letter scoring, and localized voice synthesis referee announcements. |

---

## Next Tasks
1. Design the 4x4 test circuit board in KiCad (`hardware/`).
2. Build the 1-page test website with $1 pre-order button (`software/`).
3. Connect physical NFC multiplexing bench driver to C engine.
