from .abstract import Backend
from grpphati.sparsifiers import Sparsifier, ListSparsifier
from grpphati.results import Result

try:
    from lophat import compute_pairings_with_reps, LoPhatOptions, compute_pairings
except ImportError:
    _has_lophat = False
else:
    _has_lophat = True


class LoPHATBackend(Backend):
    def __init__(
        self,
        sparsifier: Sparsifier = ListSparsifier(return_dimension=True),
        num_threads: int = 0,
        min_chunk_len: int = 10000,
        with_reps: bool = True,
    ):
        self.sparsifier = sparsifier
        self.num_threads = num_threads
        self.min_chunk_len = min_chunk_len
        self.with_reps = with_reps
        if not _has_lophat:
            raise ImportError("Optional dependency lophat required")

    def compute_ph(self, cols) -> Result:
        # cols.sort(key=lambda col: (col.get_entrance_time(), col.dimension()))
        cols.sort(key=lambda col: (col.dimension(), col.get_entrance_time()))
        sparse_cols = self.sparsifier(cols)
        opts = LoPhatOptions(
            num_threads=self.num_threads, min_chunk_len=self.min_chunk_len
        )
        if self.with_reps:
            diagram = compute_pairings_with_reps(iter(sparse_cols), options=opts)
            pairs_with_reps = list(zip(diagram.paired, diagram.paired_reps))
            pairs_with_reps.sort(key=lambda pwr: pwr[0])
            pairs = [pwr[0] for pwr in pairs_with_reps]
            reps = [pwr[1] for pwr in pairs_with_reps]
            result = Result.empty()
            result.add_paired(pairs, cols, reps=reps)
            result.add_unpaired_raw(diagram.unpaired, cols, reps=diagram.unpaired_reps)
            return result
        else:
            diagram = compute_pairings(iter(sparse_cols), options=opts)
            result = Result.empty()
            result.add_paired(diagram.paired, cols, reps=None)
            result.add_unpaired_raw(diagram.unpaired, cols, reps=None)
            return result
