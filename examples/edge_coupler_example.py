"""
edge_coupler_example.py
Builds the PhotonForge inverse-taper edge-coupler object from picdesign and
pairs it with a grating coupler at the opposite end of a bus waveguide
(edge-in / grating-out test structure). Exports the layout to GDS.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    edge_coupler_component,
    edge_coupler_taper_length,
    grating_coupler_component,
    grating_coupler_period,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780
N_EFF = 1.78
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Adiabatic taper length for the inverse-taper edge coupler ─────────────
L_taper = edge_coupler_taper_length(0.10, 0.70, 2.0, 1.45, LAM0,
                                    taper_angle_deg=0.5)
print(f"Edge-coupler taper length (0.5 deg): {L_taper:.1f} um")

period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0)

# ── 3. Edge-in / grating-out bus test structure ──────────────────────────────
circuit = pf.Component("EDGE_TO_GRATING_TEST")
edge = circuit.add_reference(
    edge_coupler_component(tip_width_um=0.10, full_width_um=0.70,
                           length_um=L_taper, name="EDGE_COUPLER"))
bus = circuit.add_reference(pf.parametric.straight(port_spec="Strip", length=300.0))
bus.connect("P0", edge["P0"])
gc = circuit.add_reference(
    grating_coupler_component(period_um=period, name="GRATING_COUPLER"))
gc.connect("P0", bus["P1"])

# Only the out-of-plane fiber GaussianPort should remain disconnected.
print(f"Disconnected ports: {circuit.disconnected_reference_ports()}")

# ── Show the layout in the PhotonForge LiveViewer ────────────────────────────
viewer = LiveViewer()
viewer(circuit)
print(f"Live viewer running at {viewer}")
if sys.stdin and sys.stdin.isatty():
    input("Press Enter to close the viewer...")
viewer.stop()
