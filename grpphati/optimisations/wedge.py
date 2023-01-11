import networkx as nx
from joblib import Parallel, delayed
from grpphati.utils.graph import wedge_components
from grpphati.results import Result


def parallel_over_wedges(pipeline, prefer=None, n_jobs=-1):
    def new_pipeline(G):
        def run_pipeline_on_component(component):
            subgraph = G.subgraph(component)
            return pipeline(subgraph)

        comps = list(wedge_components(G))
        if len(comps) > 1:
            sub_results = Parallel(n_jobs=n_jobs, prefer=prefer)(
                delayed(run_pipeline_on_component)(component) for component in comps
            )
            return Result.merge(*sub_results)
        elif len(comps) == 0:
            return Result.empty()
        else:
            return run_pipeline_on_component(comps[0])

    return new_pipeline
