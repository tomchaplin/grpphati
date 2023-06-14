import numpy as np
from grpphati.filtrations import ShortestPathFiltration, TruncatedFiltration
from grpphati.homologies import (
    DirectedFlagComplexHomology,
    RegularPathHomology,
    Homology,
)
from grpphati.optimisations import (
    all_optimisations,
    component_appendage_empty,
    component_empty,
)
from grpphati.backends import Backend, LoPHATBackend
from grpphati.truncations import cone_time
from typing import Type


def make_grounded_pipeline(
    filtration_map,
    homology_cls: Type[Homology],
    backend: Backend = LoPHATBackend(),
    optimisation_strat=None,
    truncation_strat=None,
):
    pipeline = lambda G: compute_grounded_ph(
        G, filtration_map, homology_cls, backend, truncation_strat
    )

    if optimisation_strat is None:
        return pipeline
    else:
        return optimisation_strat(pipeline)


def compute_grounded_ph(
    G, filtration_map, homology: Type[Homology], backend: Backend, truncation_strat
):
    # Get filtration
    filtration = filtration_map(G)
    # Truncate the filtration if we can
    if truncation_strat is not None:
        t_time = truncation_strat(filtration, grounded=True)
        if t_time != np.inf:
            filtration = TruncatedFiltration(filtration, t_time)
    # Ground the filtration
    grounded_filtration = filtration.ground(G)
    # Build boundary matrix
    cols = homology.get_cells([0, 1], grounded_filtration) + homology.get_cells(
        [2], filtration
    )
    return backend.compute_ph(cols)


GrPPH = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    optimisation_strat=component_appendage_empty,
    truncation_strat=cone_time,
)
GrPPH_par_wedge = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    optimisation_strat=all_optimisations,
    truncation_strat=cone_time,
)
GrPdFlH = make_grounded_pipeline(
    ShortestPathFiltration,
    DirectedFlagComplexHomology,
    optimisation_strat=component_empty,
)
