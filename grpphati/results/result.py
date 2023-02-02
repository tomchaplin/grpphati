import numpy as np


class Result:
    def __init__(self, barcode=[], reps=[]):
        self.barcode = barcode
        self.reps = reps

    def add_bar(self, bar, with_rep=None):
        self.barcode.append(bar)
        self.reps.append(with_rep)

    def add_paired(self, pairs, cols):
        for [birth_idx, death_idx] in pairs:
            birth_time = cols[birth_idx].get_entrance_time()
            death_time = cols[death_idx].get_entrance_time()
            # Don't add 0 persistence points?
            if birth_time == death_time:
                continue
            dimension = cols[birth_idx].dimension()
            # Only computing in dimension 1
            if dimension != 1:
                continue
            self.add_bar([birth_time, death_time])

    def add_unpaired(self, pairs, cols):
        all_paired_idxs = [idx for pair in pairs for idx in pair]
        dim_1_idxs = [idx for idx, col in enumerate(cols) if col.dimension() == 1]
        unpaired_idxs = [idx for idx in dim_1_idxs if idx not in all_paired_idxs]
        for idx in unpaired_idxs:
            birth_time = cols[idx].get_entrance_time()
            self.add_bar([birth_time, np.inf])

    def extend(self, other_result):
        self.barcode.extend(other_result.barcode)
        self.reps.extend(other_result.reps)

    @staticmethod
    def merge(*results):
        ret_val = results[0]
        for i in range(1, len(results)):
            ret_val.extend(results[i])
        return ret_val

    @classmethod
    def empty(cls):
        return cls(barcode=[], reps=[])
