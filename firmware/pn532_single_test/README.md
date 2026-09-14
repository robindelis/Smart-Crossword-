# PN532 Single-Antenna Sanity Test

This test verifies the physical SPI wiring between your **ESP32-S3** and **PN532 module** using the PN532's **built-in antenna coil**. It does not use the multiplexer or the 4x4 grid.

---

## 1. Hardware Wiring

| Signal | ESP32-S3 Pin | PN532 Pin | Note |
| :--- | :--- | :--- | :--- |
| **Power** | `5V` (or `VIN`) | `VDD5V` (or `5V`) | Power from USB |
| **Ground** | `GND` | `GND` | Common ground reference |
| **SCK** | `GPIO 12` | `SCK` | SPI Clock |
| **MOSI** | `GPIO 13` | `MOSI` | SPI Master Out |
| **MISO** | `GPIO 21` | `MISO` | SPI Master In |
| **CS / NSS** | `GPIO 14` | `SS` / `NSS` | SPI Chip Select |
| **IRQ** | `GPIO 10` | `INT0` / `IRQ` | Tag detect interrupt |
| **RST** | `GPIO 11` | `RST` | Hardware reset |

### Switches on PN532:
* **`SET0`** = **`L`** (Low)
* **`SET1`** = **`H`** (High)

---

## 2. Linux Serial Port Permission

If `/dev/ttyACM0` gives permission errors:
```bash
sudo chmod 666 /dev/ttyACM0
```
*(Or permanently: `sudo usermod -a -G uucp $USER` then log out and back in).*

---

## 3. Command Line Build, Flash & Monitor

Run this from the project root:
```bash
cd firmware/pn532_single_test

# Compile only
pio run

# Compile and Flash to ESP32
pio run -t upload

# Flash and immediately open Serial Monitor (Ctrl+C to exit)
pio run -t upload -t monitor
```

---

## 4. Neovim (LazyVim) Integration

### A. Autocomplete & LSP (clangd)
Generate `compile_commands.json` so Neovim's `clangd` gives full autocompletion and no red squigglies:
```bash
cd firmware/pn532_single_test
pio run -t compiledb
```

### B. Built-in Terminal
Inside Neovim, press `<Ctrl-/>` (or `<leader>ft` in LazyVim) to toggle the floating terminal and run `pio run -t upload -t monitor`.

### C. Quick Keymaps
Add to your `~/.config/nvim/lua/config/keymaps.lua`:
```lua
-- PlatformIO Shortcuts
local map = vim.keymap.set
map("n", "<leader>cb", "<cmd>!pio run<cr>", { desc = "PlatformIO: Build" })
map("n", "<leader>cu", "<cmd>!pio run -t upload<cr>", { desc = "PlatformIO: Upload" })
map("n", "<leader>cm", "<cmd>split | terminal pio device monitor<cr>", { desc = "PlatformIO: Monitor" })
```
