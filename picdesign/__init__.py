"""
picdesign — PIC Design Common Library
UNAL-BSU PIC Design Course, Spring 2025

Passive integrated photonics design toolkit for SiN-on-SiO2 visible
biosensing at 660–850 nm. All functions are purely passive (no doping,
no thermal tuning, no carrier injection).

Modules:
    materials       — Sellmeier models for SiN, SiO2
    waveguides      — single-mode condition, confinement, loss conversion, bend loss
    resonators      — ring FSR, Q factor, transmission spectra
    interferometers — MZI FSR, path-length imbalance, transmission, sensitivity
    couplers        — directional coupler, Y-branch, grating coupler, edge coupler
    dispersion      — group index, GVD, beta coefficients, nonlinear coefficient
    lca             — LCA score calculator and platform comparison
    gds_helpers     — gdstk-based GDS layout generation and export

Quick start:
    >>> from picdesign.materials import sin_refractive_index
    >>> from picdesign.resonators import ring_fsr
    >>> n = sin_refractive_index(0.780)
    >>> fsr = ring_fsr(n, 50.0, 0.780)
"""

from .materials import sin_refractive_index, sio2_refractive_index, v_number
from .waveguides import (
    single_mode_condition,
    confinement_factor,
    propagation_loss_db_per_cm_to_per_m,
    propagation_loss_per_m_to_db_per_cm,
    bend_loss_estimate,
    minimum_bend_radius,
)
from .resonators import (
    ring_fsr,
    ring_fsr_group,
    ring_circumference,
    ring_radius_from_fsr,
    ring_q_factor,
    ring_transmission,
    ring_resonator_component,
)
from .interferometers import (
    mzi_fsr,
    mzi_path_length_imbalance,
    mzi_transmission,
    mzi_sensitivity,
    mzi_arm_lengths,
    mzi_component,
)
from .couplers import (
    directional_coupler_length,
    directional_coupler_kappa,
    grating_coupler_period,
    edge_coupler_taper_length,
    y_branch_arm_spacing,
    grating_coupler_component,
    directional_coupler_component,
    y_branch_component,
    edge_coupler_component,
)
from .dispersion import (
    group_index,
    gvd_coefficient,
    beta2_from_D,
    D_from_beta2,
    nonlinear_coefficient,
    effective_mode_area,
)
from .lca import (
    lca_score,
    compare_platforms,
    lca_radar_data,
    SIN_VISIBLE_LCA_SCORES,
    SOI_TELECOM_LCA_SCORES,
    DEFAULT_LCA_WEIGHTS,
)
from .gds_helpers import (
    straight_waveguide,
    ring_resonator_cell,
    mzi_cell,
    full_biosensor_layout,
    export_component,
    sin_strip_technology,
    LAYER_WG_CORE,
    LAYER_WG_CLAD,
    LAYER_CHIP_EDGE,
)

__version__ = "1.0.0"
__author__ = "Mateo Marin"
__course__ = "UNAL-BSU PIC Design, Spring 2025"
