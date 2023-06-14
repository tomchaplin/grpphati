## This file is kept for historical reasons
## We remove dependency on PHAT due to packaging issues

from .abstract import Backend
import phat
from grpphati.sparsifiers import Sparsifier, ListSparsifier
from grpphati.results import Result


class PHATBackend(Backend):
    def __init__(
        self,
        reduction: phat.reductions = phat.reductions.twist_reduction,
        sparsifier: Sparsifier = ListSparsifier(return_dimension=True),
    ):
        self.reduction = reduction
        self.sparsifier = sparsifier

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: (col.get_entrance_time(), col.dimension()))
        sparse_cols = self.sparsifier(cols)
        boundary_matrix = phat.boundary_matrix(
            columns=sparse_cols, representation=phat.representations.sparse_pivot_column
        )
        pairs = boundary_matrix.compute_persistence_pairs(reduction=self.reduction)
        pairs.sort()
        result = Result.empty()
        result.add_paired(pairs, cols)
        result.add_unpaired(pairs, cols)
        return result
