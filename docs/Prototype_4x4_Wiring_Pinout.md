# 🔌 4x4 Prototype Wiring & Pinout Guide

Complete point-to-point connection table between the **ESP32-S3 DevKit**, the **4x4 Test Grid PCB**, and the **PN532 NFC Module**.

---

## 1. Master Connection Table

| Signal | ESP32-S3 DevKit Pin | Physical ESP32 Location | 4x4 PCB Target | PN532 Module Target | Purpose / Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **+3.3V Power** | `3V3` | Left Header (Top Pin 1 or 2) | **Header J1 Pin 1 or 2** | `VCC` | 3.3V Power rail (matches logic levels) |
| **Ground** | `GND` | Left Header (Pin 3 or Bottom) | **Header J1 Pin 13, 15, 17, or 19** | `GND` | Common system ground reference |
| **MUX S0** | `GPIO 15` | Left Header | **Header J1 Pin 11** | — | CD74HC4067 Address Bit 0 (LSB) |
| **MUX S1** | `GPIO 7` | Left Header | **Header J1 Pin 9** | — | CD74HC4067 Address Bit 1 |
| **MUX S2** | `GPIO 5` | Left Header | **Header J1 Pin 5** | — | CD74HC4067 Address Bit 2 |
| **MUX S3** | `GPIO 4` | Left Header | **Header J1 Pin 3** | — | CD74HC4067 Address Bit 3 (MSB) |
| **MUX EN** | `GPIO 6` | Left Header | **Header J1 Pin 7** | — | MUX Enable (Active LOW = 0V) |
| **SPI SCK** | `GPIO 12` | Left Header | **Header J1 Pin 18** *(or direct)* | `SCK` | SPI Serial Clock |
| **SPI MOSI**| `GPIO 13` | Left Header | **Header J1 Pin 14** *(or direct)* | `MO` / `MOSI` | SPI Master Out (ESP32 $\to$ PN532) |
| **SPI MISO**| `GPIO 21` | **RIGHT Header** ⚠️ | **Header J1 Pin 20** *(or direct)* | `M` / `MI` / `MISO` | SPI Master In (PN532 $\to$ ESP32) |
| **SPI CS** | `GPIO 14` | Left Header | **Header J1 Pin 16** *(or direct)* | `SS` / `NSS` | SPI Chip Select (Active LOW) |
| **NFC RST** | `GPIO 11` | Left Header | **Header J1 Pin 12** *(or direct)* | `RST` | PN532 Hardware Reset pulse |
| **NFC IRQ** | `GPIO 10` | Left Header | **Header J1 Pin 10** *(or direct)* | `IRQ` / `INT0` | Optional Tag Detect Interrupt |
| **RF Signal**| — | — | **Port J3 Center** *(or J2 Pin 1)* | **Gold IPEX Socket** | 13.56 MHz RF Carrier Output |
| **RF Ground**| — | — | **Port J3 Outer** *(or J2 Pin 2)* | **IPEX Ground Shield**| 50Ω RF Coaxial Ground Return |

> ⚠️ **CRITICAL PIN LOCATION NOTICE**: On the **YD-ESP32-S3** board, **GPIO 21 is located on the RIGHT header** (between GPIO 47 and GPIO 20). All other control pins (`GPIO 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 3V3, GND`) are located on the **LEFT header**.

---

## 2. Header Layout Diagrams (Top View)

### A. 4x4 PCB Header J1 (Host Controller Interface - 2x10 Pins)
```
                  [ Odd Pins (Left) ]      [ Even Pins (Right) ]
   (+3.3V Power)  Pin  1: +3.3V            Pin  2: +3.3V         (+3.3V Power)
    (Address S3)  Pin  3: MUX_S3 (GPIO 4)   Pin  4: GPIO_AUX      (Spare / LED)
    (Address S2)  Pin  5: MUX_S2 (GPIO 5)   Pin  6: I2C_SDA       (Spare SDA)
    (MUX Enable)  Pin  7: MUX_EN (GPIO 6)   Pin  8: I2C_SCL       (Spare SCL)
    (Address S1)  Pin  9: MUX_S1 (GPIO 7)   Pin 10: NFC_IRQ       (GPIO 10)
    (Address S0)  Pin 11: MUX_S0 (GPIO 15)  Pin 12: NFC_RST       (GPIO 11)
        (Ground)  Pin 13: GND               Pin 14: SPI_MOSI      (GPIO 13 -> MO)
        (Ground)  Pin 15: GND               Pin 16: SPI_CS        (GPIO 14 -> SS)
        (Ground)  Pin 17: GND               Pin 18: SPI_SCK       (GPIO 12 -> SCK)
        (Ground)  Pin 19: GND               Pin 20: SPI_MISO      (GPIO 21 -> M)
```

### B. 4x4 PCB Header J2 (Transceiver Interface - 1x10 Pins)
```
   Pin  1: RF_SIG     <-- Direct RF connection (alternative to SMA J3)
   Pin  2: GND        <-- RF ground reference
   Pin  3: +3.3V      <-- Power to transceiver
   Pin  4: GND        <-- Power ground
   Pin  5: SPI_SCK    <-- Connected internally to J1 Pin 18
   Pin  6: SPI_MISO   <-- Connected internally to J1 Pin 20
   Pin  7: SPI_MOSI   <-- Connected internally to J1 Pin 14
   Pin  8: SPI_CS     <-- Connected internally to J1 Pin 16
   Pin  9: NFC_IRQ    <-- Connected internally to J1 Pin 10
   Pin 10: NFC_RST    <-- Connected internally to J1 Pin 12
```

---

## 3. Two Wiring Architecture Options

### Option A: Internal PCB Bus Routing (Cleanest)
1. Wire ESP32-S3 $\to$ Header **J1** (all power, MUX, and SPI signals).
2. Wire Header **J2** $\to$ PN532 header (the 4x4 PCB internally carries SPI between J1 and J2).
3. Connect PN532 IPEX socket $\to$ Port **J3** (or J2 Pins 1 & 2) via coaxial pigtail.

### Option B: Parallel Star Wiring (Easiest for Breadboard)
1. Keep the working SPI Dupont wires directly between **ESP32-S3** and **PN532**.
2. Run only the 7 MUX lines from **ESP32-S3** to **J1** (`3V3, GND, GPIO 15, 7, 5, 4, 6`).
3. Connect PN532 IPEX socket $\to$ Port **J3** via coaxial cable.

---

## 4. Hardware Verification Checklist
- [ ] **Power Check**: Measure 3.3V between J1 Pin 1 and J1 Pin 13 before turning on RF.
- [ ] **MUX Switch Check**: Run MUX test firmware; verify GPIO 15 toggles between 0V and 3.3V on odd/even channels.
- [ ] **Antenna Isolation**: Desolder/remove the two 0Ω bridges above the NFC logo on the PN532 module so RF energy routes 100% into the IPEX cable.
- [ ] **Channel Resistance**: Measure ~70Ω between `RF_SIG` and the active channel coil capacitor.
