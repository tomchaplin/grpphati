import numpy as np


def add_paired(pairs, cols):
    dgm = []

    for [birth_idx, death_idx] in pairs:
        birth_time = cols[birth_idx].entrance_time
        death_time = cols[death_idx].entrance_time
        # Don't add 0 persistence points?
        if birth_time == death_time:
            continue
        dimension = cols[birth_idx].dimension()
        # Only computing in dimension 1
        if dimension != 1:
            continue
        dgm.append([birth_time, death_time])

    return dgm


def add_unpaired(dgm, pairs, cols):
    all_paired_idxs = [idx for pair in pairs for idx in pair]
    dim_1_idxs = [idx for idx, col in enumerate(cols) if col.dimension() == 1]
    unpaired_idxs = [idx for idx in dim_1_idxs if idx not in all_paired_idxs]
    for idx in unpaired_idxs:
        birth_time = cols[idx].entrance_time
        dgm.append([birth_time, np.inf])
    return dgm
