from grpphati.filtrations import ShortestPathFiltration
from grpphati.homologies import (
    DirectedFlagComplexHomology,
    RegularPathHomology,
    Homology,
)
from grpphati.utils.column import convert_to_sparse
from grpphati.utils.diagram import add_paired, add_unpaired
from grpphati.optimisations import (
    all_optimisations,
    component_appendage_empty,
    component_empty,
)
from typing import Type
import phat


def make_grounded_pipeline(
    filtration_map,
    homology_cls: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
    optimisation_strat=None,
):
    def pipeline(G):
        dgm = compute_grounded_ph(G, filtration_map, homology_cls, verbose, reduction)
        return dgm

    if optimisation_strat is None:
        return pipeline
    else:
        return optimisation_strat(pipeline)


def compute_grounded_ph(
    G,
    filtration_map,
    homology: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
):
    filtration = filtration_map(G)
    grounded_filtration = filtration.ground(G)
    # Build boundary matrix
    if verbose:
        print("Building boundary matrix")
    cols = homology.get_cells([0, 1], grounded_filtration) + homology.get_cells(
        [2], filtration
    )
    if verbose:
        print(f"Filtration basis has size {len(cols)}")
    # Sort basis according to entrance time and dimension
    # (if dim1 and dim2 item enter at same time, the dim1 should enter first to have a valid filtration)
    if verbose:
        print("Sorting basis")
    cols.sort(key=lambda col: (col.entrance_time, col.dimension()))
    # Convert to sparse format for PHAT
    if verbose:
        print("Building sparse matrix")
    sparse_cols = convert_to_sparse(cols)
    # Compute persistence pairs
    if verbose:
        print("Computing PH")
    boundary_matrix = phat.boundary_matrix(
        columns=sparse_cols, representation=phat.representations.sparse_pivot_column
    )
    pairs = boundary_matrix.compute_persistence_pairs(reduction=reduction)
    pairs.sort()
    # Add finite points to persistence diagram, recovering times
    if verbose:
        print("Building diagram")
    dgm = add_paired(pairs, cols)
    # Any unpaired edges must give rise to infinite features
    dgm = add_unpaired(dgm, pairs, cols)
    return dgm


GrPPH = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    optimisation_strat=component_appendage_empty,
)
GrPPH_par_wedge = make_grounded_pipeline(
    ShortestPathFiltration, RegularPathHomology, optimisation_strat=all_optimisations
)
GrPdFlH = make_grounded_pipeline(
    ShortestPathFiltration,
    DirectedFlagComplexHomology,
    optimisation_strat=component_empty,
)
