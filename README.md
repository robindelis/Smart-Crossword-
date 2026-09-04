# Smart Crossword Board 🔠🪵

A connected luxury wooden crossword board that bridges generations: **elderly parents and grandparents play with tactile wooden tiles in their living room, while adult children and grandchildren play moves from their smartphones across the world.**

---

## The Vision
Modern digital games leave aging parents behind, trapped in isolated screen apps or missing their family. The **Smart Crossword Board** restores the warmth of heirloom wooden board games while embedding cutting-edge electronics underneath:
* **Real Tactile Play**: 100 solid wooden letter tiles with invisible embedded NFC tags.
* **Zero Tech Friction for Seniors**: No smartphones, pairing codes, or app updates required for the senior. The board features an integrated high-contrast console and warm, human voice announcements.
* **Family Connection Across Distances**: Family members take turns on an iOS/Android mobile app, sending short voice love notes that play through the board's speaker when moves arrive.
* **Automated Official Scoring & Validation**: Automatically validates words against official tournament dictionaries and tallies double/triple letter and word scores in milliseconds—eliminating math friction and arguments.

---

## Technical Architecture

```
                                  [ Smart Crossword Board ]
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
[ Sensing Subsystem ]              [ Compute & Console ]                  [ Power & Mechanics ]
• 15x15 (225) NFC Coil Matrix      • ESP32-S3 / Dual-Core SoC             • 3.7V 3000mAh Li-ion
• Analog MUX Tree (74HC4067)       • 4.0"–5.0" High-Contrast IPS          • Magnetic Quick-Disconnect
• 13.56 MHz Transceiver            • 3W Speaker Chamber + I2S DAC         • 360° Ball-Bearing Turntable
• 100 NFC-tagged Wooden Tiles      • Embedded Trie Dictionary             • Solid Hardwood CNC Chassis
```

---

## Repository Structure

```
.
├── AGENTS.md               # Master orchestrator & specialist agent roster
├── PROJECT_STATE.md        # Roadmap, active milestones, and decision log
├── README.md               # Product overview and system architecture
├── .agents/
│   └── agents/             # Specialist agent personas & instructions
│       ├── wise.md         # Living memory & architectural invariants
│       ├── hardware.md     # RF antenna, electronics, PCB layout, chassis CAD
│       ├── firmware.md     # Embedded engine, Trie dictionary, audio, LVGL
│       ├── mobile_cloud.md # iOS/Android app, MQTT broker, push notifications
│       ├── emotional_ux.md # Senior human factors, acoustics, visual contrast
│       ├── commercial.md   # Kickstarter strategy, BOM modeling, video scripts
│       └── qa.md           # RF signal integrity, bench test protocols, fuzzing
├── hardware/               # KiCad schematics, PCB antenna layouts, CAD files
├── firmware/               # Microcontroller C++ / ESP-IDF source code
├── software/               # Cloud sync server & mobile companion app
└── tests/                  # Test suites, dictionary benchmarks, RF test tools
```

---

## Multi-Agent Development Team

This project operates with a dedicated multi-agent development fleet coordinated via [AGENTS.md](file:///home/robin/Smart-Crossword-Board/AGENTS.md). Refer to `.agents/agents/` for domain specialist roles and constraints.
