from .abstract import Backend
from lophat import compute_pairings
from grpphati.sparsifiers import Sparsifier, ListSparsifier
from grpphati.results import Result


class LoPHATBackend(Backend):
    def __init__(
        self,
        sparsifier: Sparsifier = ListSparsifier(return_dimension=False),
    ):
        self.sparsifier = sparsifier

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: (col.get_entrance_time(), col.dimension()))
        sparse_cols = self.sparsifier(cols)
        diagram = compute_pairings(sparse_cols)
        pairs = list(diagram.paired)
        pairs.sort()
        result = Result.empty()
        result.add_paired(pairs, cols)
        result.add_unpaired_raw(diagram.unpaired, cols)
        return result
