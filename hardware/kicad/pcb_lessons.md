# Living Memory: PCB & RF Layout Lessons

This document records technical invariants, electromagnetic design rules, KiCad Python automation techniques, routing topologies, and component isolation principles discovered during development of the Smart Crossword Board hardware.

---

## 1. Planar Spiral Antenna & RF Matrix Invariants

* **LESSON-PCB-001 (Planar Spiral Antenna Inner Terminal Escape & Center Aperture)**:
  * *Topological Constraint*: In a multi-turn planar spiral coil, the inner terminal is topologically trapped inside concentric conductor loops; getting back to ground or transceiver circuitry requires an underpass or layer crossover.
  * *The "Dead Center" Trap*: Routing the inner terminal to the dead center $(xc, yc)$ of the coil introduces a long return trace ($16.75\,\text{mm}$ in a $19\,\text{mm}$ grid), crosses turns at a $45^\circ$ diagonal, increases mutual inductive coupling ($\cos 45^\circ = 0.707$), and clutters the primary magnetic flux core.
  * *The "Direct Turn Via" Trap*: Placing a via directly on the 7th (innermost) turn wire causes DRC clearance violations ($0.075\,\text{mm} < 0.15\,\text{mm}$) because the turn pitch ($0.50\,\text{mm} = 0.25\,\text{mm}$ track + $0.25\,\text{mm}$ space) is smaller than standard annular rings ($0.60\,\text{mm}$ pad diameter).
  * *Reliable Invariant*:
    1. Step the inner via pad ($\varnothing 0.6\,\text{mm}$ pad, $\varnothing 0.3\,\text{mm}$ drill) $1.3\,\text{mm}$ into the inner cavity from the innermost turn (e.g. `(xc ± 3.8, yc - 3.8)`). This guarantees $>0.90\,\text{mm}$ clearance to all surrounding turns ($6\times$ minimum DRC requirement).
    2. Route the return underpass on the opposite layer (`B.Cu`) strictly perpendicular ($90^\circ$, $\cos 90^\circ = 0$, nullifying mutual inductance) across the turns directly into the perimeter ground mesh.
    3. This cuts trace length by 67% ($5.7\,\text{mm}$ vs $16.75\,\text{mm}$) and leaves the central $8.0 \times 8.0\,\text{mm}$ aperture 100% clear of all copper across all 4 layers, maximizing unobstructed magnetic flux $\Phi$ for ISO 14443A tag coupling.

* **LESSON-PCB-002 (Eddy Current Cancellation & Copper Keepouts Under 13.56 MHz Coils)**:
  * *Symptom/Physics*: Copper planes (ground or power) directly beneath planar 13.56 MHz loop antennas act as shorted secondary transformer turns. Alternating magnetic flux induces circulating eddy currents (Lenz's Law) that generate an opposing magnetic field, collapsing coil inductance $L$ and killing the tank quality factor $Q$.
  * *Reliable Invariant*: Enforce 100% copper keepout windows across ALL layers (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`) beneath every antenna coil, extending at least $\ge 1.5\,\text{mm}$ beyond the outermost turn (e.g. $18.0 \times 18.0\,\text{mm}$ keepout for a $17.5 \times 17.5\,\text{mm}$ coil).
  * *Ground Mesh Continuity*: In a $19.0\,\text{mm}$ pitch grid, an $18.0\,\text{mm}$ keepout leaves continuous $1.0\,\text{mm}$ ground mesh corridors between all rows and columns, providing low-impedance ground returns without degrading coil resonance.

* **LESSON-PCB-003 (Foreign Feeder Track Avoidance & Crosstalk Corridors)**:
  * *Symptom/Physics*: Feeder lines from neighboring coils routed underneath active antenna coils induce strong mutual capacitive and inductive crosstalk, causing false tag reads and degraded SNR across adjacent matrix channels.
  * *Reliable Invariant*: All feeder lines must run strictly in perimeter margins or dedicated inter-column alleys between keepouts:
    * Column A: Left board margin ($X \in [10.45..12.10]\,\text{mm}$, clear of $X \le 12.5\,\text{mm}$).
    * Column B: Alley A-B ($X \in [30.55..31.88]\,\text{mm}$).
    * Column C: Alley C-D ($X \in [68.45..69.50]\,\text{mm}$).
    * Column D: Right board margin ($X \in [87.12..89.00]\,\text{mm}$).
  * *Planar Routing Invariant*: In dense multiplexed arrays, planar routing on a single layer (`In2.Cu`) can be maintained with zero layer-hopping vias by staggering entry coordinates and aligning lanes outside keepout boundaries.

* **LESSON-PCB-004 (Continuous Top-Layer Microstrip for Primary RF Path)**:
  * *Symptom/Physics*: Layer-transition vias on the primary $13.56\,\text{MHz}$ RF line between transceiver output (ST25R3916 Pin 1) and matching network/SMA test port introduce parasitic via inductance ($0.5–1.2\,\text{nH}$ each) and impedance discontinuities that degrade return loss and detune filter performance.
  * *Reliable Invariant*: Route `RF_SIG` entirely on `F.Cu` as a continuous top-layer microstrip line referenced to the unbroken `In1.Cu` ground plane with zero layer-hopping vias.

---

## 2. High-Frequency Clock & Component Isolation

* **LESSON-PCB-005 (RF Shielding vs Power/Signal Routing Under 27.12 MHz Crystals)**:
  * *Symptom/Error*: Fast-switching digital or analog power traces (`VDD_D`, `VDD_A`) directly underneath a 27.12 MHz crystal body or load capacitors inject high-frequency switching ripple into high-impedance `OSC_IN`, creating phase noise, clock jitter, and transceiver instability.
  * *The Common Misconception*: Beginners often assume that "no traces under crystal" means removing all copper, including ground planes.
  * *Reliable Invariant*:
    1. Signal & Power Tracks: Strictly forbidden under the crystal footprint and load capacitors on all layers.
    2. Ground Plane: An unbroken, solid ground plane on Layer 2 (`In1.Cu`) directly beneath the crystal is **mandatory** (per ST AN2867 / AN5240). It acts as an electrostatic shield against internal PCB noise, provides an ultra-low-inductance return path for crystal load capacitors, and prevents slot-antenna radiation from ground voids.
    3. Route `OSC_IN` and `OSC_OUT` symmetrically with direct, matched paths $\le 4\,\text{mm}$.

---

## 3. KiCad Python API & Automation Invariants

* **LESSON-PCB-006 (KiCad Python 3.14 SWIG API Iteration Invariant)**:
  * *Symptom/Error*: In Python 3.14+, calling `.next()` or iterating over KiCad SWIG collections (`board.GetTracks()`, `board.Footprints()`) crashes with:
    `AttributeError: 'SwigPyIterator' object has no attribute 'next'`
  * *Root Cause*: Python 3.14 removed deprecated iteration protocol hooks relied on by older SWIG wrapper bindings.
  * *Reliable Invariant*: Always index KiCad SWIG sequences using bracket/range indexing:
    ```python
    tracks = [board.GetTracks()[i] for i in range(len(board.GetTracks()))]
    footprints = [board.Footprints()[i] for i in range(len(board.Footprints()))]
    ```

* **LESSON-PCB-007 (QFN Micro-Pitch Via Fanout Clearance)**:
  * *Symptom/Error*: Dropping standard $0.50\,\text{mm}$ vias directly adjacent to $0.50\,\text{mm}$-pitch QFN pads (e.g. ST25R3916B-AQFT 32-pin QFN) causes DRC clearance violations ($< 0.15\,\text{mm}$) with adjacent pins and copper tracks.
  * *Reliable Invariant*: Fan out escape traces at least $0.80\,\text{mm}$ beyond the QFN package courtyard before dropping layer-transition vias. Maintain manufacturer-compliant annular rings ($\varnothing 0.30\,\text{mm}$ drill, $\varnothing 0.50\,\text{mm}$ pad).
