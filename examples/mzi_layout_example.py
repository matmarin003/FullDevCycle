"""
mzi_layout_example.py
Builds the PhotonForge Mach-Zehnder interferometer object from picdesign
(input -> Y-split -> two imbalanced arms -> Y-combine -> output) and terminates
the input and output with grating couplers. Exports the layout to GDS.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    mzi_component,
    mzi_path_length_imbalance,
    grating_coupler_component,
    grating_coupler_period,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780
N_EFF = 1.78
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Size the arm imbalance for a target FSR ───────────────────────────────
target_fsr_nm = 10.0
delta_L = mzi_path_length_imbalance(target_fsr_nm, N_EFF, LAM0)
print(f"Arm imbalance for {target_fsr_nm} nm FSR: dL = {delta_L:.1f} um")

period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0)


def grating_coupler(name):
    return grating_coupler_component(period_um=period, wavelength_um=LAM0, name=name)


# ── 3. MZI with grating couplers on the input and output ─────────────────────
mzi = mzi_component(delta_L_um=delta_L, arm_length_um=120.0,
                    arm_spacing_um=6.0, name="MZI")
print(f"MZI ports: {sorted(mzi.ports)}")

circuit = pf.Component("MZI_GRATING_TEST")
ref = circuit.add_reference(mzi)
for p in ("P0", "P1"):
    gcr = circuit.add_reference(grating_coupler(f"GC_{p}"))
    gcr.connect("P0", ref[p])

# Only the out-of-plane fiber GaussianPorts should remain disconnected.
print(f"Disconnected ports: {circuit.disconnected_reference_ports()}")

# ── Show the layout in the PhotonForge LiveViewer ────────────────────────────
viewer = LiveViewer()
viewer(circuit)
print(f"Live viewer running at {viewer}")
if sys.stdin and sys.stdin.isatty():
    input("Press Enter to close the viewer...")
viewer.stop()
