from grounded_phat.filtrations import ShortestPathFiltration, Filtration
from grounded_phat.homology import (
    DirectedFlagComplexHomology,
    RegularPathHomology,
    Homology,
)
from grounded_phat.columns import convert_to_sparse
from grounded_phat.diagram_utils import add_paired, add_unpaired
from typing import Type
import phat
import time


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

    def __call__(self, G):
        filtration = self.filtration_cls(G)
        dgm = grounded_ph(filtration, self.homology_cls, self.verbose, self.reduction)
        return dgm


def grounded_ph(
    filtration: Filtration,
    homology: Type[Homology],
    verbose: bool = False,
    reduction: phat.reductions = phat.reductions.twist_reduction,
):
    ## Build boundary matrix
    if verbose:
        print("Building boundary matrix")
        tic = time.time()

    # Build up the basis that we will filter by
    cols = homology.get_cells([0, 1, 2], filtration)
    # Sort according to entrance time and dimension
    # (if dim1 and dim2 item enter at same time, the dim1 should enter first to have a valid filtration)
    cols.sort(key=lambda col: (col.entrance_time, col.dimension()))
    # Convert to sparse format for PHAT
    sparse_cols = convert_to_sparse(cols)

    ## Compute persistence pairs
    if verbose:
        print(f"Filtration basis has size {len(cols)}")
        print("Computing PH")

    boundary_matrix = phat.boundary_matrix(
        columns=sparse_cols, representation=phat.representations.sparse_pivot_column
    )

    pairs = boundary_matrix.compute_persistence_pairs(reduction=reduction)
    pairs.sort()

    ## Add finite points to persistence diagram, recovering times
    dgm = add_paired(pairs, cols)

    ## TODO: Add unpaired edges
    dgm = add_unpaired(dgm, pairs, cols)

    if verbose:
        print("Computation took %.3g seconds" % (time.time() - tic))

    return dgm


GrPPH = GroundedPipeline(ShortestPathFiltration, RegularPathHomology)
GrPdFlH = GroundedPipeline(ShortestPathFiltration, DirectedFlagComplexHomology)
