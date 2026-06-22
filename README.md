# pic-design-common-library

**UNAL-BSU PIC Design Course — Spring 2025**  
**Author:** Mateo Marin  
**Homework 5 — Part 2**

A reusable Python library of analytical and GDS-generation functions for **passive** silicon nitride (SiN) integrated photonic circuits. Developed and tested for visible biosensing at **660–850 nm** on a **SiN-on-SiO2** platform.

> All functions are strictly passive — no doping, carrier injection, thermal tuning, or active modulation.

---

## Installation

```bash
pip install -r requirements.txt
```

Required packages: `numpy`, `scipy`, `matplotlib`, `gdstk`

---

## Quick start

```python
from picdesign import (
    sin_refractive_index, sio2_refractive_index,
    single_mode_condition, confinement_factor,
    ring_fsr, ring_radius_from_fsr,
    mzi_path_length_imbalance, mzi_transmission,
    lca_score, SIN_VISIBLE_LCA_SCORES,
    full_biosensor_layout,
)

# Material indices at 780 nm
n_sin  = sin_refractive_index(0.780)   # 2.001
n_sio2 = sio2_refractive_index(0.780)  # 1.453

# Verify single-mode condition for 800 × 220 nm waveguide
sm = single_mode_condition(0.80, 0.22, n_sin, n_sio2, 0.780)
print("Single mode:", sm["single_mode"])  # True

# Design ring for 5 nm FSR
R = ring_radius_from_fsr(1.75, 5.0, 0.780)   # 13.8 µm

# Design MZI for 10 nm FSR
dL = mzi_path_length_imbalance(10.0, 1.75, 0.780)  # 33.8 µm

# Export full biosensor GDS
lib = full_biosensor_layout("biosensor_780nm.gds", ring_radius_um=R, mzi_delta_L_um=dL)
```

---

## Library modules

| Module | Contents |
|---|---|
| `materials.py` | Sellmeier models for SiN (Luke 2015) and SiO2 (Malitson); V-number |
| `waveguides.py` | Single-mode condition, confinement factor, loss conversion, bend loss & minimum radius |
| `resonators.py` | Ring FSR (effective & group index), Q factor, finesse, through-port transmission; **PhotonForge `ring_resonator_component`** |
| `interferometers.py` | MZI FSR, path-length imbalance, transmission spectrum, biosensing sensitivity; **PhotonForge `mzi_component`** (input → split → two arms → combine → output) |
| `couplers.py` | Directional coupler (CMT), Y-branch spacing, grating coupler period, edge coupler taper; **PhotonForge `grating_coupler_component`, `directional_coupler_component`, `y_branch_component`, `edge_coupler_component`** |
| `dispersion.py` | Group index, GVD coefficient D, β₂ ↔ D conversion, γ, A_eff |
| `lca.py` | Weighted LCA score calculator, platform comparison, radar chart data |
| `gds_helpers.py` | gdstk cells: straight waveguide, ring resonator, MZI, full chip layout; **PhotonForge `sin_strip_technology`** |

### PhotonForge / Tidy3D component builders

In addition to the analytical functions, `picdesign` provides builders that return
**PhotonForge `Component` objects** (geometry + ports) ready for layout, GDS export, and
Tidy3D simulation. They require an active technology — create one with
`sin_strip_technology()` and assign it to `pf.config.default_technology`:

```python
import photonforge as pf
from picdesign import (
    sin_strip_technology, grating_coupler_period,
    grating_coupler_component, directional_coupler_component,
    y_branch_component, edge_coupler_component,
    ring_resonator_component, mzi_component,
)

pf.config.default_technology = sin_strip_technology(wavelength_um=0.780)

# Surface grating coupler (fiber I/O) sized from the Bragg condition
period = grating_coupler_period(0.780, 1.78, theta_deg=10.0)
gc   = grating_coupler_component(period_um=period, n_teeth=24)   # ports: P0
ring = ring_resonator_component(radius_um=20.0, gap_um=0.20)     # ports: P0, P1
mzi  = mzi_component(delta_L_um=34.0, arm_length_um=120.0)       # ports: P0, P1

# Terminate any device port with a grating coupler:
circuit = pf.Component("RING_GC")
ref = circuit.add_reference(ring)
for p in ("P0", "P1"):
    circuit.add_reference(grating_coupler_component(period_um=period, name=f"GC_{p}")).connect("P0", ref[p])
circuit.write_gds("ring_grating.gds")
```

> These builders require the `photonforge` and `tidy3d` packages. The analytical
> functions above need only `numpy`, so `photonforge`/`tidy3d` are imported lazily.

---

## Examples

**Analytical examples:**

```bash
cd examples
python waveguide_example.py   # single-mode analysis, bend loss, confinement
python ring_example.py        # FSR design, Q factor, transmission spectrum
python mzi_example.py         # path imbalance, biosensing sensitivity
python lca_example.py         # LCA radar chart, platform comparison
```

**PhotonForge layout examples** (build physical objects, all terminated with grating couplers, export GDS):

```bash
python grating_coupler_example.py      # grating coupler + GC-to-GC loopback
python directional_coupler_example.py  # directional coupler, all 4 ports grating-coupled
python y_branch_example.py             # 1×2 Y-branch, input + 2 outputs grating-coupled
python edge_coupler_example.py         # edge-in / grating-out bus test structure
python ring_layout_example.py          # ring resonator, input + through grating-coupled
python mzi_layout_example.py           # MZI, input + output grating-coupled
```

---

## Traceability to course homeworks

| Component | Source |
|---|---|
| Mode solver patterns, material constants | HW2 — Tarea2 (SingleMode.ipynb, MMI.ipynb) |
| Ring resonator, MZI, Y-branch layout | HW4 — HomeworkNotebook.ipynb |
| Multi-device GDS pattern | HW3 — Tarrra3.ipynb |
| LCA variables | HW5 Part 1 |

---

## Layer map (SiN foundry convention)

| Name | GDS layer | Description |
|---|---|---|
| WG_CORE | (1, 0) | SiN core |
| WG_CLAD | (2, 0) | SiO2 upper cladding |
| CHIP_EDGE | (10, 0) | Dicing lane / chip boundary |
