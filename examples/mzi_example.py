"""
mzi_example.py
Demonstrates MZI design and biosensing performance from picdesign.
Platform: SiN-on-SiO2, λ = 660–850 nm, biosensing application.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from picdesign.interferometers import (
    mzi_fsr,
    mzi_path_length_imbalance,
    mzi_transmission,
    mzi_sensitivity,
    mzi_arm_lengths,
)
from picdesign.waveguides import propagation_loss_db_per_cm_to_per_m

# ── Platform parameters ──────────────────────────────────────────────────────
WAVELENGTH = 0.780   # µm
n_eff = 1.75         # TE0 effective index (SiN 800 × 220 nm @ 780 nm)
PROP_LOSS_DB_CM = 0.5  # typical SiN propagation loss (dB/cm)

# ── 1. ΔL sweep: FSR vs path imbalance ──────────────────────────────────────
print("── MZI FSR vs path-length imbalance ──")
delta_Ls = [50, 100, 200, 500, 1000]  # µm
for dL in delta_Ls:
    fsr = mzi_fsr(n_eff, dL, WAVELENGTH)
    print(f"  ΔL = {dL:5d} µm  →  FSR = {fsr:.3f} nm")

# ── 2. Design for target FSR ─────────────────────────────────────────────────
TARGET_FSR_NM = 10.0  # nm — one MZI fringe per 10 nm for sensing
dL_needed = mzi_path_length_imbalance(TARGET_FSR_NM, n_eff, WAVELENGTH)
arms = mzi_arm_lengths(dL_needed, common_length_um=200.0)
print(f"\nFor FSR = {TARGET_FSR_NM} nm:")
print(f"  ΔL needed = {dL_needed:.1f} µm")
print(f"  L1 (reference) = {arms['L1_um']:.1f} µm")
print(f"  L2 (sensing)   = {arms['L2_um']:.1f} µm")

# ── 3. Transmission spectra — lossless vs lossy ──────────────────────────────
wavelengths_nm = np.linspace(750, 810, 2000)
T_ideal = mzi_transmission(wavelengths_nm, dL_needed, n_eff, loss_db_per_cm=0.0)
T_lossy = mzi_transmission(wavelengths_nm, dL_needed, n_eff, loss_db_per_cm=PROP_LOSS_DB_CM)

fig, axes = plt.subplots(1, 3, figsize=(16, 4))

ax = axes[0]
ax.plot(wavelengths_nm, T_ideal, label="Lossless", lw=1.5)
ax.plot(wavelengths_nm, T_lossy, label=f"With loss ({PROP_LOSS_DB_CM} dB/cm)", lw=1.5, ls="--")
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Transmission")
ax.set_title(f"MZI transmission\nΔL = {dL_needed:.0f} µm, n_eff = {n_eff}")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# ── 4. Refractive-index shift sensitivity (biosensing) ───────────────────────
print("\n── Biosensing sensitivity vs ΔL ──")
dL_arr = np.linspace(50, 1000, 200)
sensitivities = [mzi_sensitivity(n_eff, dL, WAVELENGTH, dn_dC=0.20) for dL in dL_arr]

ax2 = axes[1]
ax2.plot(dL_arr, sensitivities, "g-", lw=2)
ax2.set_xlabel("Path-length imbalance ΔL (µm)")
ax2.set_ylabel("Wavelength sensitivity (nm/RIU)")
ax2.set_title("MZI sensor sensitivity vs ΔL\n(dn_eff/dn_analyte = 0.20)")
ax2.grid(True, alpha=0.3)

S_opt = mzi_sensitivity(n_eff, dL_needed, WAVELENGTH, dn_dC=0.20)
print(f"  Sensitivity at ΔL = {dL_needed:.0f} µm: {S_opt:.1f} nm/RIU")

# ── 5. Visible range FSR comparison for three ΔL values ─────────────────────
wl_range = np.linspace(660, 850, 1000)
fig_labels = ["ΔL = 100 µm", "ΔL = 200 µm", "ΔL = 500 µm"]
dL_vals = [100, 200, 500]

ax3 = axes[2]
for dL_val, label in zip(dL_vals, fig_labels):
    T = mzi_transmission(wl_range, dL_val, n_eff)
    ax3.plot(wl_range, T, label=label, lw=1.5)
ax3.set_xlabel("Wavelength (nm)")
ax3.set_ylabel("Transmission")
ax3.set_title("MZI spectral response\nacross visible biosensing range")
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
# Figures are displayed only; image files are written by the notebook into the
# project images/ folder, not saved alongside the example scripts.
plt.show()
