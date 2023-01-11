from .abstract import Backend
from grpphati.utils.column import convert_to_sparse
from grpphati.results import Result
from importlib import import_module
import numpy as np


class EireneBackend(Backend):
    def __init__(self, runtime_path=None, sysimage=None, check_version: bool = False):
        try:
            julia_pkg_1 = __import__("julia", fromlist=["Julia"])
            Julia = getattr(julia_pkg_1, "Julia")
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Julia not installed - please install grpphati with the [eirene] feature enabled"
            )
        if not sysimage is None:
            self.rt = Julia(init_julia=True, sysimage=sysimage, runtime=runtime_path)
        else:
            self.rt = Julia(init_julia=True, runtime=runtime_path)
        julia_pkg_2 = __import__("julia", fromlist=["Main"])
        self.main = getattr(julia_pkg_2, "Main")
        if check_version:
            self.rt.using("InteractiveUtils")
            self.rt.eval("versioninfo()")
        self.rt.eval("using Eirene")

    def compute_ph(self, cols) -> Result:
        cols.sort(key=lambda col: col.dimension())
        # Dimension vector
        self.main.dv = [col.dimension() for col in cols]
        # Filtration vector (entrance times)
        self.main.fv = [col.entrance_time for col in cols]
        # Compute sparse representation
        sparse_cols = convert_to_sparse(cols)
        # Row vector - concatenation of sparse columns (indexed from 1)
        self.main.rv = [
            nonzero_row + 1
            for (_, sparse_col) in sparse_cols
            for nonzero_row in sparse_col
        ]
        # Column pointers - tells us indices at which each col starts (indexed from 1)
        col_sizes = [len(sparse_col) for (_, sparse_col) in sparse_cols]
        col_starts = [1] + [int(s + 1) for s in np.cumsum(col_sizes)]
        self.main.cp = list(col_starts)
        # Eirene computation
        self.main.eval('C = eirene(rv=rv,cp=cp,dv=dv,fv=fv, model="complex")')
        return self._build_result(cols)

    def _build_result(self, cols):
        self.main.eval("C_barcode = barcode(C, dim=1)")
        barcode = self.main.C_barcode.tolist()
        julia_reps = self.main.C["cyclerep"][2]
        dim1_cols = [col for col in cols if col.dimension() == 1]
        python_reps = [_julia_to_python_rep(rep, dim1_cols) for rep in julia_reps]
        return Result(barcode=barcode, reps=python_reps)


def _julia_to_python_rep(julia_rep, dim1_cols):
    return [dim1_cols[julia_idx - 1] for julia_idx in julia_rep]
