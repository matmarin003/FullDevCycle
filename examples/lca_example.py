"""
lca_example.py
Demonstrates the LCA score calculator from picdesign for comparing
passive PIC platforms. Uses the SiN-on-SiO2 platform as the primary case.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from picdesign.lca import (
    lca_score,
    compare_platforms,
    lca_radar_data,
    SIN_VISIBLE_LCA_SCORES,
    SOI_TELECOM_LCA_SCORES,
    DEFAULT_LCA_WEIGHTS,
)

# ── 1. Score the SiN platform ─────────────────────────────────────────────────
result_sin = lca_score(SIN_VISIBLE_LCA_SCORES)
print("── SiN Visible Platform LCA ──")
print(f"  Total (weighted avg) score: {result_sin['total_score']:.2f} / 10.0")
print(f"  Dominant impact category:   {result_sin['dominant_impact']}")
print("\n  Variable breakdown:")
for var, score in SIN_VISIBLE_LCA_SCORES.items():
    bar = "█" * int(score)
    print(f"  {var:<35s}: {score:.1f}  {bar}")

# ── 2. Platform comparison ────────────────────────────────────────────────────
# Define a chalcogenide glass (ChG) mid-IR platform for comparison
chg_lca = {
    "co2_equivalent_emissions": 5.0,   # Thermal evaporation — moderate energy
    "process_energy": 4.0,             # Room-temperature deposition possible
    "water_consumption": 3.0,          # Low water use (dry deposition)
    "etch_chemistry_hazard": 7.0,      # As/Se/Ge compounds are toxic
    "wafer_yield": 6.0,                # Specialty material, lower yield
    "material_scarcity": 7.0,          # Ge, Se, As are limited supply
    "device_lifetime": 5.0,            # Sensitive to humidity and oxidation
    "packaging_burden": 7.0,           # Requires hermetic packaging
    "recyclability": 3.0,              # Relatively recoverable substrate
}

platforms = {
    "SiN (visible, 780 nm)": SIN_VISIBLE_LCA_SCORES,
    "SOI (telecom, 1550 nm)": SOI_TELECOM_LCA_SCORES,
    "ChG (mid-IR, 3000 nm)": chg_lca,
}

comparison = compare_platforms(platforms)
print("\n── Platform LCA Comparison ──")
for i, name in enumerate(comparison["ranking"], 1):
    score = comparison["scores"][name]
    print(f"  {i}. {name:<30s}: {score:.2f}")
print(f"\n  Best platform (lowest impact): {comparison['best_platform']}")

# ── 3. Radar chart — SiN platform ────────────────────────────────────────────
labels, values_sin, angles = lca_radar_data(SIN_VISIBLE_LCA_SCORES)
_, values_soi, _ = lca_radar_data(SOI_TELECOM_LCA_SCORES)
_, values_chg, _ = lca_radar_data(chg_lca)

# Short labels for the radar chart
short_labels = [
    "CO2", "Energy", "Water", "Etch\nHazard",
    "Yield", "Scarcity", "Lifetime", "Packaging", "Recyclability"
]

fig = plt.figure(figsize=(14, 5))

# Radar / spider chart
ax1 = fig.add_subplot(121, polar=True)
ax1.plot(angles, values_sin, "b-o", lw=2, label="SiN visible")
ax1.fill(angles, values_sin, alpha=0.15, color="blue")
ax1.plot(angles, values_soi, "g--s", lw=2, label="SOI telecom")
ax1.fill(angles, values_soi, alpha=0.10, color="green")
ax1.plot(angles, values_chg, "r:^", lw=2, label="ChG mid-IR")
ax1.fill(angles, values_chg, alpha=0.10, color="red")

ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(short_labels, size=8)
ax1.set_ylim(0, 10)
ax1.set_yticks([2, 4, 6, 8, 10])
ax1.set_title("LCA Impact Radar\n(lower = better)", pad=20)
ax1.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=8)

# Bar chart comparison
ax2 = fig.add_subplot(122)
x = np.arange(len(labels))
width = 0.25
ax2.bar(x - width, list(SIN_VISIBLE_LCA_SCORES.values()), width,
        label="SiN visible", color="steelblue", alpha=0.8)
ax2.bar(x, list(SOI_TELECOM_LCA_SCORES.values()), width,
        label="SOI telecom", color="seagreen", alpha=0.8)
ax2.bar(x + width, list(chg_lca.values()), width,
        label="ChG mid-IR", color="firebrick", alpha=0.8)
ax2.set_xticks(x)
ax2.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=8)
ax2.set_ylabel("LCA Impact Score (0–10)")
ax2.set_title("LCA Score per Category\n(platform comparison)")
ax2.legend(fontsize=8)
ax2.set_ylim(0, 11)
ax2.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
# Figures are displayed only; image files are written by the notebook into the
# project images/ folder, not saved alongside the example scripts.
plt.show()

# ── 4. Sensitivity analysis: vary etch chemistry weight ──────────────────────
print("\n── Sensitivity: varying etch chemistry hazard weight ──")
weights_sweep = np.linspace(0.5, 5.0, 10)
scores_vs_weight = []
for w_etch in weights_sweep:
    custom_w = {**DEFAULT_LCA_WEIGHTS, "etch_chemistry_hazard": w_etch}
    s = lca_score(SIN_VISIBLE_LCA_SCORES, custom_w)
    scores_vs_weight.append(s["total_score"])

print(f"  Score range when etch weight ∈ [0.5, 5.0]: "
      f"[{min(scores_vs_weight):.2f}, {max(scores_vs_weight):.2f}]")
