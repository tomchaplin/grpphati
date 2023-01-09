import phat
from grpphati.utils.diagram import add_paired, add_unpaired
from grpphati.utils.column import convert_to_sparse


def compute_ph_from_cols(
    cols, verbose: bool = False, reduction=phat.reductions.twist_reduction
):
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
