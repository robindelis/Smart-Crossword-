# 13.56 MHz NFC Antenna & PCB Layout Engineering Review: `st25r3916_grid_4x4`

## 1. Executive Summary

This review analyzes the **`st25r3916_grid_4x4.kicad_pcb`** layout against official industry application notes (**STMicroelectronics AN5240, AN5276, AN6134**, NXP AN11535, and TI SLOA135).

The user's intuition is **100% physically and electrically correct**:
1. **Copper under antennas**: Placing solid copper or routing signal/power traces underneath planar NFC loop antennas induces catastrophic **eddy currents** (Lenz's Law), collapses coil inductance and Q-factor, creates inter-channel crosstalk, and severely degrades or completely kills tag read range.
2. **Traces under crystal oscillators**: Routing power rails or digital lines underneath the crystal body or oscillator pins couples switching noise directly into the high-impedance inverter input, causing clock jitter, frequency drift, or failure to oscillate.

In the current PCB layout, several critical physical violations were uncovered that would cause prototype failure or severe performance loss if manufactured without changes.

---

## 2. Industry Best Practices vs. Physical Reality

### A. NFC Loop Antenna & Ground Plane Rules (ST AN5276 / NXP AN11535)

| Design Rule | Physical Reason | Consequence of Violation |
| :--- | :--- | :--- |
| **Strict Copper Keepout on ALL Layers** | An NFC coil generates an alternating 13.56 MHz magnetic field ($H$-field) perpendicular to the PCB. Any unbroken conductive sheet (GND or power plane) behind or under the coil acts as a **shorted transformer turn**. | Eddy currents flow in opposition to the primary field (Lenz's Law). The magnetic field collapses ($B_{\text{net}} \to 0$), inductance $L$ drops by 30%–60%, Q-factor collapses from ~25 to <5, and read range drops to near zero. |
| **Zero Foreign Signal/Power Traces Under Coils** | Time-varying magnetic flux $\Phi = \int B \cdot dA$ passing through any loop or track induces electromotive force ($V = -d\Phi/dt$) and parasitic capacitive coupling. | High RF crosstalk: scanning one square energizes or corrupts adjacent squares. Power rails pick up 13.56 MHz carrier noise. |
| **Keepout Margin ($\ge 1.5\,\text{mm}$)** | The magnetic fringing field extends outside the physical outer turn ($d_{\text{out}}$). | Copper pours encroaching on the outer boundary damp the fringe field and shift resonant frequency. |
| **Ferrite Shielding Requirement** | If metal objects (battery, turntable bearing, chassis ground) must sit directly behind the board, copper cannot be used as a shield. | Only a high-permeability sintered ferrite sheet ($\mu' \approx 100\text{--}150$, $\mu'' \le 3$, e.g. Würth WE-FSFS) can redirect magnetic flux lines without generating eddy currents. |

### B. 27.12 MHz Crystal Oscillator Rules (ST AN5240 / AN6134)

| Design Rule | Physical Reason | Consequence of Violation |
| :--- | :--- | :--- |
| **No Copper Traces Directly Under Crystal Body** | The crystal package and its high-impedance input pad (`OSC_IN`) are extremely sensitive to electric field capacitive coupling. | Switching spikes and DC ripple on underlying traces inject noise directly into the oscillator tank, causing clock jitter, phase noise, or startup failure. |
| **Solid, Unbroken Ground Plane on Adjacent Layer (L2)** | A quiet, unbroken ground on Layer 2 acts as a shield between the crystal circuit and noisy inner/bottom layers. | If power traces cut slots through the ground plane beneath the crystal, the shield is destroyed and slot-aperture radiation couples into the oscillator. |
| **Symmetric, Ultra-Short Traces** | `OSC_IN` and `OSC_OUT` must match in trace length and stray capacitance to maintain crystal tank balance. | Large trace asymmetry creates unequal drive levels and phase imbalance. |
| **No Power Vias Sandwiched Between IC and Crystal** | High-current vias induce magnetic and capacitive transients. | Noise from digital and analog supplies bleeds directly into the crystal pins. |

### C. Resonant Tank Placement & Feeder Dynamics

| Design Rule | Physical Reason | Consequence of Violation |
| :--- | :--- | :--- |
| **Keep Tuning Capacitors Close to the Coils** | In a parallel resonant tank ($Q \approx 20\text{--}25$), circulating reactive current is $I_{\text{circ}} = Q \cdot I_{\text{in}}$ (up to 300–400 mA peak). | When tuning capacitors ($C_a, C_b$) are placed 80 mm away near the MUX, the entire 80 mm feeder trace carries the magnified circulating current, radiating EMI, adding ~80 nH of parasitic inductance, and detuning each cell row differently. |
| **Direct, Low-Loss RF Output (`RF_SIG`) Path** | High-frequency 13.56 MHz carrier carrying up to 1.7W output from the EMC filter requires clean impedance and low parasitics. | Jumping through 4 vias across 3 layers introduces inductive discontinuities, signal reflections, and power loss. |

---

## 3. Discrepancies Found on `st25r3916_grid_4x4.kicad_pcb`

Detailed inspection of the KiCad database (`st25r3916_grid_4x4.kicad_pcb`) reveals the following specific defects:

### 1. Solid Copper Ground Plane Directly Behind All 16 Coils on `B.Cu`
* **Finding**: `In1.Cu` has 16 rule areas (cutouts of $18.5\,\text{mm} \times 18.5\,\text{mm}$), but **`B.Cu` has NO cutouts**.
* **Impact**: `Zone 0` on `B.Cu` is a solid copper GND pour from $(1.0, 1.0)$ to $(99.0, 99.0)$. The bottom of the board directly beneath every single 17.5mm antenna coil has a solid sheet of copper just 1.6 mm away.
* **Physical Failure**: 13.56 MHz magnetic field induces massive eddy currents in the B.Cu sheet, severely collapsing inductance, tank Q-factor, and read range.

### 2. 22 Copper Traces Routed Through Antenna Coils on Inner & Bottom Layers
* **Column A**:
  * `/RF_COIL_6` on `In2.Cu` runs at $X=27.10\,\text{mm}$ directly under **Cell A1**.
  * `/RF_COIL_10` on `In2.Cu` runs at $X=27.70\,\text{mm}$ directly under **Cell A1 and Cell A2**.
  * `/RF_COIL_14` on `In2.Cu` runs at $X=28.30\,\text{mm}$ directly under **Cell A1, Cell A2, and Cell A3**.
* **Column D**:
  * `/RF_COIL_7`, `/RF_COIL_11`, `/RF_COIL_15` on `In2.Cu` run at $X=72.6\text{--}73.8\,\text{mm}$ directly under **Cells D1, D2, D3**.
  * `/RF_COIL_8`, `/RF_COIL_12`, `/RF_COIL_16` on `B.Cu` run at $X=75.6\text{--}76.8\,\text{mm}$ directly under **Cells D1, D2, D3**.
  * `/VDD_D` and `/VDD_A` power tracks on `B.Cu` cut directly across the corner of **Cell D1**.
* **Physical Failure**: Feeder traces carrying 13.56 MHz signals run directly inside the magnetic field of other cells, creating severe mutual capacitive and inductive crosstalk and detuning unselected channels.

### 3. Power Traces Running Directly Under Crystal Y1 (27.12 MHz)
* **Finding**:
  * `/VDD_D` on `B.Cu` runs at $X=77.80\,\text{mm}$ directly under the center of crystal Y1 ($X=78.00, Y=9.50$).
  * `/VDD_A` on `B.Cu` runs at $X=78.60\,\text{mm}$ directly under crystal Y1.
  * Three supply vias (`/+3.3V`, `/VDD_D`, `/VDD_A`) are dropped directly between U2 pins and Y1 pads.
* **Impact**: Digital switching noise and analog supply ripple are capacitively coupled into the 27.12 MHz oscillator circuit.

### 4. Severe Asymmetry in Crystal Oscillator Routing
* **Finding**:
  * `OSC_OUT` runs directly from U2 Pin 4 to Y1 Pad 3 (length $\approx 3.5\,\text{mm}$).
  * `OSC_IN` travels from U2 Pin 5 down around a power via, across, and back up to Y1 Pad 1 (length $\approx 9.2\,\text{mm}$, nearly $3\times$ longer).
* **Impact**: Unbalanced parasitics shift crystal pullability and load capacitance matching.

### 5. Remote Resonant Tank Placement (Long Circulating Current Paths)
* **Finding**: All 16 sets of tuning capacitors ($C_{a1}\text{--}C_{a16}, C_{b1}\text{--}C_{b16}$) and damping resistors ($R_1\text{--}R_{16}$) are clustered at the top of the board near U1 ($Y = 5\text{--}16\,\text{mm}$).
* **Impact**: For Row 4 coils (L13..L16 at $Y=90\,\text{mm}$), the distance from the tuning capacitor to the coil is $\approx 80\,\text{mm}$.
  * The entire 80mm trace carries high resonant circulating current ($I_{\text{circ}} = Q \cdot I_{\text{in}}$).
  * Adds $\approx 80\,\text{nH}$ of uncompensated trace inductance, causing a substantial inductance mismatch between Row 1 ($\approx 25\,\text{nH}$ trace) and Row 4 ($\approx 85\,\text{nH}$ trace).

### 6. Transceiver `RF_SIG` Output Via Hopping
* **Finding**: The single-ended RF drive line `RF_SIG` from C39 to U1 Pin 1 travels across 45 mm, jumping between `F.Cu` $\to$ `In2.Cu` $\to$ `B.Cu` $\to$ `In2.Cu` $\to$ `F.Cu` via 4 through-hole vias.
* **Impact**: Unnecessary inductive discontinuities and RF impedance mismatch on the primary 1.7W transmitter line.

---

## 4. Actionable Remediation Plan

To make the board fully functional and compliant with ST AN5240 / AN5276, the following modifications must be implemented in the PCB generator (`build_board.py` / `build_pcb.py`):

1. **Mirror Ground Keepouts to All Layers**:
   * Replicate the 16 rule areas ($18.5\,\text{mm} \times 18.5\,\text{mm}$) on **both `In1.Cu` and `B.Cu`** (and disallow copper fills and tracks in those regions).
2. **Reroute Feeder Tracks Outside Coil Pockets**:
   * Move the vertical feeder lines out of the coil boundaries:
     * Route Column A & B feeders through the outer left margin ($X < 12.0\,\text{mm}$) or the inter-column corridor ($X \approx 31.0\,\text{mm}$).
     * Route Column C & D feeders through the inter-column corridor ($X \approx 69.0\,\text{mm}$) or outer right margin ($X > 88.0\,\text{mm}$).
     * Keep all 16 coil areas 100% free of any other signal or power traces.
3. **Clean Crystal Oscillator Keepout**:
   * Move `/VDD_D` and `/VDD_A` power tracks on `B.Cu` away from $X=76\text{--}80\,\text{mm}$ (route them south or east of U2).
   * Ensure the region under Y1 on `B.Cu` has unbroken solid ground and zero switching traces.
   * Reroute `OSC_IN` and `OSC_OUT` symmetrically and directly, with matching lengths $\le 4\,\text{mm}$ and load capacitors placed adjacent to the crystal pins.
4. **Direct `RF_SIG` Routing**:
   * Keep `RF_SIG` on `F.Cu` as a continuous, wide (0.5 mm) microstrip trace over the `In1.Cu` ground plane directly from C39 to U1 Pin 1, eliminating all 4 layer-transition vias.
5. **Individual Coil Ground Return Traces**:
   * Route the center pad 2 of each coil out of the coil window using a dedicated, narrow radial trace on `B.Cu` or `In2.Cu` connecting to the nearest ground corridor, maintaining minimal loop area.
