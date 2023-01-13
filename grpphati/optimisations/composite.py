from .components import parallel_over_components
from .check_empty import check_empty
from .wedge import parallel_over_wedges
from .appendages import remove_appendages


def all_optimisations(pipeline):
    return parallel_over_components(parallel_over_wedges(check_empty(pipeline)))


def all_optimisations_serial(pipeline):
    return parallel_over_components(
        parallel_over_wedges(check_empty(pipeline), n_jobs=1), n_jobs=1
    )


def component_appendage_empty(pipeline):
    return parallel_over_components(remove_appendages(check_empty(pipeline)))


def component_appendage_empty_serial(pipeline):
    return parallel_over_components(remove_appendages(check_empty(pipeline)), n_jobs=1)


def component_empty(pipeline):
    return parallel_over_components(check_empty(pipeline))


def component_empty_serial(pipeline):
    return parallel_over_components(check_empty(pipeline), n_jobs=1)
