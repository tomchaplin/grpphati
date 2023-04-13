from .abstract import Backend
from grpphati.sparsifiers import Sparsifier, ListSparsifier
from grpphati.results import Result

try:
    from lophat import compute_pairings, LoPhatOptions
except ImportError:
    _has_lophat = False
else:
    _has_lophat = True


class LoPHATBackend(Backend):
    def __init__(
        self,
        sparsifier: Sparsifier = ListSparsifier(return_dimension=True),
        num_threads: int = 0,
        min_chunk_len: int = 0,
    ):
        self.sparsifier = sparsifier
        self.num_threads = num_threads
        self.min_chunk_len = min_chunk_len
        if not _has_lophat:
            raise ImportError("Optional dependency lophat required")

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: (col.get_entrance_time(), col.dimension()))
        sparse_cols = self.sparsifier(cols)
        opts = LoPhatOptions(
            num_threads=self.num_threads, min_chunk_len=self.min_chunk_len
        )
        diagram = compute_pairings(sparse_cols, options=opts)
        pairs = list(diagram.paired)
        pairs.sort()
        result = Result.empty()
        result.add_paired(pairs, cols)
        result.add_unpaired_raw(diagram.unpaired, cols)
        return result
