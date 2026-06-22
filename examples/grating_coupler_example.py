"""
grating_coupler_example.py
Builds the PhotonForge *focused* grating-coupler object from picdesign (curved
teeth generated with pf.stencil.focused_grating, after the PhotonForge
grating-coupler example) and a grating-coupler-to-grating-coupler loopback test
structure (two grating couplers joined by a single-mode bus). The layout is shown
in the PhotonForge LiveViewer — no GDS is written.
Platform: SiN-on-SiO2 strip waveguide, lambda = 780 nm (visible biosensing).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import photonforge as pf
from photonforge.live_viewer import LiveViewer
from picdesign import (
    sin_strip_technology,
    grating_coupler_component,
    grating_coupler_period,
)

# ── 1. Activate the SiN strip technology ─────────────────────────────────────
LAM0 = 0.780                      # design wavelength [um]
N_EFF = 1.78                      # TE0 effective index estimate
pf.config.default_technology = sin_strip_technology(wavelength_um=LAM0)

# ── 2. Grating period from the phase-matching (Bragg) condition ──────────────
period = grating_coupler_period(LAM0, N_EFF, theta_deg=10.0, n_env=1.0)
print(f"Grating period (theta=10 deg): {period*1e3:.1f} nm")


def grating_coupler(name):
    """Focused grating coupler designed for this platform."""
    return grating_coupler_component(period_um=period, focal_length_um=12.5,
                                     length_um=15.5, grating_angle_deg=45.0,
                                     fiber_angle_deg=10.0, fill_factor=0.5,
                                     wavelength_um=LAM0, name=name)


# ── 3. Standalone grating coupler ────────────────────────────────────────────
gc = grating_coupler("GRATING_COUPLER")
print(f"Grating coupler ports: {sorted(gc.ports)}")

# ── 4. Grating-coupler loopback: GC -> bus waveguide -> GC ───────────────────
loop = pf.Component("GC_LOOPBACK")
gc_in = loop.add_reference(grating_coupler("GC_IN"))
bus = loop.add_reference(pf.parametric.straight(port_spec="Strip", length=200.0))
bus.connect("P0", gc_in["P0"])
gc_out = loop.add_reference(grating_coupler("GC_OUT"))
gc_out.connect("P0", bus["P1"])

# Only the out-of-plane fiber GaussianPorts should remain disconnected.
print(f"Loopback disconnected ports: {loop.disconnected_reference_ports()}")
lo, hi = loop.bounds()
print(f"Loopback footprint: {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} um")

# ── 5. Show the layout in the PhotonForge LiveViewer ─────────────────────────
viewer = LiveViewer()
viewer(gc)
viewer(loop)
print(f"Live viewer running at {viewer}")
if sys.stdin and sys.stdin.isatty():
    input("Press Enter to close the viewer...")
viewer.stop()
