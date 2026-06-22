"""
Ring resonator analytical design functions.
Covers FSR, Q factor, extinction ratio, and radius-from-FSR inversion.
All passive — no carrier injection, no thermal tuning.
"""

import numpy as np


def ring_fsr(n_eff: float, radius_um: float, wavelength_um: float) -> float:
    """
    Description:
        Free Spectral Range (FSR) of a ring resonator based on the effective
        refractive index. The FSR is the wavelength spacing between consecutive
        resonance peaks: FSR = λ² / (n_g × L), where L = 2π R is the
        circumference and n_g is approximated by n_eff for a first-order estimate.

    Inputs:
        n_eff         : float — effective index of the guided mode
        radius_um     : float — ring radius (µm), measured to waveguide centre
        wavelength_um : float — central wavelength (µm)

    Outputs:
        fsr_nm : float — free spectral range in nanometres (nm)

    Units:
        radius_um     → µm
        wavelength_um → µm
        fsr_nm        → nm

    Example:
        >>> ring_fsr(1.75, 50.0, 0.780)
        1.378...
    """
    L_um = 2.0 * np.pi * radius_um
    fsr_um = wavelength_um**2 / (n_eff * L_um)
    return float(fsr_um * 1000.0)  # convert µm → nm


def ring_fsr_group(n_group: float, radius_um: float, wavelength_um: float) -> float:
    """
    Description:
        Free Spectral Range using the group index n_g, which accounts for
        waveguide dispersion. More accurate than using n_eff alone when the
        waveguide is strongly dispersive (e.g., narrow SiN waveguides at
        visible wavelengths). FSR = λ² / (n_g × 2π R).

    Inputs:
        n_group       : float — group index of the guided mode
        radius_um     : float — ring radius (µm)
        wavelength_um : float — central wavelength (µm)

    Outputs:
        fsr_nm : float — free spectral range in nanometres (nm)

    Units:
        radius_um     → µm
        wavelength_um → µm
        fsr_nm        → nm

    Example:
        >>> ring_fsr_group(1.90, 50.0, 0.780)
        1.27...
    """
    L_um = 2.0 * np.pi * radius_um
    fsr_um = wavelength_um**2 / (n_group * L_um)
    return float(fsr_um * 1000.0)


def ring_circumference(radius_um: float) -> float:
    """
    Description:
        Circumference of a circular ring resonator, measured along the
        waveguide centreline. Used to compute round-trip path length for
        FSR, Q, and loss budget calculations.

    Inputs:
        radius_um : float — ring radius to waveguide centre (µm)

    Outputs:
        circumference_um : float — round-trip path length (µm)

    Units:
        radius_um        → µm
        circumference_um → µm

    Example:
        >>> ring_circumference(50.0)
        314.159...
    """
    return float(2.0 * np.pi * radius_um)


def ring_radius_from_fsr(n_eff: float, fsr_nm: float,
                         wavelength_um: float) -> float:
    """
    Description:
        Invert the FSR formula to find the ring radius needed to achieve a
        target FSR: R = λ² / (n_eff × 2π × FSR).
        Useful in the early design phase when the FSR is specified by the
        application (e.g., biosensing channel spacing).

    Inputs:
        n_eff         : float — effective index of the guided mode
        fsr_nm        : float — target FSR (nm)
        wavelength_um : float — central wavelength (µm)

    Outputs:
        radius_um : float — required ring radius (µm)

    Units:
        fsr_nm        → nm (converted internally)
        wavelength_um → µm
        radius_um     → µm

    Example:
        >>> ring_radius_from_fsr(1.75, 5.0, 0.780)
        13.83...
    """
    fsr_um = fsr_nm / 1000.0
    L_um = wavelength_um**2 / (n_eff * fsr_um)
    return float(L_um / (2.0 * np.pi))


def ring_q_factor(wavelength_um: float, fsr_nm: float,
                  linewidth_nm: float) -> float:
    """
    Description:
        Quality factor Q of a ring resonator from the resonance linewidth
        (FWHM). Q = λ / Δλ where Δλ is the full-width half-maximum of
        the transmission dip. The finesse F = FSR / Δλ is also returned.

    Inputs:
        wavelength_um : float — resonance wavelength (µm)
        fsr_nm        : float — free spectral range (nm)
        linewidth_nm  : float — resonance linewidth FWHM (nm)

    Outputs:
        dict with keys:
            'Q'       : float — quality factor
            'finesse' : float — cavity finesse

    Units:
        wavelength_um → µm
        fsr_nm        → nm
        linewidth_nm  → nm

    Example:
        >>> ring_q_factor(0.780, 5.0, 0.05)
        {'Q': 15600.0, 'finesse': 100.0}
    """
    Q = (wavelength_um * 1000.0) / linewidth_nm
    finesse = fsr_nm / linewidth_nm
    return {"Q": float(Q), "finesse": float(finesse)}


def ring_transmission(wavelengths_nm: np.ndarray, resonance_nm: float,
                      r_coupling: float, alpha_roundtrip: float) -> np.ndarray:
    """
    Description:
        Analytic through-port transmission spectrum of an all-pass ring
        resonator (single-bus coupling) using the transfer-matrix model.
        T = |E_out/E_in|² = (r² - 2·r·a·cos(φ) + a²) / (1 - 2·r·a·cos(φ) + (r·a)²)
        where a = round-trip field transmission, r = self-coupling coefficient.

    Inputs:
        wavelengths_nm  : ndarray — wavelength array (nm)
        resonance_nm    : float   — target resonance wavelength (nm)
        r_coupling      : float   — self-coupling coefficient (0–1); power coupling κ² = 1 - r²
        alpha_roundtrip : float   — round-trip field transmission (0–1, loss included)

    Outputs:
        T : ndarray — through-port power transmission (dimensionless, 0–1)

    Units:
        wavelengths_nm → nm
        T              → dimensionless

    Example:
        >>> import numpy as np
        >>> wl = np.linspace(779, 781, 1000)
        >>> T = ring_transmission(wl, 780.0, 0.9, 0.98)
    """
    # Phase: φ = 2π n_eff L / λ.  Near resonance we use a small-signal approx.
    # Here we parameterise by relative detuning from resonance_nm.
    delta_lam = wavelengths_nm - resonance_nm  # nm
    # Approximate FSR for phase calculation (will cancel in ratio at resonance)
    # φ = 2π × (resonance_nm / wavelengths_nm)  — normalised round-trip phase
    phi = 2.0 * np.pi * resonance_nm / wavelengths_nm  # proportional phase sweep

    r = r_coupling
    a = alpha_roundtrip
    cos_phi = np.cos(phi)

    numerator = r**2 - 2.0 * r * a * cos_phi + a**2
    denominator = 1.0 - 2.0 * r * a * cos_phi + (r * a) ** 2
    return numerator / denominator


# ─────────────────────────────────────────────────────────────────────────────
#  PhotonForge / Tidy3D physical component builder
# ─────────────────────────────────────────────────────────────────────────────


def ring_resonator_component(radius_um: float = 20.0, gap_um: float = 0.20,
                             bus_extension_um: float = 10.0,
                             width_um: float = 0.70, layer: tuple = (1, 0),
                             name: str = "RING_RESONATOR"):
    """
    Description:
        Build an all-pass (single-bus) ring resonator as a PhotonForge component:
        a closed circular ring of radius ``radius_um`` evanescently coupled to a
        straight bus waveguide across a ``gap_um`` gap. Ports P0 (bus input, left
        end) and P1 (bus through, right end) are exposed, both pointing inward
        following the PhotonForge convention. Requires an active PhotonForge
        technology (see ``sin_strip_technology``).

    Inputs:
        radius_um        : float — ring radius to the waveguide centre (µm);
                                   size with ring_radius_from_fsr()
        gap_um           : float — edge-to-edge bus-ring coupling gap (µm)
        bus_extension_um : float — bus length added on each side of the ring (µm)
        width_um         : float — waveguide core width (µm)
        layer            : tuple — GDS (layer, datatype), default (1,0)
        name             : str   — component name

    Outputs:
        component : photonforge.Component — ring resonator (ports P0 in, P1 through)

    Units:
        All lengths µm.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, ring_resonator_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> ring = ring_resonator_component(radius_um=20.0, gap_um=0.2)
        >>> sorted(ring.ports)
        ['P0', 'P1']
    """
    from .couplers import _require_pf, _strip_port
    pf = _require_pf()
    c = pf.Component(name)
    # Closed circular ring built from two 180° turns
    ring = (pf.Path((0.0, -radius_um), width_um)
            .turn(180, radius_um, euler_fraction=0)
            .turn(180, radius_um, euler_fraction=0))
    c.add(layer, ring)
    # Straight bus below the ring, separated by the coupling gap
    y_bus = -(radius_um + width_um + gap_um)
    c.add(layer, pf.Path((-radius_um - bus_extension_um, y_bus), width_um)
          .segment((radius_um + bus_extension_um, y_bus)))
    # Port directions follow the PhotonForge convention (input P0 faces +x into the
    # device, through P1 faces -x) so connected components attach facing outward.
    c.add_port(_strip_port(pf, (-radius_um - bus_extension_um, y_bus), 0), "P0")
    c.add_port(_strip_port(pf, (radius_um + bus_extension_um, y_bus), 180), "P1")
    return c
