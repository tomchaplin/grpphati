from .abstract import Backend
import phat
from grpphati.utils.column import convert_to_sparse
from grpphati.results import Result


class PHATBackend(Backend):
    def __init__(self, reduction: phat.reductions = phat.reductions.twist_reduction):
        self.reduction = reduction

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: (col.entrance_time, col.dimension()))
        sparse_cols = convert_to_sparse(cols)
        boundary_matrix = phat.boundary_matrix(
            columns=sparse_cols, representation=phat.representations.sparse_pivot_column
        )
        pairs = boundary_matrix.compute_persistence_pairs(reduction=self.reduction)
        pairs.sort()
        result = Result.empty()
        result.add_paired(pairs, cols)
        result.add_unpaired(pairs, cols)
        return result
