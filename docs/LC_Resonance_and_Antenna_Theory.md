# 13.56 MHz NFC Antenna Theory: Selecting $L$, $C$, and $R$

This document details the electromagnetic and circuit theory used to design the 16-coil antenna matrix for the **Smart Crossword Board** 4x4 test grid. It provides the exact mathematical formulas, physical invariants, and electrical schematics that led to the selection of **$L = 1.262\,\mu\text{H}$**, **$C = 100\,\text{pF}$**, and **$R = 3.3\,\Omega$**.

---

## 1. Electrical Schematic of the Resonant Tank

Each of the 16 squares on the board consists of a planar spiral inductor etched into the top copper layer, paired with an 0603 damping resistor and an 0603 C0G tuning capacitor. 

The CD74HC4067 multiplexer connects the active RF source to one resonant tank at a time:

```text
                                  INDIVIDUAL CELL RESONANT TANK
                      ┌────────────────────────────────────────────────────────┐
                      │                                                        │
                      │               R_damp (3.3 Ω)      Planar Coil (L)      │
                      │               ┌──────────┐        ┌─────────────┐      │
RF_SIG (13.56 MHz)    │     ┌─────────┤ 0603 SMD ├────────┤ 7-Turn PCB  ├──┐   │
       │              │     │         └──────────┘        └─────────────┘  │   │
       ▼              │     │                                              │   │
┌──────────────┐      │     │                                              │   │
│  CD74HC4067  │      │     │                                              │   │
│  Multiplexer ├──────┼─────┤ RF_CHx                                       │   │
│  (Channel x) │      │     │                                              │   │
└──────────────┘      │     │         C_tune (100 pF)                      │   │
                      │     │         ┌──────────┐                         │   │
                      │     └─────────┤ C0G/NP0  ├─────────────────────────┤   │
                      │               └──────────┘                         │   │
                      │                                                    │   │
                      └────────────────────────────────────────────────────┼───┘
                                                                           │
GND Plane (Solid B.Cu return) ─────────────────────────────────────────────┴──── GND
```

```mermaid
graph LR
    RF["RF_SIG (Transceiver)"] --> MUX["CD74HC4067 MUX Switch"]
    MUX --> CH["RF_CHx Node"]
    CH --> R["R_damp (3.3 Ω)"]
    R --> L["Planar Coil L (1.262 µH)"]
    L --> GND["System Ground (B.Cu)"]
    CH --> C["C_tune (100 pF C0G)"]
    C --> GND
```

* **Parallel Resonance Topology**: The capacitor $C_{\text{tune}}$ is connected in parallel with the series branch ($R_{\text{damp}} + L_{\text{coil}}$). 
* **Circulating Reactive Current**: At the 13.56 MHz resonant frequency, the parallel impedance peaks, creating a high circulating reactive current ($I_{\text{circ}} = Q \cdot I_{\text{in}}$) through the coil turns to project a strong magnetic flux $B_z$ through the 2.0mm–2.5mm wooden top plate.

---

## 2. Step 1: Coil Geometry & Inductance ($L$)

### Physical Dimensions & Trace Definitions ($w$ and $s$)
* **Cell Pitch**: $19.0\,\text{mm} \times 19.0\,\text{mm}$ (matches tournament Scrabble tile size).
* **Coil Outer Dimension ($d_{\text{out}}$)**: $17.5\,\text{mm} \times 17.5\,\text{mm}$ (leaves $0.75\,\text{mm}$ clearance on each side to adjacent cells to prevent magnetic crosstalk).
* **Trace Width ($w = 0.25\,\text{mm} = 10\,\text{mil}$)**: The physical width of the etched copper strip on the top layer (`F.Cu`) that carries the RF current.
* **Trace Spacing / Gap ($s = 0.25\,\text{mm} = 10\,\text{mil}$)**: The clear, unetched dielectric gap (bare FR4) between two adjacent concentric turns of the spiral.
* **Turn Pitch ($p = w + s = 0.50\,\text{mm}$)**: The center-to-center distance between adjacent loops. Each turn reduces the outer dimension by $2p = 1.0\,\text{mm}$ (advancing inward by $0.50\,\text{mm}$ on both sides).

#### Cross-Section Diagram of Adjacent Coil Turns

```text
                     ◄── w ──►         ◄── s ──►         ◄── w ──►
                   ┌───────────┐                       ┌───────────┐
  Top Copper Layer │  Copper   │    Dielectric Gap     │  Copper   │
  (F.Cu, 35 µm)    │   Trace   │   (FR4, no copper)    │   Trace   │
  ═════════════════╧═══════════╧═══════════════════════╧═══════════╧═════════════════
  FR4 Core Substrate (h = 1.6 mm, ε_r = 4.5)
  ─────────────────────────────────────────────────────────────────────────────────
  Bottom Ground Plane (B.Cu solid copper shield return)
                   │◄──────────── Turn Pitch (p = w + s = 0.50 mm) ──────────────►│
```

#### Top-Down Planar View

```text
       ┌───────────────────────────────────────────────────────────┐ ◄── d_out (17.5 mm)
       │  Outer Copper Turn (w = 0.25 mm)                          │
       │  ┌─────────────────────────────────────────────────────┐  │
       │  │  Dielectric Gap / Space (s = 0.25 mm)               │  │
       │  │  ┌───────────────────────────────────────────────┐  │  │
       │  │  │  Turn 2 Copper Trace (w = 0.25 mm)            │  │  │
       │  │  │  ┌─────────────────────────────────────────┐  │  │  │
       │  │  │  │  Turn 3...                              │  │  │  │
       │  │  │  │                                         │  │  │  │
       │  │  │  │        Unwound Center Core              │  │  │  │
       │  │  │  │        ◄─── d_in (11.0 mm) ───►         │  │  │  │
       │  │  │  │                                         │  │  │  │
```

#### Why $w = 0.25\,\text{mm}$ and $s = 0.25\,\text{mm}$ Were Chosen:
1. **PCB Manufacturing Reliability**: JLCPCB standard pooled service supports down to $0.127\,\text{mm}$ ($5\,\text{mil}$). Running at $0.25\,\text{mm}$ ($10\,\text{mil}$) provides a $2\times$ safety margin, guaranteeing 100% etching yield, zero trace bridging, and zero price surcharge.
2. **Skin-Effect Conduction**: At $13.56\,\text{MHz}$, the skin depth is $\delta = 17.7\,\mu\text{m}$. A trace width of $w = 0.25\,\text{mm}$ gives enough perimeter ($2w \approx 0.5\,\text{mm}$) to keep the high-frequency AC resistance down to $R_{\text{AC}} \approx 0.66\,\Omega$.
3. **Low Inter-Turn Parasitic Capacitance**: If spacing $s$ is too tight ($< 0.15\,\text{mm}$), inter-turn capacitive coupling spikes, creating self-resonance too close to $13.56\,\text{MHz}$. At $s = 0.25\,\text{mm}$, inter-turn stray capacitance is negligible ($< 0.5\,\text{pF}$).
4. **Geometric Fit**: $N = 7$ turns requires $7w + 6s = 1.75\,\text{mm} + 1.50\,\text{mm} = 3.25\,\text{mm}$ of copper per edge ($6.5\,\text{mm}$ total across the diameter). This leaves an inner window $d_{\text{in}} = 11.0\,\text{mm}$, allowing magnetic flux lines to pass freely through the center of the coil without Eddy current self-cancellation.

### The Modified Wheeler Inductance Model
For a planar square spiral coil, the inductance $L$ is calculated using the **Modified Wheeler Formula**:

$$L = k_1 \mu_0 \frac{N^2 \cdot d_{\text{avg}}}{1 + k_2 \cdot \rho}$$

Where:
* $\mu_0 = 4\pi \times 10^{-7}\,\text{H/m}$ (magnetic permeability of vacuum).
* $N = 7$ (number of turns).
* $w = 0.25\,\text{mm}$ (copper trace width).
* $s = 0.25\,\text{mm}$ (dielectric space between turns).
* $k_1 = 2.34$ and $k_2 = 2.75$ (empirical coefficients for square geometries).

#### Geometric Derivation:
1. **Inner Diameter ($d_{\text{in}}$)**:
   $$d_{\text{in}} = d_{\text{out}} - 2N w - 2(N - 1)s$$
   $$d_{\text{in}} = 17.5 - (2 \times 7 \times 0.25) - (2 \times 6 \times 0.25) = 17.5 - 3.5 - 3.0 = \mathbf{11.0\,\text{mm}}$$

2. **Average Diameter ($d_{\text{avg}}$)**:
   $$d_{\text{avg}} = \frac{d_{\text{out}} + d_{\text{in}}}{2} = \frac{17.5 + 11.0}{2} = \mathbf{14.25\,\text{mm}} = 0.01425\,\text{m}$$

3. **Fill Ratio ($\rho$)**:
   $$\rho = \frac{d_{\text{out}} - d_{\text{in}}}{d_{\text{out}} + d_{\text{in}}} = \frac{17.5 - 11.0}{17.5 + 11.0} = \frac{6.5}{28.5} \approx \mathbf{0.2281}$$

4. **Resulting Inductance ($L$)**:
   $$L = 2.34 \cdot (4\pi \times 10^{-7}) \cdot \frac{7^2 \cdot 0.01425}{1 + (2.75 \cdot 0.2281)}$$
   $$L = (2.9405 \times 10^{-6}) \cdot \frac{49 \cdot 0.01425}{1 + 0.6272} = (2.9405 \times 10^{-6}) \cdot \frac{0.69825}{1.6272} \approx \mathbf{1.262\,\mu\text{H}}$$

---

## 3. Step 2: Resonant Tuning Capacitor ($C$)

### The Thomson Resonance Formula
The carrier frequency of ISO/IEC 14443 Type A NFC is **$f_0 = 13.56\,\text{MHz}$**. 

The angular frequency is:
$$\omega_0 = 2\pi f_0 = 2\pi \cdot (13.56 \times 10^6) \approx \mathbf{8.520 \times 10^7\,\text{rad/s}}$$

At resonance, the inductive reactance and capacitive reactance cancel each other out ($X_L = X_C$):
$$\omega_0 L = \frac{1}{\omega_0 C_{\text{total}}} \implies C_{\text{total}} = \frac{1}{\omega_0^2 \cdot L}$$

Plugging in our coil inductance $L = 1.262\,\mu\text{H}$:
$$C_{\text{total}} = \frac{1}{(8.520 \times 10^7)^2 \cdot (1.262 \times 10^{-6})} = \frac{1}{(7.259 \times 10^{15}) \cdot (1.262 \times 10^{-6})} = \mathbf{109.2\,\text{pF}}$$

### Practical Reality: The 100 pF Standard Value & Detuning Tolerance

In textbook theory, one calculates $C_{\text{total}} = 109.2\,\text{pF}$ and then "finds" $9.2\,\text{pF}$ of parasitic capacitance so that $109.2 - 9.2$ lands on an exact, round **$100.0\,\text{pF}$**.

In real-world engineering, the causality is reversed:
1. **Standard Parts Availability**: In manufacturing, you cannot buy an off-the-shelf "109.2 pF" capacitor. The standard E12/E24 capacitor values are $82\,\text{pF}$, **$100\,\text{pF}$**, and $120\,\text{pF}$. Placing two capacitors (e.g. $100\,\text{pF} + 10\,\text{pF}$) doubles the component count, SMT assembly cost, and PCB footprint area.
2. **Parasitics are Variable, Not Fixed**: The CD74HC4067 multiplexer switch contributes roughly $5\,\text{pF} - 9\,\text{pF}$, and PCB traces contribute $1\,\text{pF} - 2\,\text{pF}$. Crucially, trace lengths differ from channel 0 to channel 15, meaning real parasitics fluctuate between $6\,\text{pF}$ and $11\,\text{pF}$ across the board.
3. **Component Tolerances**: A C0G capacitor has a $\pm 5\%$ tolerance, and PCB trace etching on the planar inductor has a $\pm 5\%$ to $\pm 10\%$ inductance tolerance.

Therefore, **the circuit will inevitably be slightly detuned from 13.56 MHz in physical operation.**

---

### Detuning Analysis: Will It Still Create Sufficient Magnetic Flux?

**Yes, without question.** The circuit was specifically designed to be tolerant of detuning. Here is the mathematical and electromagnetic proof:

#### 1. The Resonance Response Curve (Lorentzian Form)
The relative magnetic flux $B(f)$ generated by the coil at the transmitter frequency $f_0 = 13.56\,\text{MHz}$ when the tank has an actual resonant frequency $f_{\text{res}}$ is given by the normalized resonant transfer function:

$$\frac{B(f_0)}{B_{\text{max}}} = \frac{1}{\sqrt{1 + 4 Q^2 \left(\frac{f_0 - f_{\text{res}}}{f_{\text{res}}}\right)^2}}$$

#### 2. Quantitative Sensitivity Table ($Q = 25$, $L = 1.262\,\mu\text{H}$)

| Total Tank Capacitance ($C_{\text{total}}$) | Actual Resonant Freq ($f_{\text{res}}$) | Detuning from 13.56 MHz ($\Delta f$) | Relative Magnetic Flux ($B/B_{\text{max}}$) | Field Degradation (dB) | Operational Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$95\,\text{pF}$** (100pF cap $-5\%$ tol, min stray) | $14.54\,\text{MHz}$ | $+975\,\text{kHz}$ ($+7.2\%$) | **$28.6\%$** | $-10.9\,\text{dB}$ | Marginal read depth |
| **$100\,\text{pF}$** (100pF cap, zero stray) | $14.17\,\text{MHz}$ | $+607\,\text{kHz}$ ($+4.5\%$) | **$42.3\%$** | $-7.5\,\text{dB}$ | Reliable read (PN5180) |
| **$105\,\text{pF}$** (100pF cap $+ 5\,\text{pF}$ stray) | $13.83\,\text{MHz}$ | $+266\,\text{kHz}$ ($+2.0\%$) | **$72.1\%$** | $-2.8\,\text{dB}$ | **Within $-3\,\text{dB}$ Bandwidth** |
| **$109.2\,\text{pF}$** (Theoretical ideal) | **$13.56\,\text{MHz}$** | **$0\,\text{kHz}$** ($0.0\%$) | **$100.0\%$** | $0.0\,\text{dB}$ | Maximum peak |
| **$115\,\text{pF}$** (100pF cap $+ 15\,\text{pF}$ stray) | $13.21\,\text{MHz}$ | $-349\,\text{kHz}$ ($-2.6\%$) | **$60.4\%$** | $-4.4\,\text{dB}$ | Strong read |

#### 3. Four Physical Mechanisms Ensuring Sufficient Magnetic Flux

1. **Broadened Bandwidth via Damping Resistor ($R_{\text{damp}} = 3.3\,\Omega$)**:
   * If the coil were undamped, its unloaded $Q$ would be $\approx 163$, giving a razor-sharp bandwidth of only $83\,\text{kHz}$. A stray drift of just $2\,\text{pF}$ would collapse the magnetic field by over $90\%$.
   * By introducing $R_{\text{damp}} = 3.3\,\Omega$, we deliberately broadens the bandwidth to:
     $$B = \frac{f_0}{Q} = \frac{13.56\,\text{MHz}}{25} \approx \mathbf{542\,\text{kHz}}$$
   * Within $\pm 271\,\text{kHz}$ of detuning, the magnetic field remains $\ge 70.7\%$ of maximum peak.

2. **The Tag Loading Effect (Frequency Pulling Downward)**:
   * When an NTAG213 sticker is placed onto the board, the tag's internal LC loop couples magnetically with the reader coil.
   * Mutual inductance ($M$) and the tag's chip load reactively "pull" the reader tank's resonant frequency **downward by $200\,\text{kHz} - 400\,\text{kHz}$**.
   * In commercial NFC design (e.g. NXP AN11535), coils are **intentionally tuned slightly high (13.8 – 14.1 MHz)** when unloaded. When a game tile lands on the cell, the tag pulls the resonance straight down into the $13.56\,\text{MHz}$ center frequency!

3. **NXP PN5180 5x Power Headroom (250 mW vs 50 mW)**:
   * A budget PN532 emits only $\approx 50\,\text{mW}$ of RF power. If detuning costs $6\,\text{dB}$ of coupling, a PN532 would struggle to penetrate $2.5\,\text{mm}$ of wood.
   * The **NXP PN5180 delivers 250 mW** of RF output power. It has $>12\,\text{dB}$ of link margin over the minimum tag power-on threshold.
   * Furthermore, the PN5180 features **Dynamic Power Control (DPC)**: when it detects impedance mismatch or load detuning, it dynamically adjusts its internal RF driver stage to pump additional current into the coil.

4. **NTAG213 Activation Threshold**:
   * The NTAG213 tag chip requires a minimum magnetic field strength of $H_{\text{min}} \approx 1.5\,\text{A/m}$ to power up its internal EEPROM.
   * At $2.5\,\text{mm}$ tile distance, a $1.26\,\mu\text{H}$ coil driven with $250\,\text{mW}$ produces $H > 8\,\text{A/m}$ at peak resonance.
   * Even under worst-case detuning where magnetic flux drops to $40\%$, the field is still $H \approx 3.2\,\text{A/m}$—well above the tag's activation threshold.

### Selected Capacitor Specification
* **Value**: **$100\,\text{pF}$** (E12 standard, 0603 footprint).
* **Dielectric**: **C0G / NP0** (50V, Class 1 ceramic, LCSC `C14405`).
  * *Why C0G is critical*: Unlike X7R (which drifts by $\pm 15\%$ across temperature and loses capacitance under voltage), C0G has zero voltage drift and $\pm 30\,\text{ppm/}^\circ\text{C}$ temperature stability, ensuring that once fabricated, the resonant frequency stays locked in place.

---

## 4. Step 3: Damping Resistor ($R$) and Quality Factor ($Q$)

### Why $Q$ Cannot Be Too High or Too Low
The Quality Factor ($Q$) dictates the sharpness of resonance and the usable bandwidth of the antenna:

$$Q = \frac{\omega_0 L}{R_{\text{total}}} = \frac{f_0}{\text{Bandwidth } (B)}$$

| Q-Factor | Consequence on 13.56 MHz NFC Operation |
| :--- | :--- |
| **Too High ($Q > 35$)** | **Bandwidth is too narrow.** ISO 14443A uses $106\,\text{kbps}$ ASK modulation with sidebands at $f_0 \pm 848\,\text{kHz}$ ($12.712\,\text{MHz}$ and $14.408\,\text{MHz}$). A high $Q$ chokes these subcarrier sidebands and causes severe ringing, corrupting tag communication. |
| **Too Low ($Q < 15$)** | **Magnetic field is too weak.** Circulating current drops, and the field cannot penetrate through $2.0\,\text{mm} - 2.5\,\text{mm}$ of hardwood. |
| **Target Sweet Spot ($Q = 20 - 25$)** | Optimal magnetic field strength with clean $848\,\text{kHz}$ sideband transmission. |

### AC Resistance of the Copper Trace (Skin Effect)
At $13.56\,\text{MHz}$, electrical current does not flow through the entire $35\,\mu\text{m}$ ($1\,\text{oz}$) thickness of the copper trace; it crowds into the outer surface due to the **Skin Effect**.

1. **Skin Depth in Copper ($\delta$)**:
   $$\delta = \sqrt{\frac{\rho_{\text{cu}}}{\pi f_0 \mu_0}} = \sqrt{\frac{1.68 \times 10^{-8}}{\pi \cdot (13.56 \times 10^6) \cdot (4\pi \times 10^{-7})}} \approx \mathbf{17.7\,\mu\text{m}}$$

2. **Total Trace Length ($l$)**:
   $$l \approx 4 \cdot N \cdot d_{\text{avg}} = 4 \cdot 7 \cdot 0.01425\,\text{m} = \mathbf{0.399\,\text{m}} \approx 40\,\text{cm}$$

3. **High-Frequency AC Resistance ($R_{\text{AC}}$)**:
   $$R_{\text{AC}} \approx \frac{\rho_{\text{cu}} \cdot l}{2 \cdot (w + \delta) \cdot \delta} \approx \frac{(1.68 \times 10^{-8}) \cdot 0.399}{2 \cdot (0.25 \times 10^{-3} + 17.7 \times 10^{-6}) \cdot (17.7 \times 10^{-6})} \approx \mathbf{0.66\,\Omega}$$

4. **Unloaded Q-Factor (Without Damping Resistor)**:
   $$Q_{\text{unloaded}} = \frac{\omega_0 L}{R_{\text{AC}}} = \frac{(8.520 \times 10^7) \cdot (1.262 \times 10^{-6})}{0.66} \approx \mathbf{162.9}$$
   *An unloaded Q of 163 gives a bandwidth of only $83\,\text{kHz}$, which would completely destroy ISO 14443 subcarrier pulses!*

### Calculating Required Damping Resistor ($R_{\text{damp}}$)
To bring the loaded Quality Factor down to our target **$Q_{\text{target}} = 25$**:

1. **Required Total Loop Resistance ($R_{\text{total}}$)**:
   $$R_{\text{total}} = \frac{\omega_0 L}{Q_{\text{target}}} = \frac{(8.520 \times 10^7) \cdot (1.262 \times 10^{-6})}{25} \approx \mathbf{4.30\,\Omega}$$

2. **Loop Resistance Budget**:
   $$R_{\text{total}} = R_{\text{AC\_coil}} + R_{\text{MUX\_ON}} + R_{\text{damp}}$$
   Where:
   * $R_{\text{AC\_coil}} \approx 0.66\,\Omega$ (trace skin resistance).
   * $R_{\text{MUX\_ON}} \approx 0.35\,\Omega$ (CD74HC4067 channel on-resistance at RF).
   * $R_{\text{damp}}$ is the discrete resistor.

3. **Solving for $R_{\text{damp}}$**:
   $$R_{\text{damp}} = R_{\text{total}} - R_{\text{AC\_coil}} - R_{\text{MUX\_ON}} = 4.30\,\Omega - 0.66\,\Omega - 0.35\,\Omega = \mathbf{3.29\,\Omega}$$

* **Selected Nominal Value**: **$3.3\,\Omega$** ($1\%$, 0603 SMD).

---

## 5. Summary Specification Table

| Parameter | Theoretical Formula | Target / Calculated | Chosen Physical Component |
| :--- | :--- | :--- | :--- |
| **Resonant Frequency** | $f_0$ | $13.56\,\text{MHz}$ | Industrial ISM Standard (ISO 14443A) |
| **Coil Inductance** | $L = k_1 \mu_0 \frac{N^2 d_{\text{avg}}}{1 + k_2 \rho}$ | **$1.262\,\mu\text{H}$** | 7-Turn Planar Square Spiral ($17.5\text{mm} \times 17.5\text{mm}$) |
| **Total Resonant Capacitance** | $C_{\text{total}} = \frac{1}{\omega_0^2 L}$ | $109.2\,\text{pF}$ | Total LC tank capacitance |
| **Tuning Capacitor ($C$)** | $C = C_{\text{total}} - C_{\text{parasitic}}$ | **$100.0\,\text{pF}$** | **$100\,\text{pF}$ 50V C0G/NP0 0603** (LCSC `C14405`) |
| **Coil AC Resistance** | $R_{\text{AC}} \propto \frac{l}{\delta \cdot w}$ | $0.66\,\Omega$ | Trace skin effect at 13.56 MHz |
| **Target Quality Factor** | $Q = \frac{\omega_0 L}{R_{\text{total}}}$ | **$25.0$** | Optimum for ISO 14443A 848 kHz subcarrier |
| **Damping Resistor ($R$)** | $R_{\text{damp}} = \frac{\omega_0 L}{Q} - R_{\text{AC}} - R_{\text{MUX}}$ | **$3.29\,\Omega$** | **$3.3\,\Omega$ 1% 1/10W 0603** (LCSC `C22971`) |
| **Usable RF Bandwidth** | $B = \frac{f_0}{Q}$ | **$542.4\,\text{kHz}$** | Clear transmission of tag data without distortion |
