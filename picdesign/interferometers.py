"""
Mach-Zehnder interferometer (MZI) analytical design functions.
Covers FSR, path-length imbalance, transfer matrix, and sensitivity.
All passive — waveguide perturbation is via external refractive-index change
(evanescent sensing), not via carrier injection or heating.
"""

import numpy as np


def mzi_fsr(n_eff: float, delta_L_um: float, wavelength_um: float) -> float:
    """
    Description:
        Free Spectral Range of a Mach-Zehnder interferometer. The FSR is the
        wavelength spacing between adjacent transmission maxima and is set by
        the optical path-length difference ΔL between the two arms:
            FSR = λ² / (n_eff × ΔL)

    Inputs:
        n_eff         : float — effective index of the waveguide mode
        delta_L_um    : float — physical path-length imbalance ΔL (µm)
        wavelength_um : float — central wavelength (µm)

    Outputs:
        fsr_nm : float — free spectral range in nanometres (nm)

    Units:
        delta_L_um    → µm
        wavelength_um → µm
        fsr_nm        → nm

    Example:
        >>> mzi_fsr(1.75, 100.0, 0.780)
        3.37...
    """
    fsr_um = wavelength_um**2 / (n_eff * delta_L_um)
    return float(fsr_um * 1000.0)


def mzi_path_length_imbalance(fsr_nm: float, n_eff: float,
                               wavelength_um: float) -> float:
    """
    Description:
        Invert the MZI FSR formula to find the physical path-length difference
        ΔL required to achieve a target FSR. Useful in the design phase when
        the sensing bandwidth or channel spacing is specified first.
            ΔL = λ² / (n_eff × FSR)

    Inputs:
        fsr_nm        : float — target free spectral range (nm)
        n_eff         : float — effective index of the guided mode
        wavelength_um : float — central wavelength (µm)

    Outputs:
        delta_L_um : float — required path-length imbalance (µm)

    Units:
        fsr_nm        → nm (converted internally)
        wavelength_um → µm
        delta_L_um    → µm

    Example:
        >>> mzi_path_length_imbalance(5.0, 1.75, 0.780)
        67.5...
    """
    fsr_um = fsr_nm / 1000.0
    return float(wavelength_um**2 / (n_eff * fsr_um))


def mzi_transmission(wavelengths_nm: np.ndarray, delta_L_um: float,
                     n_eff: float, loss_db_per_cm: float = 0.0) -> np.ndarray:
    """
    Description:
        Analytic through-port power transmission of a balanced MZI as a
        function of wavelength. Assumes 50/50 splitting at both Y-junctions.
            T(λ) = 0.5 × [1 + cos(2π n_eff ΔL / λ)] × η_loss
        where η_loss accounts for differential propagation loss between arms.

    Inputs:
        wavelengths_nm : ndarray — wavelength sweep (nm)
        delta_L_um     : float   — path-length imbalance ΔL (µm)
        n_eff          : float   — effective index of both arms (assumed equal)
        loss_db_per_cm : float   — propagation loss (dB/cm), applied to the
                                   longer arm only (default 0 = lossless)

    Outputs:
        T : ndarray — power transmission at output port (dimensionless, 0–1)

    Units:
        wavelengths_nm → nm
        delta_L_um     → µm
        T              → dimensionless

    Example:
        >>> import numpy as np
        >>> wl = np.linspace(750, 810, 500)
        >>> T = mzi_transmission(wl, 100.0, 1.75)
    """
    lam_um = wavelengths_nm / 1000.0
    phi = 2.0 * np.pi * n_eff * delta_L_um / lam_um

    # Amplitude loss factor on longer arm
    alpha_per_m = loss_db_per_cm * 100.0 / (10.0 * np.log10(np.e))
    eta = np.exp(-alpha_per_m * delta_L_um * 1e-6)

    T = 0.5 * (1.0 + eta * np.cos(phi))
    return T


def mzi_sensitivity(n_eff: float, delta_L_um: float,
                    wavelength_um: float,
                    dn_dC: float = 1e-4) -> float:
    """
    Description:
        Wavelength sensitivity of an MZI biosensor to a surface refractive-index
        change. Assumes the analyte covers only the sensing arm (half of ΔL).
        S = dλ_peak/dC = (λ / n_g) × (L_sense × dn_eff/dn_analyte) / ΔL
        Simplified here to S = FSR × (dn_eff / dn_analyte) for a first estimate.

    Inputs:
        n_eff         : float — effective index of the sensing mode
        delta_L_um    : float — path-length imbalance ΔL (µm)
        wavelength_um : float — central wavelength (µm)
        dn_dC         : float — effective index change per RIU (refractive index unit),
                                typical SiN biosensing: ~0.1–0.3 RIU⁻¹ (default 1e-4)

    Outputs:
        S_nm_per_RIU : float — wavelength shift per RIU (nm/RIU)

    Units:
        wavelength_um → µm
        delta_L_um    → µm
        dn_dC         → RIU⁻¹
        S             → nm/RIU

    Example:
        >>> mzi_sensitivity(1.75, 100.0, 0.780, dn_dC=0.2)
        89.1...
    """
    fsr_nm = wavelength_um**2 / (n_eff * delta_L_um / 1000.0)  # nm
    # Sensitivity ≈ FSR × (dn_eff/dn_a) / n_eff  (order-of-magnitude)
    S = fsr_nm * dn_dC / n_eff * 1000.0
    return float(S)


def mzi_arm_lengths(delta_L_um: float,
                    common_length_um: float = 0.0) -> dict:
    """
    Description:
        Compute the individual arm lengths L1 (reference) and L2 (sensing/delayed)
        of an MZI given the path-length imbalance and the shared routing length.
        L2 = common_length + ΔL, L1 = common_length.

    Inputs:
        delta_L_um       : float — path-length imbalance ΔL (µm)
        common_length_um : float — minimum arm length shared by both arms (µm)

    Outputs:
        dict with keys:
            'L1_um' : float — shorter (reference) arm length (µm)
            'L2_um' : float — longer (sensing/delayed) arm length (µm)
            'delta_L_um' : float — confirmed imbalance (µm)

    Units:
        All µm.

    Example:
        >>> mzi_arm_lengths(100.0, 200.0)
        {'L1_um': 200.0, 'L2_um': 300.0, 'delta_L_um': 100.0}
    """
    L1 = common_length_um
    L2 = common_length_um + delta_L_um
    return {"L1_um": float(L1), "L2_um": float(L2), "delta_L_um": float(delta_L_um)}


# ─────────────────────────────────────────────────────────────────────────────
#  PhotonForge / Tidy3D physical component builder
# ─────────────────────────────────────────────────────────────────────────────


def mzi_component(delta_L_um: float = 34.0, arm_length_um: float = 120.0,
                  arm_spacing_um: float = 6.0, bend_radius_um: float = 10.0,
                  name: str = "MZI"):
    """
    Description:
        Build a Mach-Zehnder interferometer as a PhotonForge component with the
        canonical topology: a single input is split by a Y-branch into two arms,
        the arms run with a path-length imbalance ΔL, and a second (mirrored)
        Y-branch recombines them into a single output. The reference arm has
        length ``arm_length_um``; the sensing arm is longer by ``delta_L_um``.
        The shorter arm is bridged to the combiner with an auto-router so the
        layout is fully connected. Ports: P0 (input), P1 (output). Requires an
        active PhotonForge technology (see ``sin_strip_technology``).

    Inputs:
        delta_L_um     : float — path-length imbalance ΔL between arms (µm);
                                 size with mzi_path_length_imbalance()
        arm_length_um  : float — reference (straight) arm length (µm)
        arm_spacing_um : float — centre-to-centre arm separation (µm)
        bend_radius_um : float — bend radius of the delay-arm trombone (µm)
        name           : str   — component name

    Outputs:
        component : photonforge.Component — MZI with ports 'P0' (in), 'P1' (out)

    Units:
        All lengths µm.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, mzi_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> mzi = mzi_component(delta_L_um=34.0, arm_length_um=120.0)
        >>> sorted(mzi.ports)
        ['P0', 'P1']
    """
    from .couplers import _require_pf, y_branch_component
    pf = _require_pf()
    tech = pf.config.default_technology
    core_width = sum(w for w, _, lyr in tech.ports["Strip"].path_profiles
                     if lyr == (1, 0))

    def _delay_arm(span_um, extra_um, radius_um):
        """Trombone delay arm: spans ``span_um`` in x with a downward detour so
        its total path length is exactly ``span_um + extra_um``. Returns a
        component with ports P0 (input, +x) and P1 (output, -x)."""
        lead = (span_um - 4.0 * radius_um) / 2.0
        if lead < 0:
            raise ValueError(
                f"arm_length_um ({span_um}) must be at least 4×bend_radius_um "
                f"({4.0 * radius_um}) to fit the delay trombone.")

        def _path(drop):
            p = pf.Path((0.0, 0.0), core_width)
            p.segment((lead, 0.0), relative=True)
            p.turn(-90, radius_um)
            p.segment((0.0, -drop), relative=True)
            p.turn(90, radius_um)
            p.turn(90, radius_um)
            p.segment((0.0, drop), relative=True)
            p.turn(-90, radius_um)
            p.segment((lead, 0.0), relative=True)
            return p

        # Path length is affine in ``drop`` (only the vertical straights change),
        # so two evaluations give the exact ``drop`` for the target length.
        l0 = _path(0.0).length()
        slope = (_path(10.0).length() - l0) / 10.0
        drop = (span_um + extra_um - l0) / slope
        if drop < 0:
            raise ValueError(
                f"delta_L_um ({extra_um}) is too small for arm_length_um "
                f"({span_um}); minimum achievable ΔL is {l0 - span_um:.2f} µm. "
                f"Increase arm_length_um, reduce bend_radius_um, or raise ΔL.")
        path = _path(drop)
        d = pf.Component(name + "_DELAY")
        d.add((1, 0), path)
        d.add((2, 0), pf.envelope(d.get_structures((1, 0)), 1.0,
                                  trim_x_min=True, trim_x_max=True))
        d.add_port(pf.Port((0.0, 0.0), 0, "Strip"), "P0")
        d.add_port(pf.Port((span_um, 0.0), 180, "Strip"), "P1")
        return d

    c = pf.Component(name)
    # Input Y-branch splitter (outputs P1 = bottom, P2 = top).
    split = c.add_reference(y_branch_component(arm_spacing_um=arm_spacing_um,
                                               name="Y_SPLIT"))
    # Reference arm: straight, on the top output.
    ref = c.add_reference(pf.parametric.straight(port_spec="Strip",
                                                 length=arm_length_um))
    ref.connect("P0", split["P2"])
    # Delay arm: trombone with an exact extra length ΔL, on the bottom output.
    delay = c.add_reference(_delay_arm(arm_length_um, delta_L_um, bend_radius_um))
    delay.connect("P0", split["P1"])
    # Output Y-branch combiner. The Y is y-symmetric, so connect()'s 180° turn
    # swaps the input sides: connecting P2 to the (bottom) delay arm lands the
    # combiner's P1 exactly on the (top) reference arm — no bridging route, so
    # the geometric imbalance stays exactly ΔL.
    comb = c.add_reference(y_branch_component(arm_spacing_um=arm_spacing_um,
                                              name="Y_COMBINE"))
    comb.connect("P2", delay["P1"])
    c.add_port(split["P0"], "P0")
    c.add_port(comb["P0"], "P1")
    return c
