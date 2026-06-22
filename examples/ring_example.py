"""
ring_example.py
Demonstrates ring resonator design functions from picdesign.
Covers FSR targeting, Q-factor estimation, and transmission spectrum.
Platform: SiN-on-SiO2, λ = 780 nm, visible biosensing application.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from picdesign.materials import sin_refractive_index, sio2_refractive_index
from picdesign.resonators import (
    ring_fsr,
    ring_fsr_group,
    ring_circumference,
    ring_radius_from_fsr,
    ring_q_factor,
    ring_transmission,
)
from picdesign.dispersion import effective_mode_area

# ── Platform parameters ──────────────────────────────────────────────────────
WAVELENGTH = 0.780   # µm
n_eff = 1.75         # approximate TE0 effective index (SiN 800 × 220 nm at 780 nm)
n_g = 1.92           # approximate group index (includes waveguide dispersion)

# ── 1. FSR for different ring radii ─────────────────────────────────────────
print("── FSR sweep (effective index model) ──")
radii = [10, 20, 30, 50, 75, 100]
for R in radii:
    fsr = ring_fsr(n_eff, R, WAVELENGTH)
    fsr_g = ring_fsr_group(n_g, R, WAVELENGTH)
    C = ring_circumference(R)
    print(f"  R = {R:4d} µm | C = {C:6.1f} µm | FSR (n_eff) = {fsr:.3f} nm | FSR (n_g) = {fsr_g:.3f} nm")

# ── 2. Design for target FSR ─────────────────────────────────────────────────
TARGET_FSR_NM = 5.0   # nm — desired channel spacing for sensing
R_needed = ring_radius_from_fsr(n_eff, TARGET_FSR_NM, WAVELENGTH)
print(f"\nFor FSR = {TARGET_FSR_NM} nm → required radius: {R_needed:.2f} µm")
print(f"  Circumference: {ring_circumference(R_needed):.2f} µm")

# ── 3. Q factor from linewidth ───────────────────────────────────────────────
# Typical SiN ring at 780 nm: Q ~ 50 000–500 000
LINEWIDTH_NM = 0.015  # nm (15 pm → Q ≈ 52 000)
q_result = ring_q_factor(WAVELENGTH, TARGET_FSR_NM, LINEWIDTH_NM)
print(f"\nQ factor (Δλ = {LINEWIDTH_NM*1000:.0f} pm): {q_result['Q']:.0f}")
print(f"Finesse:                        {q_result['finesse']:.0f}")

# ── 4. Transmission spectrum ─────────────────────────────────────────────────
RESONANCE_NM = 780.0
wavelengths_nm = np.linspace(777, 783, 5000)

# Over-coupled (r = 0.95, a = 0.995) — deep dip at resonance
T_over = ring_transmission(wavelengths_nm, RESONANCE_NM,
                            r_coupling=0.95, alpha_roundtrip=0.995)

# Critical coupling (r = a) — full extinction
T_crit = ring_transmission(wavelengths_nm, RESONANCE_NM,
                            r_coupling=0.98, alpha_roundtrip=0.98)

# Under-coupled (r = 0.995, a = 0.97) — shallow dip
T_under = ring_transmission(wavelengths_nm, RESONANCE_NM,
                             r_coupling=0.995, alpha_roundtrip=0.97)

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

ax = axes[0]
ax.plot(wavelengths_nm, T_over, label="Over-coupled (r=0.95, a=0.995)", lw=1.5)
ax.plot(wavelengths_nm, T_crit, label="Critical coupling (r=a=0.98)", lw=1.5, ls="--")
ax.plot(wavelengths_nm, T_under, label="Under-coupled (r=0.995, a=0.97)", lw=1.5, ls=":")
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Through-port Transmission")
ax.set_title(f"Ring resonator transmission spectrum\n(resonance @ {RESONANCE_NM} nm)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── 5. FSR vs radius plot ─────────────────────────────────────────────────────
r_arr = np.linspace(5, 150, 300)
fsr_arr_eff = np.array([ring_fsr(n_eff, r, WAVELENGTH) for r in r_arr])
fsr_arr_grp = np.array([ring_fsr_group(n_g, r, WAVELENGTH) for r in r_arr])

ax2 = axes[1]
ax2.plot(r_arr, fsr_arr_eff, label=f"FSR (n_eff = {n_eff})", lw=2)
ax2.plot(r_arr, fsr_arr_grp, label=f"FSR (n_g = {n_g})", lw=2, ls="--")
ax2.axhline(TARGET_FSR_NM, color="gray", ls=":", label=f"Target FSR = {TARGET_FSR_NM} nm")
ax2.axvline(R_needed, color="red", ls="--", alpha=0.6, label=f"R = {R_needed:.1f} µm")
ax2.set_xlabel("Ring Radius (µm)")
ax2.set_ylabel("FSR (nm)")
ax2.set_title("FSR vs Ring Radius — SiN Biosensor")
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
# Figures are displayed only; image files are written by the notebook into the
# project images/ folder, not saved alongside the example scripts.
plt.show()
