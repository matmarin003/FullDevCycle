"""
Material refractive index models for passive PIC platforms.
All functions are purely analytical (Sellmeier equations) — no active components.
Platform focus: SiN on SiO2 for visible biosensing at 660–850 nm.
"""

import numpy as np


def sin_refractive_index(wavelength_um: float) -> float:
    """
    Description:
        Refractive index of stoichiometric silicon nitride (Si3N4) using the
        Sellmeier equation from Luke et al. 2015. Valid from ~0.31 to 5.5 µm.
        No doping or heating effects — purely passive material model.

    Inputs:
        wavelength_um : float — free-space wavelength in micrometers (µm)

    Outputs:
        n : float — real refractive index at the given wavelength

    Units:
        wavelength_um → µm
        n             → dimensionless

    Example:
        >>> sin_refractive_index(0.780)
        2.001...
    """
    lam = wavelength_um
    n_sq = (
        1.0
        + 3.0249 * lam**2 / (lam**2 - 0.1353406**2)
        + 40314.0 * lam**2 / (lam**2 - 1239.842**2)
    )
    return float(np.sqrt(n_sq))


def sio2_refractive_index(wavelength_um: float) -> float:
    """
    Description:
        Refractive index of fused silica (SiO2) using the Malitson Sellmeier
        equation. Valid from ~0.21 to 6.7 µm. Used as the cladding / BOX layer
        in the SiN-on-oxide passive platform.

    Inputs:
        wavelength_um : float — free-space wavelength in micrometers (µm)

    Outputs:
        n : float — real refractive index at the given wavelength

    Units:
        wavelength_um → µm
        n             → dimensionless

    Example:
        >>> sio2_refractive_index(0.780)
        1.453...
    """
    lam = wavelength_um
    n_sq = (
        1.0
        + 0.6961663 * lam**2 / (lam**2 - 0.0684043**2)
        + 0.4079426 * lam**2 / (lam**2 - 0.1162414**2)
        + 0.8974794 * lam**2 / (lam**2 - 9.896161**2)
    )
    return float(np.sqrt(n_sq))


def v_number(width_um: float, height_um: float,
             n_core: float, n_clad: float,
             wavelength_um: float) -> float:
    """
    Description:
        Normalised frequency (V number) for a rectangular dielectric waveguide.
        Uses the geometric mean of width and height as the equivalent radius.
        This is the standard figure of merit for estimating the number of guided modes.

    Inputs:
        width_um      : float — waveguide core width (µm)
        height_um     : float — waveguide core height (µm)
        n_core        : float — core refractive index (dimensionless)
        n_clad        : float — cladding refractive index (dimensionless)
        wavelength_um : float — free-space wavelength (µm)

    Outputs:
        V : float — normalised frequency (dimensionless)

    Units:
        width_um, height_um, wavelength_um → µm
        V                                  → dimensionless

    Example:
        >>> v_number(0.80, 0.22, 2.0, 1.45, 0.780)
        3.14...
    """
    NA = np.sqrt(n_core**2 - n_clad**2)
    d_eff = np.sqrt(width_um * height_um)
    return float(np.pi * d_eff * NA / wavelength_um)


def numerical_aperture(n_core: float, n_clad: float) -> float:
    """
    Description:
        Numerical aperture of a waveguide — the sine of the maximum acceptance
        half-angle. Useful for estimating coupling efficiency from free space.

    Inputs:
        n_core : float — core refractive index
        n_clad : float — cladding refractive index

    Outputs:
        NA : float — numerical aperture (dimensionless)

    Units:
        All dimensionless.

    Example:
        >>> numerical_aperture(2.0, 1.45)
        0.895...
    """
    return float(np.sqrt(n_core**2 - n_clad**2))
