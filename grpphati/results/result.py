import numpy as np


def _map_to_cols(rep, cols):
    return [cols[idx] for idx in rep]


class Result:
    def __init__(self, barcode=[], reps=[]):
        self.barcode = barcode
        self.reps = reps

    def add_bar(self, bar, with_rep=None):
        self.barcode.append(bar)
        self.reps.append(with_rep)

    def add_paired(self, pairs, cols, reps=None):
        for bar_idx, [birth_idx, death_idx] in enumerate(pairs):
            birth_time = cols[birth_idx].get_entrance_time()
            death_time = cols[death_idx].get_entrance_time()
            # Don't add 0 persistence points?
            if birth_time == death_time:
                continue
            dimension = cols[birth_idx].dimension()
            # Only computing in dimension 1
            if dimension != 1:
                continue
            if reps is not None:
                self.add_bar(
                    [birth_time, death_time], _map_to_cols(reps[bar_idx], cols)
                )
            else:
                self.add_bar([birth_time, death_time])

    def add_unpaired(self, pairs, cols, reps=None):
        all_paired_idxs = [idx for pair in pairs for idx in pair]
        dim_1_idxs = [idx for idx, col in enumerate(cols) if col.dimension() == 1]
        unpaired_idxs = [idx for idx in dim_1_idxs if idx not in all_paired_idxs]
        for bar_idx, idx in enumerate(unpaired_idxs):
            birth_time = cols[idx].get_entrance_time()
            if reps is not None:
                self.add_bar(
                    [birth_time, np.inf], with_rep=_map_to_cols(reps[bar_idx], cols)
                )
            else:
                self.add_bar([birth_time, np.inf])

    def add_unpaired_raw(self, unpaired_idxs, cols, reps=None):
        for bar_idx, idx in enumerate(unpaired_idxs):
            if cols[idx].dimension() != 1:
                continue
            birth_time = cols[idx].get_entrance_time()
            if reps is not None:
                self.add_bar(
                    [birth_time, np.inf], with_rep=_map_to_cols(reps[bar_idx], cols)
                )
            else:
                self.add_bar([birth_time, np.inf])

    def extend(self, other_result):
        self.barcode.extend(other_result.barcode)
        self.reps.extend(other_result.reps)

    def num_features(self):
        return len(self.barcode)

    def num_infinite_features(self):
        return len([True for bar in self.barcode if bar[1] == np.inf])

    def num_finite_features(self):
        return len([True for bar in self.barcode if np.isfinite(bar[1])])

    def max_finite_feature(self):
        try:
            return max(bar[1] for bar in self.barcode if np.isfinite(bar[1]))
        except ValueError:
            return None

    def min_finite_feature(self):
        try:
            return min(bar[1] for bar in self.barcode if np.isfinite(bar[1]))
        except ValueError:
            return None

    def compute_betti_curve(self, x_range):
        n_features = self.num_features()
        return [
            n_features - len([True for bar in self.barcode if bar[1] <= x])
            for x in x_range
        ]

    @staticmethod
    def merge(*results):
        ret_val = results[0]
        for i in range(1, len(results)):
            ret_val.extend(results[i])
        return ret_val

    @classmethod
    def empty(cls):
        return cls(barcode=[], reps=[])
