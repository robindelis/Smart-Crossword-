# Smart Crossword Board

A connected wooden crossword board: **older parents or grandparents play with physical wooden tiles on a board at home, while family members play their turns from an app on their phones.**

---

## What It Is

1. **Real Wooden Tiles**: 100 wooden letter tiles with hidden radio tags (NFC) inside.
2. **Simple for Older Players**: No phone needed at the board. A built-in screen and speaker announce opponent moves and show where to place tiles.
3. **Play from Anywhere**: Family members make moves and send short voice notes from their phones.
4. **Automatic Scoring**: The board checks the official dictionary and calculates double/triple scores automatically.

---

## System Overview

```
                                  [ Smart Crossword Board ]
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
[ Tile Sensors ]                       [ Screen & Audio ]                     [ Power & Turntable ]
• 15x15 (225) antenna grid             • Dual-core microcontroller            • 3.7V 3000mAh battery
• 16-channel switch chips              • 4.3" high-contrast screen            • Magnetic power cable
• 13.56 MHz NFC reader                 • 3W speaker for voice audio           • 360° turntable ring
• 100 tagged wooden tiles              • Offline dictionary in memory         • Wooden enclosure
```

---

## Repository Folders

```
.
├── AGENTS.md               # Team rules and agent list
├── README.md               # This file
├── Project_Cockpit.canvas  # Visual board for Obsidian
├── docs/                   # Project documentation, specs, sourcing & state
│   ├── PROJECT_STATE.md    # Current phase, decisions, and roadmap
│   ├── Project_Tasks.md    # Task list (Kanban format)
│   └── ...                 # RFID specs, software architecture, candidate lists
├── .agents/
│   └── agents/             # Agent guidelines (hardware, code, sales, testing)
├── commercial/             # Market research, video script, ad templates
├── hardware/               # Circuit schematics and board layouts
├── firmware/               # Microcontroller code
├── software/               # Native Android companion app
└── tests/                  # Test scripts and benchmarks
```
