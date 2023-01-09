from grpphati.filtrations import ShortestPathFiltration
from grpphati.homologies import (
    DirectedFlagComplexHomology,
    RegularPathHomology,
    Homology,
)
from grpphati.optimisations import (
    all_optimisations,
    component_appendage_empty,
    component_empty,
)
from grpphati.utils.ph import compute_ph_from_cols
from typing import Type
import phat


def make_standard_pipeline(
    filtration_map,
    homology_cls: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
    optimisation_strat=None,
):
    def pipeline(G):
        dgm = compute_standard_ph(G, filtration_map, homology_cls, verbose, reduction)
        return dgm

    if optimisation_strat is None:
        return pipeline
    else:
        return optimisation_strat(pipeline)


def compute_standard_ph(
    G,
    filtration_map,
    homology: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
):
    filtration = filtration_map(G)
    # Build boundary matrix
    if verbose:
        print("Building boundary matrix")
    cols = homology.get_cells([0, 1, 2], filtration)
    if verbose:
        print(f"Filtration basis has size {len(cols)}")
    return compute_ph_from_cols(cols, verbose, reduction)


PPH = make_standard_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    optimisation_strat=component_appendage_empty,
)
PPH_par_wedge = make_standard_pipeline(
    ShortestPathFiltration, RegularPathHomology, optimisation_strat=all_optimisations
)
PdFlH = make_standard_pipeline(
    ShortestPathFiltration,
    DirectedFlagComplexHomology,
    optimisation_strat=component_empty,
)
