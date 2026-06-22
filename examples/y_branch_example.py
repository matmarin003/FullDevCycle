"""
y_branch_example.py
Builds the PhotonForge 1x2 Y-branch splitter object from picdesign and
terminates the input and both outputs with grating couplers.
Exports the layout to GDS.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    y_branch_component,
    y_branch_arm_spacing,
    grating_coupler_component,
    grating_coupler_period,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780
N_EFF = 1.78
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Minimum arm spacing to avoid output-arm crosstalk ─────────────────────
min_spacing = y_branch_arm_spacing(LAM0, 2.0, 1.45, 0.70)
spacing = max(6.0, round(min_spacing, 1))
print(f"Minimum arm spacing: {min_spacing:.2f} um  ->  using {spacing:.1f} um")

period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0)


def grating_coupler(name):
    return grating_coupler_component(period_um=period, wavelength_um=LAM0, name=name)


# ── 3. Y-branch with grating couplers on the input and both outputs ──────────
y = y_branch_component(arm_spacing_um=spacing, s_bend_length_um=25.0,
                       name="Y_BRANCH")
print(f"Y-branch ports: {sorted(y.ports)}")

circuit = pf.Component("Y_BRANCH_GRATING_TEST")
ref = circuit.add_reference(y)
for p in ("P0", "P1", "P2"):
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
