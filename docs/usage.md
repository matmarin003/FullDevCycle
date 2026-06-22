# picdesign — Usage Guide

**Course:** UNAL-BSU PIC Design, Spring 2025  
**Author:** Mateo Marin  
**Platform:** SiN-on-SiO2 passive integrated photonics (visible biosensing, 660–850 nm)

---

## Quick install

```bash
cd pic-design-common-library
pip install -r requirements.txt
```

## Package structure

```
picdesign/
├── materials.py       Sellmeier models — SiN, SiO2, V-number
├── waveguides.py      Single-mode, confinement, loss conversion, bend loss
├── resonators.py      Ring FSR, Q factor, transmission spectrum
├── interferometers.py MZI FSR, ΔL, transmission, sensitivity
├── couplers.py        Directional coupler, Y-branch, grating, edge coupler
├── dispersion.py      Group index, GVD, β₂, γ, A_eff
├── lca.py             LCA score calculator and platform comparison
└── gds_helpers.py     gdstk GDS layout generation and export
```

---

## Core function reference

### materials.py

| Function | Description | Returns |
|---|---|---|
| `sin_refractive_index(λ)` | SiN Sellmeier (Luke 2015) | n (float) |
| `sio2_refractive_index(λ)` | SiO2 Malitson Sellmeier | n (float) |
| `v_number(w, h, n_c, n_cl, λ)` | Normalised frequency V | V (float) |
| `numerical_aperture(n_c, n_cl)` | Waveguide NA | NA (float) |

### waveguides.py

| Function | Description | Returns |
|---|---|---|
| `single_mode_condition(w, h, n_c, n_cl, λ)` | SM check per dimension | dict |
| `confinement_factor(w, h, n_c, n_cl, λ)` | Fraction of power in core | Γ (float) |
| `propagation_loss_db_per_cm_to_per_m(α_dB)` | dB/cm → m⁻¹ | α (float) |
| `propagation_loss_per_m_to_db_per_cm(α)` | m⁻¹ → dB/cm | α_dB (float) |
| `bend_loss_estimate(R, w, n_c, n_eff, n_cl, λ)` | Marcuse bend loss | α_bend m⁻¹ |
| `minimum_bend_radius(w, n_c, n_eff, n_cl, λ, max_loss)` | Min R for target loss | R_min µm |

### resonators.py

| Function | Description | Returns |
|---|---|---|
| `ring_fsr(n_eff, R, λ)` | FSR from effective index | FSR nm |
| `ring_fsr_group(n_g, R, λ)` | FSR from group index | FSR nm |
| `ring_circumference(R)` | Round-trip path length | C µm |
| `ring_radius_from_fsr(n_eff, FSR, λ)` | Invert FSR formula | R µm |
| `ring_q_factor(λ, FSR, Δλ)` | Quality factor and finesse | dict |
| `ring_transmission(λ_arr, λ_res, r, a)` | Through-port spectrum | T array |

### interferometers.py

| Function | Description | Returns |
|---|---|---|
| `mzi_fsr(n_eff, ΔL, λ)` | MZI FSR | FSR nm |
| `mzi_path_length_imbalance(FSR, n_eff, λ)` | ΔL from target FSR | ΔL µm |
| `mzi_transmission(λ_arr, ΔL, n_eff, loss)` | Transmission spectrum | T array |
| `mzi_sensitivity(n_eff, ΔL, λ, dn/dC)` | Biosensor sensitivity | nm/RIU |
| `mzi_arm_lengths(ΔL, L_common)` | Individual arm lengths | dict |

### couplers.py

| Function | Description | Returns |
|---|---|---|
| `directional_coupler_length(κ, ratio)` | Coupling length | L µm |
| `directional_coupler_kappa(gap, w, n_c, n_cl, λ)` | Coupling coefficient | κ µm⁻¹ |
| `grating_coupler_period(λ, n_eff, θ, n_env)` | Grating period Λ | Λ µm |
| `edge_coupler_taper_length(w1, w2, n_c, n_cl, λ, α_taper)` | Adiabatic taper length | L µm |
| `y_branch_arm_spacing(λ, n_c, n_cl, w)` | Min centre-centre spacing | s µm |

### dispersion.py

| Function | Description | Returns |
|---|---|---|
| `group_index(n_eff_arr, λ_arr)` | n_g(λ) via finite differences | array |
| `gvd_coefficient(n_eff_arr, λ_arr)` | D(λ) dispersion parameter | array |
| `beta2_from_D(D, λ)` | D → β₂ (ps²/km) | float |
| `D_from_beta2(β₂, λ)` | β₂ → D (ps/(nm·km)) | float |
| `nonlinear_coefficient(n₂, λ, A_eff)` | γ (W⁻¹m⁻¹) | float |
| `effective_mode_area(w, h, Γ)` | A_eff geometric estimate | µm² |

### lca.py

| Function | Description | Returns |
|---|---|---|
| `lca_score(variables, weights)` | Weighted LCA total score | dict |
| `compare_platforms(platforms, weights)` | Cross-platform ranking | dict |
| `lca_radar_data(variables)` | Data for radar chart | tuple |

### gds_helpers.py

| Function | Description | Returns |
|---|---|---|
| `straight_waveguide(lib, name, L, w)` | Straight waveguide cell | gdstk.Cell |
| `ring_resonator_cell(lib, name, R, w, gap, L_bus)` | Ring + bus cell | gdstk.Cell |
| `mzi_cell(lib, name, ΔL, L_arm, w)` | MZI layout cell | gdstk.Cell |
| `full_biosensor_layout(filename, ...)` | Complete chip GDS | gdstk.Library |
| `export_component(cell, filename)` | Single-cell GDS export | None |
| `sin_strip_technology(λ, w, h, ...)` | SiN-on-SiO2 strip technology for PhotonForge | photonforge.Technology |

---

## PhotonForge / Tidy3D component builders

These functions return **`photonforge.Component`** objects (geometry + ports) for layout,
GDS export, and Tidy3D simulation. Set an active technology first:
`pf.config.default_technology = sin_strip_technology()`. The `photonforge`/`tidy3d`
packages are imported lazily, so the analytical functions above keep `numpy` as their
only dependency.

| Function | Description | Ports |
|---|---|---|
| `grating_coupler_component(period_um, n_teeth, ...)` | Surface grating coupler (fan-out taper + tooth array) | `P0` |
| `directional_coupler_component(gap_um, coupling_length_um, ...)` | 4-port S-bend directional coupler | `P0`–`P3` |
| `y_branch_component(arm_spacing_um, ...)` | 1×2 Y-branch splitter | `P0` (in), `P1`/`P2` (out) |
| `edge_coupler_component(tip_width_um, full_width_um, length_um)` | Inverse-taper edge coupler | `P0` (bus side) |
| `ring_resonator_component(radius_um, gap_um, ...)` | All-pass ring + bus | `P0` (in), `P1` (through) |
| `mzi_component(delta_L_um, arm_length_um, ...)` | MZI: input → split → two arms → combine → output | `P0` (in), `P1` (out) |

```python
import photonforge as pf
from picdesign import (sin_strip_technology, grating_coupler_period,
                       grating_coupler_component, ring_resonator_component)

pf.config.default_technology = sin_strip_technology(wavelength_um=0.780)
period = grating_coupler_period(0.780, 1.78, theta_deg=10.0)

ring = ring_resonator_component(radius_um=20.0, gap_um=0.20)   # ports P0, P1
circuit = pf.Component("RING_GC")
ref = circuit.add_reference(ring)
for p in ("P0", "P1"):                                          # grating-couple both ports
    gc = grating_coupler_component(period_um=period, name=f"GC_{p}")
    circuit.add_reference(gc).connect("P0", ref[p])
circuit.write_gds("ring_grating.gds")
```

See `examples/grating_coupler_example.py`, `ring_layout_example.py`,
`mzi_layout_example.py`, `y_branch_example.py`, `directional_coupler_example.py`,
and `edge_coupler_example.py` for complete grating-coupled assemblies.

---

## Layer conventions

| Layer name | GDS (layer, datatype) | Description |
|---|---|---|
| WG_CORE | (1, 0) | SiN waveguide core |
| WG_CLAD | (2, 0) | SiO2 upper cladding (if patterned) |
| CHIP_EDGE | (10, 0) | Chip boundary / dicing lane |

---

## Design example: SiN biosensor at 780 nm

```python
from picdesign import *

# Material indices
n_sin  = sin_refractive_index(0.780)   # ≈ 2.00
n_sio2 = sio2_refractive_index(0.780)  # ≈ 1.45

# Check single-mode condition for 800 nm wide, 220 nm tall SiN waveguide
sm = single_mode_condition(0.80, 0.22, n_sin, n_sio2, 0.780)
print("Single mode:", sm["single_mode"])

# Design ring with 5 nm FSR
R = ring_radius_from_fsr(1.75, 5.0, 0.780)  # ≈ 13.8 µm

# Design MZI with 10 nm FSR
dL = mzi_path_length_imbalance(10.0, 1.75, 0.780)  # ≈ 33.8 µm

# Export full biosensor GDS
lib = full_biosensor_layout("biosensor_780nm.gds")
```

---

## Relation to previous homeworks

| Homework | Components reused |
|---|---|
| HW2 (Tarea2) | Mode solver logic → `waveguides.single_mode_condition`; MMI geometry → `couplers` |
| HW3 (Tarea3) | Multi-device layout pattern → `gds_helpers.full_biosensor_layout` |
| HW4 | Ring resonator, MZI, Y-branch, grating coupler → `resonators`, `interferometers`, `gds_helpers` |
