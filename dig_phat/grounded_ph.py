import numpy as np
from dig_phat.filtrations import ShortestPathFiltration
from dig_phat.homology import Homology
from dig_phat.columns import Column, convert_to_sparse
from dig_phat.diagram_utils import add_paired, add_unpaired
import phat
import time
from pprint import pprint

# TODO: Change filtration interface so that it will return a map of filtered edges
# FOR NOW ASSUMES REG_PATH
def grounded_ph(
    G, filtration, homology, verbose=True, reduction=phat.reductions.twist_reduction
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


def grpph(G, verbose=True, reduction=phat.reductions.twist_reduction):
    return grounded_ph(
        G,
        ShortestPathFiltration(G),
        Homology.REG_PATH,
        verbose=verbose,
        reduction=reduction,
    )
