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
  - [ ] Procure test bench tiles (Amazon Belgium 200-pack B0GH7LXL2K) & 15mm NTAG213 stickers
  - [ ] Verify reading tags through 2.0mm–2.5mm hardwood
  - [ ] Verify 16-channel scan latency (<40ms)

## ✅ Done

- [x] 13.56 MHz NFC Antenna Resonance & Q-Damping Theory ([`docs/LC_Resonance_and_Antenna_Theory.md`](LC_Resonance_and_Antenna_Theory.md), [`Project_Cockpit.canvas`](../Project_Cockpit.canvas))
  - [x] Derived coil inductance $L = 1.262\,\mu\text{H}$ using Modified Wheeler model for 17.5mm square coil (N=7)
  - [x] Derived tuning capacitor $C = 100\,\text{pF}$ C0G with Thomson resonance formula ($109.2\,\text{pF} - 9.2\,\text{pF}$ parasitics)
  - [x] Derived damping resistor $R = 3.3\,\Omega$ to lock loaded $Q = 25$ ($542\,\text{kHz}$ bandwidth for ISO 14443A subcarriers)
  - [x] Added theoretical group, circuit schematic diagram, and summary cards to `Project_Cockpit.canvas`
- [x] 4x4 Prototype PCB & Shopping List Hardware Compatibility Audit & Schematic Sync ([`hardware/kicad/test_grid_4x4/README.md`](../hardware/kicad/test_grid_4x4/README.md), [`Prototype_4x4_Shopping_List.md`](Prototype_4x4_Shopping_List.md))

  - [x] Verified mechanical and electrical fit for all 12 items (tiles, tags, MCU, MUX, reader, screen, audio, bearing, fasteners)
  - [x] Synchronized `test_grid_4x4.kicad_sch` to match the perfected zero-DRC layout of `test_grid_4x4.kicad_pcb`
  - [x] Documented integration notes for CD74HC4067 SOIC-24 PCBA vs Amazon DIP breakout and PN532 RF stage tap
  - [x] Recorded FAIL-011 and ADL-021
- [x] DataLoom Dynamic Procurement Spreadsheets & Candidate Sourcing Sync ([`Prototype_4x4_Shopping_List.loom`](Prototype_4x4_Shopping_List.loom), [`Production_15x15_Sourcing_List.loom`](Production_15x15_Sourcing_List.loom), [`Prototype_4x4_Shopping_List.md`](Prototype_4x4_Shopping_List.md), [`Production_15x15_Sourcing_List.md`](Production_15x15_Sourcing_List.md), [`Procurement_Shopping_List.md`](Procurement_Shopping_List.md))

  - [x] Generated native Obsidian DataLoom (.loom) files validated with DataLoom's internal deserializer
  - [x] Updated Prototype (4x4) Shopping List with top picks across all 12 items (€69.47 allocated / €125.47 pack checkout total)
  - [x] Updated Production (15x15) Sourcing List with top picks across all 12 items ($67.87 BOM per unit)
  - [x] Synchronized master Procurement_Shopping_List.md with DataLoom embeds and quick-reference tables
  - [x] Validated 100% of e-commerce links via `verify_ecommerce_links.py` (FAIL-010 compliance)
- [x] Multi-Candidate Component Sourcing & Comparison Table ([`Component_Candidate_Comparison.md`](Component_Candidate_Comparison.md), [`Project_Cockpit.canvas`](../Project_Cockpit.canvas))
  - [x] Evaluated 2–4 top candidate options for all 9 components (tiles, NFC tags, readers, MCUs, multiplexers, turntables, displays, audio, fasteners)
  - [x] Verified 100% of e-commerce links live via `verify_ecommerce_links.py` (FAIL-010 compliance)
  - [x] Added comparison card and visual edges to Obsidian Canvas `group-procurement` section
  - [x] Benchmarked prototype bench budget (€69.47) and mass production target ($67.87)
- [x] Web Sourcing Scout & Automated Live Link Verification Engine (`.agents/agents/web_sourcing.md`, `scripts/verify_ecommerce_links.py`)
  - [x] Enforced local-first search hierarchy (Amazon BE priority, surrounding EU, specialized stores)
  - [x] Real-link live validation tool with browser headers, price/stock extraction, and CI test suite (`tests/test_link_verification.py`)
  - [x] Verified in-stock procurement options: Amazon Belgium 200-pack tiles (€6.99, ASIN: `B0GH7LXL2K`) and NTAG213 tags
  - [x] Added FAIL-010 to living memory and ADL-015 to decisions log
- [x] Wooden Scrabble tiles & 15mm NTAG213 RFID sourcing strategy (`commercial/tile_and_rfid_sourcing.md`)
  - [x] Benchmarked wholesale/retail pricing (AliExpress, Alibaba, Amazon, Panda, CXJ RFID)
  - [x] Multi-language distributions (EN 100, FR 102, DE 102, NL 102, ES 100 FISE)
  - [x] Selected 15mm diameter NTAG213 paper stickers ($0.035 ea) over 12mm and epoxy tags
  - [x] Enforced localized single-language bag fulfillment + $25 Kickstarter add-ons
  - [x] Balanced $6.52 turnkey tile subsystem within $70–$100 BOM budget
- [x] 3D CAD models for 4x4 test enclosure & NFC tiles (`hardware/cad/`)
  - [x] FreeCAD automation specialist agent (`.agents/agents/cad.md`)
  - [x] Base chassis tray with M3 bosses and header cutouts (`output/base_enclosure.*`)
  - [x] Top grid faceplate with 1.2mm ribs and 1.5mm RF floor (`output/top_grid_plate.*`)
  - [x] Prototype NFC letter tile with 15.5mm coin tag cavity (`output/nfc_tile_prototype.*`)
  - [x] Master 3D assembly and STEP exchange (`output/assembly_4x4_prototype.*`)
  - [x] Automated test suite with 100% pass rate (`tests/test_cad_models.py`)
  - [x] Continuous learning log with 11 technical invariants (`hardware/cad/cad_lessons.md`)
- [x] Design 4x4 test circuit board in KiCad (`hardware/kicad/test_grid_4x4/`)
  - [x] Sized planar spiral coils (17.5mm, 7 turns, L=1.26µH, 19mm pitch)
  - [x] Resonant LC tank (100pF C0G capacitors, 3.3Ω damping resistors for Q=25)
  - [x] 16-channel analog multiplexer (CD74HC4067) with address control
  - [x] ESP32 host controller header (J1 2x10) and NFC transceiver header (J2 1x10)
  - [x] SMA 50Ω coaxial test port (J3) for oscilloscope/VNA bench testing
  - [x] 4-layer PCB layout with GND keepouts under coils to preserve Q
  - [x] Automated 4-layer routing pass in KiCad 10: 0 violations, 0 unconnected items
  - [x] KiCad project, schematic, board layout, and 3D preview render verified
- [x] Portable C crossword game engine (`firmware/engine/crossword_engine.c`)
  - [x] Move rules: straight line, continuity, connectivity, center star requirement
  - [x] Official 15x15 bonus multipliers (Double/Triple letter & word, Bingo +50)
  - [x] Multi-language support (English, French, Dutch, German, Spanish)
  - [x] Official tournament dictionaries downloaded & integrated (2.1M total words)
  - [x] Language-specific tile bags & letter scoring tables
  - [x] Native C test suite with 100% pass rate (`tests/test_engine.c`)
- [x] Native Android Companion App (`software/android/`)
  - [x] Interactive 4x4 test grid with 2W, 3W, 2L, 3L & center star bonus multipliers
  - [x] Embedded English tournament referee with 168k dictionary in assets
  - [x] Unique username generator (`name#1234`) and physical board pairing (`board_scb8492`)
  - [x] Local-first SQLite database with session exclusivity and ADB inspector script
  - [x] Firebase Authentication and Google Play Services Sign-In integration
  - [x] 15 JVM unit tests and 6 on-device hardware instrumented tests
- [x] Market research and competitor breakdown (`commercial/market_analysis.md`)
- [x] Pre-launch $1 deposit plan and ad templates (`commercial/prelaunch_playbook.md`)
- [x] Kickstarter video script (`commercial/kickstarter_video_script.md`)
- [x] Agent team setup and rules (`AGENTS.md`)
- [x] Core rules and technical limits recorded (`.agents/agents/wise.md`)
- [x] Project state and decision log (`PROJECT_STATE.md`)
- [x] Git repo initialized on main
- [x] Obsidian vault and visual board setup (`Project_Cockpit.canvas`)
