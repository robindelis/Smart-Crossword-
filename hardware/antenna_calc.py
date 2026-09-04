#!/usr/bin/env python3
"""
Smart Crossword Board - 13.56 MHz NFC Antenna Calculator
Calculates planar spiral inductor parameters for 19mm x 19mm squares using
the Modified Wheeler planar inductor model and ISO14443A matching rules.
"""

import math

def calculate_square_spiral(d_out_mm=17.5, width_mm=0.25, space_mm=0.25, turns=7, cu_thick_um=35.0):
    """
    Calculate inductance, AC resistance, and matching capacitance for a square planar coil.
    """
    mu_0 = 4.0 * math.pi * 1e-7
    f0 = 13.56e6 # 13.56 MHz
    omega = 2.0 * math.pi * f0

    d_out = d_out_mm * 1e-3
    w = width_mm * 1e-3
    s = space_mm * 1e-3
    N = float(turns)

    d_in = d_out - 2.0 * N * w - 2.0 * (N - 1.0) * s
    if d_in <= 0:
        raise ValueError(f"Turn count {turns} too high for outer diameter {d_out_mm}mm!")

    d_avg = 0.5 * (d_out + d_in)
    rho = (d_out - d_in) / (d_out + d_in)

    # Modified Wheeler coefficients for square spiral
    k1 = 2.34
    k2 = 2.75
    L = k1 * mu_0 * (N**2 * d_avg) / (1.0 + k2 * rho)

    # Resonant capacitance at 13.56 MHz
    C_res = 1.0 / (omega**2 * L)

    # Skin depth in copper at 13.56 MHz
    # rho_cu = 1.68e-8 ohm*m
    rho_cu = 1.68e-8
    skin_depth = math.sqrt(rho_cu / (math.pi * f0 * mu_0)) # ~17.8 um

    # Total conductor length
    # Approximate length = 4 * N * d_avg
    length = 4.0 * N * d_avg

    # DC resistance
    t_cu = cu_thick_um * 1e-6
    R_dc = rho_cu * length / (w * t_cu)

    # High frequency AC resistance (due to skin effect)
    eff_thick = min(t_cu, 2.0 * skin_depth)
    R_ac = rho_cu * length / (2.0 * (w + eff_thick) * skin_depth)

    # Ideal damping resistor for Q = 25
    target_Q = 25.0
    R_total_desired = (omega * L) / target_Q
    R_damp = max(0.0, R_total_desired - R_ac)

    # Actual unloaded Q
    Q_unloaded = (omega * L) / R_ac

    return {
        "turns": turns,
        "d_out_mm": d_out_mm,
        "d_in_mm": d_in * 1e3,
        "d_avg_mm": d_avg * 1e3,
        "trace_w_mm": width_mm,
        "trace_s_mm": space_mm,
        "inductance_uH": L * 1e6,
        "c_res_pF": C_res * 1e12,
        "r_dc_ohm": R_dc,
        "r_ac_ohm": R_ac,
        "q_unloaded": Q_unloaded,
        "r_damp_ohm": R_damp,
        "target_q": target_Q
    }

def print_summary(res):
    print("=" * 60)
    print(f"Smart Crossword Board - 13.56 MHz Coil Results (N={res['turns']} turns)")
    print("=" * 60)
    print(f"  Outer Dimensions:       {res['d_out_mm']:.1f} mm x {res['d_out_mm']:.1f} mm")
    print(f"  Inner Clearance:        {res['d_in_mm']:.1f} mm x {res['d_in_mm']:.1f} mm")
    print(f"  Trace Width / Spacing:  {res['trace_w_mm']:.2f} mm / {res['trace_s_mm']:.2f} mm")
    print(f"  Calculated Inductance:  {res['inductance_uH']:.3f} µH")
    print(f"  Resonant Tuning C:      {res['c_res_pF']:.1f} pF (at 13.56 MHz)")
    print(f"  DC Resistance (R_dc):   {res['r_dc_ohm']:.2f} Ω")
    print(f"  AC Resistance (R_ac):   {res['r_ac_ohm']:.2f} Ω (at 13.56 MHz)")
    print(f"  Unloaded Q-Factor:      {res['q_unloaded']:.1f}")
    print(f"  Suggested Damping Res:  {res['r_damp_ohm']:.2f} Ω (for target Q={res['target_q']})")
    print("=" * 60)

if __name__ == "__main__":
    print("Evaluating 19mm x 19mm Cell Spiral Geometry:")
    for turns in [5, 6, 7]:
        r = calculate_square_spiral(turns=turns)
        print_summary(r)
