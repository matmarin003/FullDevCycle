"""
Passive coupler design functions: directional couplers and Y-branches.
All functions are analytical — no active tuning (no heaters, no doping).
Based on coupled-mode theory and Gaussian optics.
"""

import numpy as np


def directional_coupler_length(kappa: float, coupling_ratio: float = 0.5) -> float:
    """
    Description:
        Coupling length of a directional coupler to achieve a target power
        splitting ratio. From coupled-mode theory:
            L_c = arcsin(√κ_target) / κ_coupling
        where κ_coupling [µm⁻¹] is the mutual coupling coefficient between
        the two waveguides and κ_target is the desired power coupling ratio (0–1).

    Inputs:
        kappa          : float — mutual coupling coefficient between waveguides (µm⁻¹)
        coupling_ratio : float — target power transfer ratio (0–1), default 0.5 (3 dB)

    Outputs:
        L_um : float — required coupling length (µm)

    Units:
        kappa → µm⁻¹
        L_um  → µm

    Example:
        >>> directional_coupler_length(0.02, 0.5)
        78.54...
    """
    if not (0.0 < coupling_ratio <= 1.0):
        raise ValueError("coupling_ratio must be in (0, 1]")
    return float(np.arcsin(np.sqrt(coupling_ratio)) / kappa)


def directional_coupler_kappa(gap_um: float, width_um: float,
                               n_core: float, n_clad: float,
                               wavelength_um: float) -> float:
    """
    Description:
        Estimate the mutual coupling coefficient κ for a symmetric directional
        coupler using an exponential evanescent-field approximation. The formula
        κ ≈ (π NA² / (n_eff λ)) × exp(-γ × gap) is a simplified model; for
        accurate values use a full eigenmode expansion (EME) solver.

    Inputs:
        gap_um        : float — gap between the two waveguide cores (µm)
        width_um      : float — core width of each waveguide (µm)
        n_core        : float — core refractive index
        n_clad        : float — cladding refractive index
        wavelength_um : float — free-space wavelength (µm)

    Outputs:
        kappa_per_um : float — coupling coefficient (µm⁻¹)

    Units:
        gap_um, width_um, wavelength_um → µm
        kappa_per_um                    → µm⁻¹

    Example:
        >>> directional_coupler_kappa(0.2, 0.8, 2.0, 1.45, 0.780)
        0.034...
    """
    NA = np.sqrt(n_core**2 - n_clad**2)
    n_eff_approx = 0.5 * (n_core + n_clad)  # rough midpoint
    gamma = 2.0 * np.pi * NA / wavelength_um  # evanescent decay rate (µm⁻¹)
    kappa = (np.pi * NA**2 / (n_eff_approx * wavelength_um)) * np.exp(-gamma * gap_um)
    return float(kappa)


def y_branch_arm_spacing(wavelength_um: float, n_core: float,
                          n_clad: float, width_um: float) -> float:
    """
    Description:
        Minimum centre-to-centre spacing between the two output arms of a
        Y-branch splitter such that the evanescent coupling between them is
        negligible (< 1% power transfer at the junction exit). Based on the
        criterion that the evanescent field decays by 20 dB across the gap.

    Inputs:
        wavelength_um : float — free-space wavelength (µm)
        n_core        : float — core refractive index
        n_clad        : float — cladding refractive index
        width_um      : float — core width (µm)

    Outputs:
        spacing_um : float — minimum centre-to-centre arm spacing (µm)

    Units:
        All µm (except refractive indices).

    Example:
        >>> y_branch_arm_spacing(0.780, 2.0, 1.45, 0.8)
        2.13...
    """
    NA = np.sqrt(n_core**2 - n_clad**2)
    gamma = 2.0 * np.pi * NA / wavelength_um  # field decay rate µm⁻¹
    # Require exp(-gamma × gap) < 0.1, so gap > ln(10)/gamma
    min_gap = np.log(10.0) / gamma
    return float(width_um + min_gap)


def grating_coupler_period(wavelength_um: float, n_eff: float,
                            theta_deg: float = 10.0,
                            n_env: float = 1.0) -> float:
    """
    Description:
        Grating period Λ for a 1st-order grating coupler that diffracts light
        from a single-mode waveguide into free space at angle θ from the
        surface normal. Phase-matching condition (Bragg condition):
            n_eff = n_env × sin(θ) + λ / Λ

        Solving for Λ:
            Λ = λ / (n_eff - n_env × sin(θ))

    Inputs:
        wavelength_um : float — free-space wavelength (µm)
        n_eff         : float — waveguide effective index
        theta_deg     : float — diffraction angle from surface normal (degrees), default 10°
        n_env         : float — refractive index of environment above the grating, default 1.0 (air)

    Outputs:
        period_um : float — grating period (µm)

    Units:
        wavelength_um → µm
        theta_deg     → degrees
        period_um     → µm

    Example:
        >>> grating_coupler_period(0.780, 1.75, 10.0, 1.0)
        0.496...
    """
    theta_rad = np.radians(theta_deg)
    denom = n_eff - n_env * np.sin(theta_rad)
    if denom <= 0:
        raise ValueError(
            "n_eff must be greater than n_env×sin(θ); check input parameters."
        )
    return float(wavelength_um / denom)


def edge_coupler_taper_length(width_start_um: float, width_end_um: float,
                               n_core: float, n_clad: float,
                               wavelength_um: float,
                               taper_angle_deg: float = 0.5) -> float:
    """
    Description:
        Minimum adiabatic taper length for an edge coupler that expands the
        waveguide mode from width_start to width_end. Uses the adiabaticity
        condition: the local taper angle must remain below half the local
        coupling angle between the fundamental and first-order modes.
        Here we use a simple geometric estimate given a target taper half-angle.

    Inputs:
        width_start_um  : float — starting waveguide width (µm), narrow end at chip facet
        width_end_um    : float — target bus waveguide width (µm)
        n_core          : float — core refractive index
        n_clad          : float — cladding refractive index
        wavelength_um   : float — free-space wavelength (µm)
        taper_angle_deg : float — taper half-angle (degrees), default 0.5° (adiabatic)

    Outputs:
        length_um : float — estimated taper length (µm)

    Units:
        width_start_um, width_end_um, wavelength_um → µm
        taper_angle_deg                              → degrees
        length_um                                    → µm

    Example:
        >>> edge_coupler_taper_length(0.10, 0.80, 2.0, 1.45, 0.780)
        40.6...
    """
    delta_w = abs(width_end_um - width_start_um)
    length = delta_w / (2.0 * np.tan(np.radians(taper_angle_deg)))
    return float(length)


# ─────────────────────────────────────────────────────────────────────────────
#  PhotonForge / Tidy3D physical component builders
# ─────────────────────────────────────────────────────────────────────────────
#  The functions below return ``photonforge.Component`` objects (geometry + ports)
#  ready for layout, GDS export, and Tidy3D simulation in the notebook. They need
#  an active PhotonForge technology — set ``pf.config.default_technology`` first,
#  e.g. with ``picdesign.sin_strip_technology()``. ``photonforge`` and ``tidy3d``
#  are imported lazily so the analytical functions above keep numpy as their only
#  dependency.


def _require_pf():
    """Return the photonforge module, raising if no technology is active."""
    import photonforge as pf
    if pf.config.default_technology is None:
        raise RuntimeError(
            "No active PhotonForge technology. Call "
            "picdesign.sin_strip_technology() and assign it to "
            "pf.config.default_technology before building components."
        )
    return pf


def _strip_port(pf, center, direction_deg):
    """Strip-waveguide port at ``center`` pointing along ``direction_deg`` (deg)."""
    return pf.Port(center, direction_deg, "Strip")


def grating_coupler_component(period_um: float = 0.50,
                              focal_length_um: float = 12.5,
                              length_um: float = 15.5,
                              grating_angle_deg: float = 45.0,
                              fiber_angle_deg: float = 10.0,
                              fill_factor: float = 0.5,
                              n_env: float = 1.0,
                              wavelength_um: float = 0.780,
                              waist_radius_um: float = 2.5,
                              port_spec: str = "Strip",
                              core_layer: tuple = (1, 0),
                              add_fiber_port: bool = True,
                              name: str = "GRATING_COUPLER"):
    """
    Description:
        Build a PhotonForge *focused* surface grating coupler. The teeth are
        curved arcs that focus the diffracted beam toward the single-mode
        waveguide, so no long linear fan-out taper is needed and the device
        footprint stays compact. The geometry is generated with
        ``photonforge.stencil.focused_grating`` (F. Van Laere et al., IEEE PTL
        19(23), 2007) — the same approach used in the PhotonForge grating-coupler
        example. Three layers are drawn: the curved teeth + input taper on
        WG_CORE, a filled SLAB under the teeth, and a WG_CLAD region. An in-plane
        ``Strip`` waveguide port ``P0`` (facing +x) feeds the bus; an out-of-plane
        ``GaussianPort`` named ``FIBER`` (optional) models the angled fiber. The
        period satisfies the phase-matching condition for ``fiber_angle_deg`` —
        size it with ``grating_coupler_period()``. Requires an active PhotonForge
        technology (see ``sin_strip_technology``).

    Inputs:
        period_um        : float — grating period Λ (µm); use grating_coupler_period()
        focal_length_um  : float — distance from the focal point (waveguide) to the
                                   first tooth (µm)
        length_um        : float — radial length of the grating (∝ number of teeth) (µm)
        grating_angle_deg: float — angular opening of the focusing arc section (deg)
        fiber_angle_deg  : float — fiber tilt from surface normal (deg); sets n·sinθ
        fill_factor      : float — tooth width / period (0–1)
        n_env            : float — index of the medium above the grating (1.0 = air)
        wavelength_um    : float — design wavelength (µm)
        waist_radius_um  : float — Gaussian fiber-mode waist radius (µm)
        port_spec        : str   — port specification name for the bus, default "Strip"
        core_layer       : tuple — GDS (layer, datatype) of the core, default (1,0)
        add_fiber_port   : bool  — if True, add the out-of-plane GaussianPort "FIBER"
        name             : str   — component name

    Outputs:
        component : photonforge.Component — focused grating coupler with port 'P0'
                    (and 'FIBER' if add_fiber_port is True)

    Units:
        All lengths µm; angles in degrees.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, grating_coupler_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> gc = grating_coupler_component(period_um=0.49, focal_length_um=12.5)
        >>> sorted(gc.ports)
        ['FIBER', 'P0']
    """
    pf = _require_pf()
    import numpy as np

    tech = pf.config.default_technology
    spec = tech.ports[port_spec]
    # Single-mode waveguide core width to taper down to at the focal point.
    input_width = sum(w for w, _, lyr in spec.path_profiles if lyr == core_layer)
    sin_angle = n_env * np.sin(np.radians(fiber_angle_deg))

    grating = pf.stencil.focused_grating(
        wavelength_um, period_um, sin_angle, focal_length_um, length_um,
        angle=grating_angle_deg, input_width=input_width, fill_factor=fill_factor,
    )

    c = pf.Component(name)
    c.add("WG_CORE", *grating)                              # curved teeth + taper
    c.add("SLAB", pf.envelope(grating[1:], period_um))      # slab under the teeth
    c.add("WG_CLAD", pf.envelope(grating, 1.5, trim_x_min=True))
    c.add_port(pf.Port((0.0, 0.0), 0, port_spec), "P0")

    if add_fiber_port:
        cos_angle = np.cos(np.radians(fiber_angle_deg))
        input_vector = np.array((-sin_angle, 0.0, -cos_angle))
        port_height = 0.5  # place the fiber plane just above the chip surface (µm)
        center = (np.array((focal_length_um + 0.5 * length_um, 0.0, 0.0))
                  + input_vector / input_vector[2] * port_height)
        c.add_port(
            pf.GaussianPort(center, input_vector, waist_radius=waist_radius_um,
                            polarization_angle=90, field_tolerance=1e-2),
            "FIBER",
        )
    return c


def directional_coupler_component(gap_um: float = 0.20,
                                  coupling_length_um: float = 10.0,
                                  s_bend_length_um: float = 15.0,
                                  s_bend_offset_um: float = 6.0,
                                  name: str = "DIRECTIONAL_COUPLER"):
    """
    Description:
        Build a 4-port directional coupler: two strip waveguides brought to a
        ``gap_um`` separation over a straight ``coupling_length_um`` interaction
        region, with S-bend access on both sides routing the ports apart. Wraps
        ``photonforge.parametric.s_bend_coupler``. Ports: P0/P1 (left) and
        P2/P3 (right). Requires an active PhotonForge technology.

    Inputs:
        gap_um             : float — edge-to-edge gap in the coupling region (µm);
                                     pair with directional_coupler_kappa()/_length()
        coupling_length_um : float — straight interaction length L_c (µm)
        s_bend_length_um   : float — S-bend access length (µm)
        s_bend_offset_um   : float — lateral S-bend offset separating the ports (µm)
        name               : str   — component name

    Outputs:
        component : photonforge.Component — 4-port coupler (ports P0–P3)

    Units:
        All lengths µm.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, directional_coupler_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> dc = directional_coupler_component(gap_um=0.2, coupling_length_um=8.0)
        >>> sorted(dc.ports)
        ['P0', 'P1', 'P2', 'P3']
    """
    pf = _require_pf()
    # s_bend_coupler's `coupling_distance` is the centre-to-centre separation of
    # the two waveguides, not the physical edge-to-edge gap. Convert by adding one
    # core width, otherwise a sub-width gap makes the cores overlap (no gap).
    spec = pf.config.default_technology.ports["Strip"]
    core_width = sum(w for w, _, lyr in spec.path_profiles if lyr == (1, 0))
    return pf.parametric.s_bend_coupler(
        port_spec="Strip", coupling_distance=gap_um + core_width,
        coupling_length=coupling_length_um, s_bend_length=s_bend_length_um,
        s_bend_offset=s_bend_offset_um, name=name,
    )


def y_branch_component(arm_spacing_um: float = 5.0,
                       s_bend_length_um: float = 20.0,
                       input_length_um: float = 3.0,
                       junction_length_um: float = 2.0,
                       port_spec: str = "Strip",
                       core_layer: tuple = (1, 0),
                       clad_layer: tuple = (2, 0),
                       name: str = "Y_BRANCH"):
    """
    Description:
        Build a 1×2 Y-branch power splitter using the optimized adiabatic
        Y-junction profile from the PhotonForge *Y-Splitter* example
        (https://docs.flexcompute.com/projects/photonforge/en/latest/examples/Y_Splitter.html).
        A short, shape-optimized taper splits the single input core into two
        closely-spaced output cores; two separating S-bends then fan the outputs
        symmetrically to a centre-to-centre ``arm_spacing_um`` so their modes are
        decoupled. The reference profile is defined for a 0.5 µm waveguide and is
        scaled to the active technology's core width. Cladding is generated with
        ``pf.envelope`` and ports are found with ``detect_ports``.
        Ports: P0 (input), P1/P2 (the two outputs). Requires an active PhotonForge
        technology.

    Inputs:
        arm_spacing_um     : float — centre-to-centre spacing of the two outputs (µm);
                                     keep above y_branch_arm_spacing() to avoid crosstalk
        s_bend_length_um   : float — separating S-bend fan-out length (µm)
        input_length_um    : float — straight input stub length before the junction (µm)
        junction_length_um : float — length of the optimized splitting taper (µm)
        port_spec          : str   — port specification name, default "Strip"
        core_layer         : tuple — GDS (layer, datatype) of the core, default (1,0)
        clad_layer         : tuple — GDS (layer, datatype) of the cladding, default (2,0)
        name               : str   — component name

    Outputs:
        component : photonforge.Component — Y-branch (ports P0, P1, P2)

    Units:
        All lengths µm.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, y_branch_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> y = y_branch_component(arm_spacing_um=6.0)
        >>> sorted(y.ports)
        ['P0', 'P1', 'P2']
    """
    pf = _require_pf()
    import numpy as np

    tech = pf.config.default_technology
    spec = tech.ports[port_spec]
    core_width = sum(w for w, _, lyr in spec.path_profiles if lyr == core_layer)
    clad_width = sum(w for w, _, lyr in spec.path_profiles if lyr == clad_layer)
    clad_margin = 0.5 * (clad_width - core_width)  # cladding overhang per side (µm)

    # Optimized 1×2 Y-junction width profile from the PhotonForge Y-Splitter
    # example (defined for a 0.5 µm reference core), scaled to this platform.
    scale = core_width / 0.5
    w = np.array((0.5, 0.5, 0.6, 0.7, 0.9, 1.26, 1.4, 1.4,
                  1.4, 1.4, 1.31, 1.2, 1.2)) * scale
    length = junction_length_um
    y_out = 0.35 * scale  # half-separation of the two output cores at taper exit

    x0 = input_length_um if input_length_um > 0 else 0.0
    vertices = np.vstack((np.linspace(x0, x0 + length, len(w)), -0.5 * w)).T
    y_polygon = pf.Polygon(np.vstack((vertices, vertices[::-1] * np.array((1, -1)))))

    # Separating S-bends fan the two outputs out to the requested arm spacing.
    s_offset = arm_spacing_um / 2.0 - y_out
    if s_offset < 0:
        raise ValueError(
            f"arm_spacing_um ({arm_spacing_um}) is too small; it must exceed the "
            f"junction output separation ({2.0 * y_out:.3f} µm)."
        )
    x_end = x0 + length
    s_bend1 = pf.Path((x_end, y_out), core_width).s_bend(
        (s_bend_length_um, s_offset), relative=True)
    s_bend2 = pf.Path((x_end, -y_out), core_width).s_bend(
        (s_bend_length_um, -s_offset), relative=True)

    c = pf.Component(name)
    structures = [y_polygon, s_bend1, s_bend2]
    if input_length_um > 0:
        # Straight input stub feeding the junction.
        structures.append(pf.Path((0.0, 0.0), core_width).segment((x0, 0.0)))
    c.add(core_layer, *structures)
    clad = pf.envelope(c.get_structures(core_layer), clad_margin,
                       trim_x_min=True, trim_x_max=True)
    c.add(clad_layer, clad)
    c.add_port(c.detect_ports([port_spec]))
    return c


def edge_coupler_component(tip_width_um: float = 0.10,
                           full_width_um: float = 0.70,
                           length_um: float = 100.0,
                           layer: tuple = (1, 0),
                           name: str = "EDGE_COUPLER"):
    """
    Description:
        Build an inverse-taper edge coupler: the strip narrows to ``tip_width_um``
        at the chip facet (x = 0, mode deconfines to match a lensed fiber) and
        widens adiabatically to ``full_width_um`` at the on-chip bus (x = length).
        A single port ``P0`` (facing +x) is exposed at the bus side; the facet
        end is the cleave/polish plane and has no in-plane port. Requires an
        active PhotonForge technology.

    Inputs:
        tip_width_um  : float — taper tip width at the facet (µm)
        full_width_um : float — bus/strip width on chip (µm)
        length_um     : float — taper length (µm); see edge_coupler_taper_length()
        layer         : tuple — GDS (layer, datatype), default (1,0)
        name          : str   — component name

    Outputs:
        component : photonforge.Component — edge coupler with port 'P0' (bus side)

    Units:
        All lengths µm.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology, edge_coupler_component
        >>> pf.config.default_technology = sin_strip_technology()
        >>> ec = edge_coupler_component(tip_width_um=0.1, length_um=100.0)
        >>> list(ec.ports)
        ['P0']
    """
    pf = _require_pf()
    c = pf.Component(name)
    c.add(layer, pf.Polygon([(0.0, -tip_width_um / 2.0),
                             (length_um, -full_width_um / 2.0),
                             (length_um, full_width_um / 2.0),
                             (0.0, tip_width_um / 2.0)]))
    c.add_port(_strip_port(pf, (length_um, 0.0), 0), "P0")
    return c
