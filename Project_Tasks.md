# Project Tasks

## 📋 Backlog

- [ ] Add static electric protection to the magnetic charging port
- [ ] Buy 250mm turntable bearings to test smooth rotation
- [ ] Pick a 40mm speaker with good bass for clear voice audio
- [ ] Test screen speed with the graphics library on the display
- [ ] Design simple database for player stats and scores
- [ ] 3D model the tile trays and storage pouch

## ⏳ In Progress (Phase 1: Test Board & Code)

- [ ] Build 1-page test website (`software/`)
  - [ ] Show product photo and plain-language explanation
  - [ ] Add $1 pre-order Stripe button
  - [ ] Collect emails and send automated confirmation
- [ ] Bench test 4x4 circuit board
  - [ ] Order PCB prototype from JLCPCB
  - [ ] Verify reading tags through 2.0mm–2.5mm hardwood
  - [ ] Verify 16-channel scan latency (<40ms)

## ✅ Done

- [x] Design 4x4 test circuit board in KiCad (`hardware/kicad/test_grid_4x4/`)
  - [x] Sized planar spiral coils (17.5mm, 7 turns, L=1.26µH, 19mm pitch)
  - [x] Resonant LC tank (100pF C0G capacitors, 3.3Ω damping resistors for Q=25)
  - [x] 16-channel analog multiplexer (CD74HC4067) with address control
  - [x] ESP32 host controller header (J1 2x10) and NFC transceiver header (J2 1x10)
  - [x] SMA 50Ω coaxial test port (J3) for oscilloscope/VNA bench testing
  - [x] 4-layer PCB layout with GND keepouts under coils to preserve Q
  - [x] KiCad project, schematic, board layout, and 3D preview render verified
- [x] Portable C crossword game engine (`firmware/engine/crossword_engine.c`)
  - [x] Move rules: straight line, continuity, connectivity, center star requirement
  - [x] Official 15x15 bonus multipliers (Double/Triple letter & word, Bingo +50)
  - [x] Multi-language support (English, French, Dutch, German, Spanish)
  - [x] Official tournament dictionaries downloaded & integrated (2.1M total words)
  - [x] Language-specific tile bags & letter scoring tables
  - [x] Native C test suite with 100% pass rate (`tests/test_engine.c`)
- [x] WebAssembly compilation via clang (`software/web/engine.wasm`)
- [x] Interactive web prototype with multi-language selector & localized voice referee (`software/web/index.html`)
- [x] Market research and competitor breakdown (`commercial/market_analysis.md`)
- [x] Pre-launch $1 deposit plan and ad templates (`commercial/prelaunch_playbook.md`)
- [x] Kickstarter video script (`commercial/kickstarter_video_script.md`)
- [x] Agent team setup and rules (`AGENTS.md`)
- [x] Core rules and technical limits recorded (`.agents/agents/wise.md`)
- [x] Project state and decision log (`PROJECT_STATE.md`)
- [x] Git repo initialized on main
- [x] Obsidian vault and visual board setup (`Project_Cockpit.canvas`)
