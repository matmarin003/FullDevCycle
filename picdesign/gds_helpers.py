"""
GDS layout helpers for passive PIC components using gdstk.
Builds SiN-on-SiO2 passive structures: waveguides, rings, MZIs, and full chips.
All components are purely passive — no metal heaters, no p/n junctions.

Layer map (compatible with common SiN foundry conventions):
    WG_CORE  = (1, 0)  — SiN waveguide core
    WG_CLAD  = (2, 0)  — SiO2 upper cladding (if patterned)
    CHIP_EDGE = (10, 0) — chip boundary / dicing lane marker
"""

import numpy as np
import gdstk


LAYER_WG_CORE = (1, 0)
LAYER_WG_CLAD = (2, 0)
LAYER_CHIP_EDGE = (10, 0)


def _check_lib(lib):
    if not isinstance(lib, gdstk.Library):
        raise TypeError("lib must be a gdstk.Library instance")


def straight_waveguide(lib: gdstk.Library, cell_name: str,
                        length_um: float, width_um: float,
                        layer: tuple = LAYER_WG_CORE) -> gdstk.Cell:
    """
    Description:
        Create a straight waveguide GDS cell as a rectangular polygon.
        The waveguide runs along the x-axis, centred on y = 0.
        Input port is at (0, 0) and output port at (length_um, 0).

    Inputs:
        lib       : gdstk.Library — parent GDS library to add the cell to
        cell_name : str           — name of the new cell
        length_um : float         — waveguide length (µm)
        width_um  : float         — waveguide core width (µm)
        layer     : tuple         — GDS (layer, datatype), default LAYER_WG_CORE

    Outputs:
        cell : gdstk.Cell — the created cell with the waveguide polygon

    Units:
        length_um, width_um → µm (GDS units)

    Example:
        >>> import gdstk
        >>> lib = gdstk.Library()
        >>> cell = straight_waveguide(lib, 'WG_50um', 50.0, 0.8)
    """
    _check_lib(lib)
    cell = lib.new_cell(cell_name)
    rect = gdstk.rectangle(
        (0, -width_um / 2), (length_um, width_um / 2),
        layer=layer[0], datatype=layer[1]
    )
    cell.add(rect)
    return cell


def ring_resonator_cell(lib: gdstk.Library, cell_name: str,
                         radius_um: float, width_um: float,
                         gap_um: float, bus_length_um: float,
                         layer: tuple = LAYER_WG_CORE) -> gdstk.Cell:
    """
    Description:
        Create a ring resonator GDS cell with a single straight bus waveguide
        and one circular ring coupled through a gap. The bus runs along the
        x-axis; the ring centre sits above the bus at y = gap + width + radius.

    Inputs:
        lib           : gdstk.Library — parent GDS library
        cell_name     : str           — cell name
        radius_um     : float         — ring radius to core centre (µm)
        width_um      : float         — waveguide width for both bus and ring (µm)
        gap_um        : float         — coupling gap between bus top and ring bottom (µm)
        bus_length_um : float         — total bus length (µm)
        layer         : tuple         — GDS layer, default WG_CORE

    Outputs:
        cell : gdstk.Cell — ring resonator cell

    Units:
        All dimensions in µm.

    Example:
        >>> lib = gdstk.Library()
        >>> cell = ring_resonator_cell(lib, 'RING_R50', 50.0, 0.8, 0.3, 200.0)
    """
    _check_lib(lib)
    cell = lib.new_cell(cell_name)

    # Bus waveguide
    bus = gdstk.rectangle(
        (0, -width_um / 2), (bus_length_um, width_um / 2),
        layer=layer[0], datatype=layer[1]
    )
    cell.add(bus)

    # Ring: approximate as a thick annulus using gdstk.ellipse
    ring_cx = bus_length_um / 2
    ring_cy = width_um / 2 + gap_um + radius_um
    ring = gdstk.ellipse(
        (ring_cx, ring_cy),
        radius_um + width_um / 2,      # outer radius
        inner_radius=radius_um - width_um / 2,  # inner radius
        layer=layer[0], datatype=layer[1]
    )
    cell.add(ring)
    return cell


def mzi_cell(lib: gdstk.Library, cell_name: str,
              delta_L_um: float, arm_length_um: float,
              width_um: float, s_bend_height_um: float = 10.0,
              layer: tuple = LAYER_WG_CORE) -> gdstk.Cell:
    """
    Description:
        Create a simple MZI GDS cell using straight arms and S-bends to
        separate the two arms. The MZI consists of:
        – input straight section (50 µm)
        – Y-junction splitter (approximated as a branching point)
        – lower reference arm of length arm_length_um
        – upper sensing arm of length arm_length_um + delta_L_um
        – S-bends to bring both arms back to the same y-coordinate
        – output coupler and straight section

        Note: Y-junctions are approximated as simple diagonal splits for
        the GDS mask; accurate shapes should be replaced with optimised
        taper profiles from Homework 4.

    Inputs:
        lib               : gdstk.Library — parent GDS library
        cell_name         : str           — cell name
        delta_L_um        : float         — path-length imbalance (µm)
        arm_length_um     : float         — length of the reference arm (µm)
        width_um          : float         — waveguide width (µm)
        s_bend_height_um  : float         — vertical separation of arms (µm), default 10
        layer             : tuple         — GDS layer

    Outputs:
        cell : gdstk.Cell — MZI cell

    Units:
        All dimensions in µm.

    Example:
        >>> lib = gdstk.Library()
        >>> cell = mzi_cell(lib, 'MZI_dL100', 100.0, 400.0, 0.8)
    """
    _check_lib(lib)
    cell = lib.new_cell(cell_name)

    in_len = 50.0
    out_len = 50.0
    bend_len = s_bend_height_um * 3.0  # approximate S-bend x-extent

    # Input waveguide
    cell.add(gdstk.rectangle(
        (0, -width_um / 2), (in_len, width_um / 2),
        layer=layer[0], datatype=layer[1]
    ))

    x0 = in_len
    y_ref = 0.0
    y_sens = s_bend_height_um

    # Reference (lower) arm
    cell.add(gdstk.rectangle(
        (x0 + bend_len, y_ref - width_um / 2),
        (x0 + bend_len + arm_length_um, y_ref + width_um / 2),
        layer=layer[0], datatype=layer[1]
    ))

    # Sensing (upper) arm with extra ΔL
    extra_half = delta_L_um / 2.0
    cell.add(gdstk.rectangle(
        (x0 + bend_len - extra_half, y_sens - width_um / 2),
        (x0 + bend_len + arm_length_um + extra_half, y_sens + width_um / 2),
        layer=layer[0], datatype=layer[1]
    ))

    # S-bends as diagonal polygons (simplified mask approximation)
    def sbend_polygon(x_start, y_start, y_end, dx, w, lay):
        pts = np.array([
            [x_start, y_start - w / 2],
            [x_start + dx, y_end - w / 2],
            [x_start + dx, y_end + w / 2],
            [x_start, y_start + w / 2],
        ])
        return gdstk.Polygon(pts, layer=lay[0], datatype=lay[1])

    # Input S-bends
    cell.add(sbend_polygon(x0, 0, y_ref, bend_len, width_um, layer))
    cell.add(sbend_polygon(x0, 0, y_sens, bend_len, width_um, layer))

    x1 = x0 + bend_len + arm_length_um
    # Output S-bends (mirror)
    cell.add(sbend_polygon(x1, y_ref, 0, bend_len, width_um, layer))
    cell.add(sbend_polygon(x1 + extra_half, y_sens, 0, bend_len, width_um, layer))

    x_out = x1 + bend_len + extra_half
    # Output waveguide
    cell.add(gdstk.rectangle(
        (x_out, -width_um / 2), (x_out + out_len, width_um / 2),
        layer=layer[0], datatype=layer[1]
    ))
    return cell


def full_biosensor_layout(filename: str,
                           wg_width_um: float = 0.80,
                           ring_radius_um: float = 50.0,
                           ring_gap_um: float = 0.30,
                           mzi_delta_L_um: float = 100.0,
                           chip_x_um: float = 5000.0,
                           chip_y_um: float = 1000.0) -> gdstk.Library:
    """
    Description:
        Generate a complete passive biosensor PIC GDS layout containing:
          1. Input edge coupler taper
          2. Bus waveguide
          3. Reference (straight) waveguide
          4. MZI sensing arm (with path-length imbalance)
          5. Ring resonator sensor
          6. Output edge coupler tapers
        All on the SiN WG_CORE layer. The chip boundary is drawn on CHIP_EDGE.
        This layout is derived from the multi-device patterns in Homework 4.

    Inputs:
        filename       : str   — output .gds file path
        wg_width_um    : float — waveguide core width (µm), default 0.8
        ring_radius_um : float — ring resonator radius (µm), default 50
        ring_gap_um    : float — ring coupling gap (µm), default 0.3
        mzi_delta_L_um : float — MZI path-length imbalance (µm), default 100
        chip_x_um      : float — chip x dimension (µm), default 5000
        chip_y_um      : float — chip y dimension (µm), default 1000

    Outputs:
        lib : gdstk.Library — the GDS library (also written to filename)

    Units:
        All dimensions in µm.

    Example:
        >>> lib = full_biosensor_layout('biosensor.gds')
        >>> print(f"Cells: {[c.name for c in lib.cells]}")
    """
    lib = gdstk.Library(name="SiN_Biosensor", unit=1e-6, precision=1e-9)
    top = lib.new_cell("TOP")

    spacing_y = 150.0  # row spacing
    bus_len = chip_x_um - 200.0  # leave 100 µm on each side for tapers

    # Row 0: Reference straight waveguide
    ref_cell = straight_waveguide(lib, "REF_WG", bus_len, wg_width_um)
    top.add(gdstk.Reference(ref_cell, origin=(100.0, 0.0)))

    # Row 1: Ring resonator
    ring_cell = ring_resonator_cell(
        lib, "RING_SENSOR",
        ring_radius_um, wg_width_um, ring_gap_um, bus_len
    )
    top.add(gdstk.Reference(ring_cell, origin=(100.0, spacing_y)))

    # Row 2: MZI sensor
    mzi = mzi_cell(lib, "MZI_SENSOR", mzi_delta_L_um, 400.0, wg_width_um)
    top.add(gdstk.Reference(mzi, origin=(100.0, 2 * spacing_y)))

    # Chip boundary
    top.add(gdstk.rectangle(
        (0, -spacing_y / 2), (chip_x_um, 2.5 * spacing_y),
        layer=LAYER_CHIP_EDGE[0], datatype=LAYER_CHIP_EDGE[1]
    ))

    lib.write_gds(filename)
    print(f"GDS written → {filename}")
    print(f"  Cells: {[c.name for c in lib.cells]}")
    return lib


def export_component(cell: gdstk.Cell, filename: str,
                     unit: float = 1e-6,
                     precision: float = 1e-9) -> None:
    """
    Description:
        Export a single gdstk.Cell to a standalone GDS file. Wraps the cell
        in a new Library before writing. Useful for exporting individual
        components from the design library for standalone verification.

    Inputs:
        cell      : gdstk.Cell — the cell to export
        filename  : str        — output file path (e.g., 'ring.gds')
        unit      : float      — GDS database unit in metres, default 1e-6 (µm)
        precision : float      — GDS precision in metres, default 1e-9 (nm)

    Outputs:
        None (writes file to disk)

    Units:
        unit, precision → metres

    Example:
        >>> import gdstk
        >>> lib = gdstk.Library()
        >>> cell = straight_waveguide(lib, 'TEST_WG', 50.0, 0.8)
        >>> export_component(cell, 'test_wg.gds')
    """
    out_lib = gdstk.Library(name=cell.name, unit=unit, precision=precision)
    out_lib.add(cell)
    out_lib.write_gds(filename)
    print(f"Exported cell '{cell.name}' → {filename}")


# ─────────────────────────────────────────────────────────────────────────────
#  PhotonForge / Tidy3D technology helper
# ─────────────────────────────────────────────────────────────────────────────


def sin_strip_technology(wavelength_um: float = 0.780, width_um: float = 0.70,
                         thickness_um: float = 0.30,
                         n_core: float = None, n_clad: float = None,
                         core_layer: tuple = LAYER_WG_CORE,
                         clad_layer: tuple = LAYER_WG_CLAD):
    """
    Description:
        Create a PhotonForge ``Technology`` for the SiN-on-SiO2 strip-waveguide
        platform used throughout the course (visible biosensing at 660–850 nm).
        Core and cladding permittivities default to the Sellmeier indices of SiN
        and SiO2 at ``wavelength_um`` (from picdesign.materials). Assign the
        result to ``pf.config.default_technology`` before building components.
        ``photonforge`` and ``tidy3d`` are imported lazily.

    Inputs:
        wavelength_um : float — design wavelength for the default indices (µm)
        width_um      : float — nominal strip (core) width (µm)
        thickness_um  : float — core thickness/height (µm)
        n_core        : float — core index override (default: SiN Sellmeier)
        n_clad        : float — cladding index override (default: SiO2 Sellmeier)
        core_layer    : tuple — GDS (layer, datatype) for the core, default (1,0)
        clad_layer    : tuple — GDS (layer, datatype) for the cladding, default (2,0)

    Outputs:
        technology : photonforge.Technology — SiN strip-waveguide technology

    Units:
        All lengths µm; indices dimensionless.

    Example:
        >>> import photonforge as pf
        >>> from picdesign import sin_strip_technology
        >>> tech = sin_strip_technology(wavelength_um=0.780)
        >>> pf.config.default_technology = tech
    """
    import photonforge as pf
    import tidy3d as td
    from .materials import sin_refractive_index, sio2_refractive_index

    if n_core is None:
        n_core = float(sin_refractive_index(wavelength_um))
    if n_clad is None:
        n_clad = float(sio2_refractive_index(wavelength_um))
    core = td.Medium(permittivity=n_core ** 2)
    clad = td.Medium(permittivity=n_clad ** 2)
    return pf.basic_technology(core_medium=core, clad_medium=clad,
                               core_thickness=thickness_um, strip_width=width_um,
                               core_layer=core_layer, clad_layer=clad_layer)
