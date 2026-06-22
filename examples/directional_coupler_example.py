"""
directional_coupler_example.py
Builds the PhotonForge directional-coupler object from picdesign and terminates
all four ports with grating couplers for fiber-array characterization.
Exports the layout to GDS.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    directional_coupler_component,
    grating_coupler_component,
    grating_coupler_period,
    directional_coupler_kappa,
    directional_coupler_length,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780
N_EFF = 1.78
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Size the coupler for a 3 dB (50/50) split (analytical estimate) ───────
n_core = 2.0
n_clad = 1.45
kappa = directional_coupler_kappa(0.20, 0.70, n_core, n_clad, LAM0)
Lc = directional_coupler_length(kappa, coupling_ratio=0.5)
print(f"kappa = {kappa:.4f} /um  ->  3 dB coupling length Lc = {Lc:.1f} um")

period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0)


def grating_coupler(name):
    return grating_coupler_component(period_um=period, wavelength_um=LAM0, name=name)


# ── 3. Directional coupler with grating couplers on all four ports ───────────
dc = directional_coupler_component(gap_um=0.20, coupling_length_um=Lc,
                                   s_bend_length_um=15.0, s_bend_offset_um=6.0,
                                   name="DIRECTIONAL_COUPLER")
print(f"Directional coupler ports: {sorted(dc.ports)}")

circuit = pf.Component("DC_GRATING_TEST")
ref = circuit.add_reference(dc)
for p in sorted(dc.ports):
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
