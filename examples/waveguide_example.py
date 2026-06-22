"""
waveguide_example.py
Demonstrates waveguide design functions from picdesign for a SiN-on-SiO2
platform targeting visible biosensing at 660–850 nm (central λ = 780 nm).
Run this script directly or import cells into a Jupyter notebook.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from picdesign.materials import sin_refractive_index, sio2_refractive_index, v_number
from picdesign.waveguides import (
    single_mode_condition,
    confinement_factor,
    propagation_loss_db_per_cm_to_per_m,
    propagation_loss_per_m_to_db_per_cm,
    bend_loss_estimate,
    minimum_bend_radius,
)

# ── Platform parameters ──────────────────────────────────────────────────────
WAVELENGTH = 0.780   # µm — central wavelength for visible biosensing
HEIGHT = 0.220       # µm — SiN core height (220 nm, LPCVD stoichiometric)

# ── 1. Material indices ──────────────────────────────────────────────────────
n_sin = sin_refractive_index(WAVELENGTH)
n_sio2 = sio2_refractive_index(WAVELENGTH)
print(f"SiN  n({WAVELENGTH*1000:.0f} nm) = {n_sin:.4f}")
print(f"SiO2 n({WAVELENGTH*1000:.0f} nm) = {n_sio2:.4f}")

# ── 2. Single-mode width sweep ───────────────────────────────────────────────
widths = np.linspace(0.30, 1.20, 100)
sm_results = [single_mode_condition(w, HEIGHT, n_sin, n_sio2, WAVELENGTH) for w in widths]
sm_flags = [r["single_mode"] for r in sm_results]
confinements = [confinement_factor(w, HEIGHT, n_sin, n_sio2, WAVELENGTH) for w in widths]

# Find the SM/MM boundary
cutoff_width = sm_results[0]["cutoff_width_um"]
print(f"\nSingle-mode cutoff width (analytical): {cutoff_width*1000:.1f} nm")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

ax = axes[0]
ax.fill_between(widths * 1000, 0, 1, where=sm_flags, alpha=0.15, color="green", label="Single mode region")
ax.fill_between(widths * 1000, 0, 1, where=[not f for f in sm_flags], alpha=0.15, color="red", label="Multi-mode region")
ax.axvline(cutoff_width * 1000, color="k", ls="--", label=f"SM cutoff ≈ {cutoff_width*1000:.0f} nm")
ax.plot(widths * 1000, confinements, "b-", lw=2, label="Confinement factor Γ")
ax.set_xlabel("Waveguide Width (nm)")
ax.set_ylabel("Confinement Factor Γ")
ax.set_title(f"Single-mode condition & confinement\nSiN h={HEIGHT*1000:.0f} nm, λ={WAVELENGTH*1000:.0f} nm")
ax.legend(fontsize=8)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)

# ── 3. Loss conversion ───────────────────────────────────────────────────────
print("\n── Loss conversion ──")
for loss_db in [0.1, 0.5, 1.0, 2.0, 5.0]:
    alpha = propagation_loss_db_per_cm_to_per_m(loss_db)
    print(f"  {loss_db:.1f} dB/cm  →  {alpha:.1f} m⁻¹")

# ── 4. Bend loss vs radius ───────────────────────────────────────────────────
# Use a representative n_eff for a 800 nm wide SiN waveguide at 780 nm
n_eff_approx = 1.75  # estimated from FEM, typical SiN @ 780 nm TE0
radii = np.linspace(10, 200, 200)
bend_losses_per_m = [
    bend_loss_estimate(r, 0.80, n_sin, n_eff_approx, n_sio2, WAVELENGTH)
    for r in radii
]
bend_losses_db_cm = [
    propagation_loss_per_m_to_db_per_cm(a) for a in bend_losses_per_m
]

R_min = minimum_bend_radius(0.80, n_sin, n_eff_approx, n_sio2, WAVELENGTH, max_loss_db_per_cm=0.1)
print(f"\nMinimum bend radius (< 0.1 dB/cm): {R_min:.1f} µm")

ax2 = axes[1]
ax2.semilogy(radii, np.maximum(bend_losses_db_cm, 1e-6), "r-", lw=2)
ax2.axvline(R_min, color="k", ls="--", label=f"R_min ≈ {R_min:.0f} µm")
ax2.axhline(0.1, color="gray", ls=":", label="0.1 dB/cm threshold")
ax2.set_xlabel("Bend Radius (µm)")
ax2.set_ylabel("Bend Loss (dB/cm)")
ax2.set_title("Bend radiation loss vs radius\n(Marcuse model, SiN 800 nm × 220 nm)")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
# Figures are displayed only; image files are written by the notebook into the
# project images/ folder, not saved alongside the example scripts.
plt.show()
