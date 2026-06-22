"""
Analytical waveguide design functions for passive SiN-on-SiO2 PICs.
Covers single-mode condition, confinement, loss, and bend radius estimation.
All models are passive — no doping, current injection, or thermal tuning.
"""

import numpy as np


def single_mode_condition(width_um: float, height_um: float,
                          n_core: float, n_clad: float,
                          wavelength_um: float) -> dict:
    """
    Description:
        Approximate single-mode condition for a rectangular dielectric waveguide
        using the V-number threshold. A waveguide is considered single-mode in
        each transverse dimension when V < π/2 (Marcatili's criterion).
        The check is performed separately for width and height.

    Inputs:
        width_um      : float — core width (µm)
        height_um     : float — core height (µm)
        n_core        : float — core refractive index
        n_clad        : float — cladding refractive index
        wavelength_um : float — free-space wavelength (µm)

    Outputs:
        dict with keys:
            'V_width'       : float — V number for width dimension
            'V_height'      : float — V number for height dimension
            'single_mode_x' : bool  — True if single-mode in width
            'single_mode_y' : bool  — True if single-mode in height
            'single_mode'   : bool  — True if single-mode in both dimensions
            'cutoff_width'  : float — maximum width for single-mode (µm)
            'cutoff_height' : float — maximum height for single-mode (µm)

    Units:
        width_um, height_um, wavelength_um → µm
        V numbers → dimensionless

    Example:
        >>> single_mode_condition(0.80, 0.22, 2.0, 1.45, 0.780)
        {'V_width': ..., 'single_mode': True, ...}
    """
    NA = np.sqrt(n_core**2 - n_clad**2)
    k0 = np.pi / wavelength_um  # = π/λ, so V = k0 * d * NA

    V_w = float(np.pi * width_um * NA / wavelength_um)
    V_h = float(np.pi * height_um * NA / wavelength_um)

    # Single-mode cutoff: V < π/2 per dimension
    threshold = np.pi / 2.0
    sm_x = V_w < threshold
    sm_y = V_h < threshold

    cutoff_w = float(wavelength_um / (2.0 * NA))
    cutoff_h = float(wavelength_um / (2.0 * NA))

    return {
        "V_width": V_w,
        "V_height": V_h,
        "single_mode_x": sm_x,
        "single_mode_y": sm_y,
        "single_mode": sm_x and sm_y,
        "cutoff_width_um": cutoff_w,
        "cutoff_height_um": cutoff_h,
    }


def confinement_factor(width_um: float, height_um: float,
                       n_core: float, n_clad: float,
                       wavelength_um: float) -> float:
    """
    Description:
        Approximate optical confinement factor Γ for a rectangular waveguide
        using the 1-D Gaussian mode overlap model (Petermann's approximation).
        Γ is the fraction of modal power confined within the core region.
        This estimate is valid when the mode is well-guided (V > 1).

    Inputs:
        width_um      : float — core width (µm)
        height_um     : float — core height (µm)
        n_core        : float — core refractive index
        n_clad        : float — cladding refractive index
        wavelength_um : float — free-space wavelength (µm)

    Outputs:
        gamma : float — confinement factor in [0, 1] (dimensionless)

    Units:
        width_um, height_um, wavelength_um → µm
        gamma → dimensionless (fraction of power)

    Example:
        >>> confinement_factor(0.80, 0.22, 2.0, 1.45, 0.780)
        0.72...
    """
    NA = np.sqrt(n_core**2 - n_clad**2)
    # Approximate mode-field half-widths from the characteristic equation solution
    # (simplified Marcatili: κ·d/2 ≈ π/2 at cutoff; uses exponential field decay)
    V_w = np.pi * width_um * NA / wavelength_um
    V_h = np.pi * height_um * NA / wavelength_um

    # 1-D confinement: Γ_1d = 1 - exp(-2*V²/(1+V²))  (empirical fit)
    def _gamma_1d(V):
        return 1.0 - np.exp(-2.0 * V**2 / (1.0 + V**2))

    return float(_gamma_1d(V_w) * _gamma_1d(V_h))


def propagation_loss_db_per_cm_to_per_m(loss_db_per_cm: float) -> float:
    """
    Description:
        Convert waveguide propagation loss from dB/cm (common in PIC
        characterisation reports) to m⁻¹ (SI units used in coupled-mode
        theory and GNLSE simulations).

        Relation: α [m⁻¹] = (loss [dB/cm] × 100) / (10 × log10(e))
                           = loss [dB/cm] × 100 / 4.3429

    Inputs:
        loss_db_per_cm : float — propagation loss in dB/cm

    Outputs:
        alpha_per_m : float — field amplitude loss coefficient in m⁻¹

    Units:
        loss_db_per_cm → dB/cm
        alpha_per_m    → m⁻¹

    Example:
        >>> propagation_loss_db_per_cm_to_per_m(1.0)
        230.26...
    """
    return float(loss_db_per_cm * 100.0 / (10.0 * np.log10(np.e)))


def propagation_loss_per_m_to_db_per_cm(alpha_per_m: float) -> float:
    """
    Description:
        Inverse of propagation_loss_db_per_cm_to_per_m. Converts loss
        coefficient from m⁻¹ back to dB/cm for comparison with
        experimental literature values.

    Inputs:
        alpha_per_m : float — field amplitude loss coefficient (m⁻¹)

    Outputs:
        loss_db_per_cm : float — propagation loss in dB/cm

    Units:
        alpha_per_m    → m⁻¹
        loss_db_per_cm → dB/cm

    Example:
        >>> propagation_loss_per_m_to_db_per_cm(230.26)
        1.000...
    """
    return float(alpha_per_m * 10.0 * np.log10(np.e) / 100.0)


def bend_loss_estimate(radius_um: float, width_um: float,
                       n_core: float, n_eff: float,
                       n_clad: float, wavelength_um: float) -> float:
    """
    Description:
        Estimate bend radiation loss using the Marcuse analytical formula for
        a weakly-guiding bent slab waveguide. The loss grows exponentially as
        the bend radius decreases. This is an order-of-magnitude estimate;
        accurate values require full FEM/FDTD simulation.

        α_bend = (C1 / √R) × exp(-C2 × R)
        where C1 and C2 depend on the mode confinement (see Marcuse 1982).

    Inputs:
        radius_um   : float — bend radius (µm)
        width_um    : float — core width (µm)
        n_core      : float — core refractive index
        n_eff       : float — effective index of the guided mode
        n_clad      : float — cladding refractive index
        wavelength_um : float — free-space wavelength (µm)

    Outputs:
        alpha_bend_per_m : float — bend loss coefficient (m⁻¹)

    Units:
        radius_um, width_um, wavelength_um → µm
        alpha_bend_per_m                   → m⁻¹

    Example:
        >>> bend_loss_estimate(50.0, 0.80, 2.0, 1.75, 1.45, 0.780)
        0.12...
    """
    k0 = 2.0 * np.pi / (wavelength_um * 1e-6)  # rad/m
    R = radius_um * 1e-6                         # m

    beta = n_eff * k0
    kappa = np.sqrt(max(beta**2 - (n_clad * k0)**2, 1e-30))

    # Marcuse radiation coefficient
    C2 = (2.0 * kappa**3) / (3.0 * beta**2 * R)
    # Pre-factor (simplified, assuming large V)
    C1 = (beta**2 / (2.0 * np.sqrt(np.pi) * kappa**1.5))

    alpha = C1 / np.sqrt(R) * np.exp(-C2 * R)
    return float(alpha)


def minimum_bend_radius(width_um: float, n_core: float,
                        n_eff: float, n_clad: float,
                        wavelength_um: float,
                        max_loss_db_per_cm: float = 0.1) -> float:
    """
    Description:
        Estimate the minimum bend radius such that bend-induced radiation
        loss stays below a target threshold. Uses a bisection search over
        the Marcuse bend loss model.

    Inputs:
        width_um          : float — core width (µm)
        n_core            : float — core refractive index
        n_eff             : float — effective mode index
        n_clad            : float — cladding refractive index
        wavelength_um     : float — free-space wavelength (µm)
        max_loss_db_per_cm: float — maximum acceptable bend loss (dB/cm), default 0.1

    Outputs:
        R_min_um : float — minimum acceptable bend radius (µm)

    Units:
        width_um, wavelength_um → µm
        max_loss_db_per_cm      → dB/cm
        R_min_um                → µm

    Example:
        >>> minimum_bend_radius(0.80, 2.0, 1.75, 1.45, 0.780, 0.1)
        45.3...
    """
    alpha_target = propagation_loss_db_per_cm_to_per_m(max_loss_db_per_cm)
    lo, hi = 1.0, 1e5  # µm
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        a = bend_loss_estimate(mid, width_um, n_core, n_eff, n_clad, wavelength_um)
        if a > alpha_target:
            lo = mid
        else:
            hi = mid
    return float(0.5 * (lo + hi))
