"""
Life Cycle Assessment (LCA) scoring functions for passive PIC platforms.
Provides a simple weighted-sum LCA score calculator and preset variable
dictionaries for common passive photonics platforms (SiN, SOI).
"""

import numpy as np
from typing import Dict


# ---------------------------------------------------------------------------
# Default LCA variable definitions and normalised reference values
# ---------------------------------------------------------------------------

# SiN-on-SiO2 passive platform (visible biosensing, 660–850 nm)
# Values are relative scores: 0 = best (lowest impact), 10 = worst
SIN_VISIBLE_LCA_SCORES: Dict[str, float] = {
    "co2_equivalent_emissions": 6.0,   # High-temperature LPCVD deposition
    "process_energy": 7.0,             # LPCVD requires 700–900 °C furnace anneal
    "water_consumption": 5.0,          # Wet cleans + CMP slurry rinse
    "etch_chemistry_hazard": 8.0,      # CF4/CHF3 fluorinated RIE chemistry
    "wafer_yield": 3.0,                # Mature 200 mm CMOS-compatible process
    "material_scarcity": 2.0,          # Si and N are abundant; SiH4 handling needed
    "device_lifetime": 2.0,            # SiN very stable; no degradation at RT
    "packaging_burden": 4.0,           # Edge or grating coupling; no hermetic sealing
    "recyclability": 6.0,              # Si substrate recoverable; SiN coating non-trivial
}

SOI_TELECOM_LCA_SCORES: Dict[str, float] = {
    "co2_equivalent_emissions": 5.0,
    "process_energy": 6.0,
    "water_consumption": 6.0,
    "etch_chemistry_hazard": 7.0,
    "wafer_yield": 2.0,
    "material_scarcity": 2.0,
    "device_lifetime": 3.0,
    "packaging_burden": 5.0,
    "recyclability": 5.0,
}

# Default equal weights (all variables equally important)
DEFAULT_LCA_WEIGHTS: Dict[str, float] = {k: 1.0 for k in SIN_VISIBLE_LCA_SCORES}


def lca_score(variables: Dict[str, float],
              weights: Dict[str, float] | None = None) -> dict:
    """
    Description:
        Compute a simplified weighted-sum Life Cycle Assessment (LCA) score
        for a passive PIC platform. Each variable is scored 0–10 (lower = better
        environmental impact). The total score is:
            LCA_total = Σ (weight_i × score_i) / Σ weight_i

        This is a relative / screening-level LCA — it does not replace a
        full ISO 14040/14044 LCA study but is useful for platform comparison.

    Inputs:
        variables : dict[str, float] — LCA variable name → score (0–10)
        weights   : dict[str, float] — variable name → weight (default equal)
                    If None, all weights are set to 1.0.

    Outputs:
        dict with keys:
            'total_score'      : float — weighted average score (0–10)
            'individual_scores': dict  — per-variable weighted contributions
            'dominant_impact'  : str   — variable with the highest weighted score

    Units:
        Scores → dimensionless (0 = no impact, 10 = maximum impact)

    Example:
        >>> from picdesign.lca import lca_score, SIN_VISIBLE_LCA_SCORES
        >>> result = lca_score(SIN_VISIBLE_LCA_SCORES)
        >>> print(result['total_score'])
        4.78...
    """
    if weights is None:
        weights = {k: 1.0 for k in variables}

    total_weight = sum(weights.get(k, 1.0) for k in variables)
    weighted_sum = sum(variables[k] * weights.get(k, 1.0) for k in variables)
    total_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    individual = {k: variables[k] * weights.get(k, 1.0) / total_weight
                  for k in variables}

    dominant = max(individual, key=lambda k: individual[k])

    return {
        "total_score": float(total_score),
        "individual_scores": individual,
        "dominant_impact": dominant,
    }


def compare_platforms(platforms: Dict[str, Dict[str, float]],
                      weights: Dict[str, float] | None = None) -> dict:
    """
    Description:
        Compare LCA scores across multiple passive PIC platforms. Ranks them
        from lowest (best) to highest (worst) environmental impact.

    Inputs:
        platforms : dict[str, dict] — platform name → LCA variable scores dict
        weights   : dict or None    — shared weights for all variables

    Outputs:
        dict with keys:
            'ranking'       : list[str]  — platform names sorted best→worst
            'scores'        : dict[str, float] — per-platform total score
            'best_platform' : str        — platform with the lowest score

    Units:
        Scores → dimensionless

    Example:
        >>> from picdesign.lca import compare_platforms, SIN_VISIBLE_LCA_SCORES, SOI_TELECOM_LCA_SCORES
        >>> result = compare_platforms({'SiN': SIN_VISIBLE_LCA_SCORES, 'SOI': SOI_TELECOM_LCA_SCORES})
    """
    scores = {name: lca_score(vars_, weights)["total_score"]
              for name, vars_ in platforms.items()}
    ranking = sorted(scores, key=lambda k: scores[k])
    return {
        "ranking": ranking,
        "scores": scores,
        "best_platform": ranking[0],
    }


def lca_radar_data(variables: Dict[str, float]) -> tuple:
    """
    Description:
        Prepare data for a radar (spider) chart of LCA scores.
        Returns the variable names and their scores in the order needed
        for matplotlib's polar axes.

    Inputs:
        variables : dict[str, float] — LCA variable name → score (0–10)

    Outputs:
        (labels, values, angles) where:
            labels : list[str]     — variable names
            values : list[float]   — scores (repeated first value to close the polygon)
            angles : ndarray       — angle positions in radians (closed polygon)

    Units:
        Scores → dimensionless

    Example:
        >>> labels, values, angles = lca_radar_data(SIN_VISIBLE_LCA_SCORES)
    """
    labels = list(variables.keys())
    values = [variables[k] for k in labels]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    # Close the polygon
    values += values[:1]
    angles += angles[:1]
    return labels, values, np.array(angles)
