from grpphati.backends.abstract import Backend
from grpphati.sparsifiers import Sparsifier, GeneratorSparsifier
from grpphati.results import Result

try:
    from persuit import std_persuit, std_persuit_serial, std_persuit_serial_bs
except ImportError:
    _has_persuit = False
else:
    _has_persuit = True


class PersuitBackend(Backend):
    def __init__(
        self,
        in_parallel=True,
        internal="vec",
        sparsifier: Sparsifier = GeneratorSparsifier(return_dimension=False),
    ):
        if not _has_persuit:
            raise ImportError("Optional dependency persuit required")
        self.in_parallel = in_parallel
        self.internal = internal
        self.sparsifier = sparsifier

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: (col.get_entrance_time(), col.dimension()))
        # Extract rows, ignore dimension
        sparse_cols = self.sparsifier(iter(cols))
        if self.in_parallel:
            pairs = std_persuit(sparse_cols)
        else:
            if self.internal == "bitset":
                pairs = std_persuit_serial_bs(sparse_cols)
            else:
                pairs = std_persuit_serial(sparse_cols)
        pairs.sort()
        result = Result.empty()
        result.add_paired(pairs, cols)
        result.add_unpaired(pairs, cols)
        return result
