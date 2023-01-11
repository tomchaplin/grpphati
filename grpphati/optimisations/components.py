import networkx as nx
from joblib import Parallel, delayed
from grpphati.results import Result


def parallel_over_components(pipeline, prefer=None, n_jobs=-1):
    def new_pipeline(G):
        def run_pipeline_on_component(component):
            subgraph = G.subgraph(component)
            return pipeline(subgraph)

        weak_components = list(nx.weakly_connected_components(G))
        if len(weak_components) > 1:
            sub_results = Parallel(n_jobs=n_jobs, prefer=prefer)(
                delayed(run_pipeline_on_component)(component)
                for component in weak_components
            )
            return Result.merge(*sub_results)
        elif len(weak_components) == 0:
            return Result.empty()
        else:
            return run_pipeline_on_component(weak_components[0])

    return new_pipeline
