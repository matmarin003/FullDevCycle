"""
ring_layout_example.py
Builds the PhotonForge all-pass ring-resonator object from picdesign and
terminates the bus input and through port with grating couplers.
Exports the layout to GDS.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    ring_resonator_component,
    ring_radius_from_fsr,
    grating_coupler_component,
    grating_coupler_period,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780
N_EFF = 1.78
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Size the ring radius for a target FSR ─────────────────────────────────
target_fsr_nm = 2.5
radius = ring_radius_from_fsr(N_EFF, target_fsr_nm, LAM0)
radius = max(radius, 20.0)   # respect the minimum bend radius for water cladding
print(f"Ring radius for {target_fsr_nm} nm FSR: {radius:.1f} um")

period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0)


def grating_coupler(name):
    return grating_coupler_component(period_um=period, wavelength_um=LAM0, name=name)


# ── 3. Ring resonator with grating couplers on input and through ports ───────
ring = ring_resonator_component(radius_um=radius, gap_um=0.20,
                                bus_extension_um=15.0, name="RING_RESONATOR")
print(f"Ring ports: {sorted(ring.ports)}")

circuit = pf.Component("RING_GRATING_TEST")
ref = circuit.add_reference(ring)
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
