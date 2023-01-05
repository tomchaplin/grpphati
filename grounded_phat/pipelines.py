from .filtration import ShortestPathFiltration, Filtration
from .homology import (
    DirectedFlagComplexHomology,
    RegularPathHomology,
    Homology,
)
from .util.column import convert_to_sparse
from .util.diagram import add_paired, add_unpaired
from typing import Type
import phat


class GroundedPipeline:
    def __init__(
        self,
        filtration_cls: Type[Filtration],
        homology_cls: Type[Homology],
        verbose: bool = False,
        reduction: phat.reductions = phat.reductions.twist_reduction,
    ):
        self.filtration_cls = filtration_cls
        self.homology_cls = homology_cls
        self.verbose = verbose
        self.reduction = reduction

    def __call__(self, G, verbose=None, reduction=None):
        verbose = self.verbose if verbose is None else verbose
        reduction = self.reduction if reduction is None else reduction
        filtration = self.filtration_cls(G)
        dgm = grounded_ph(filtration, self.homology_cls, verbose, reduction)
        return dgm


def grounded_ph(
    filtration: Filtration,
    homology: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
):
    # Build boundary matrix
    if verbose:
        print("Building boundary matrix")
    cols = homology.get_cells([0, 1, 2], filtration)
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


GrPPH = GroundedPipeline(ShortestPathFiltration, RegularPathHomology)
GrPdFlH = GroundedPipeline(ShortestPathFiltration, DirectedFlagComplexHomology)
