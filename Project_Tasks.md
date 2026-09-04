# Project Tasks

## 📋 Backlog

- [ ] Add static electric protection to the magnetic charging port
- [ ] Buy 250mm turntable bearings to test smooth rotation
- [ ] Pick a 40mm speaker with good bass for clear voice audio
- [ ] Test screen speed with the graphics library on the display
- [ ] Design simple database for player stats and scores
- [ ] 3D model the tile trays and storage pouch

## ⏳ In Progress (Phase 1: Test Board & Code)

- [ ] Design the 4x4 test circuit board in KiCad (`hardware/`)
  - [ ] Wire NFC chip to 16-channel multiplexer switch
  - [ ] Size the antenna coils (1.5µH, 3 turns)
  - [ ] Test reading tags through 2.5mm wood
- [ ] Build 1-page test website (`software/`)
  - [ ] Show product photo and plain-language explanation
  - [ ] Add $1 pre-order Stripe button
  - [ ] Collect emails and send automated confirmation

## ✅ Done

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
