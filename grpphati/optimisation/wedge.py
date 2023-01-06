import networkx as nx
from joblib import Parallel, delayed
from grpphati.util.graph import wedge_components


def parallel_over_wedges(pipeline, prefer=None, n_jobs=-1):
    def new_pipeline(G):
        def run_pipeline_on_component(component):
            subgraph = G.subgraph(component)
            return pipeline(subgraph)

        comps = list(wedge_components(G))
        if len(comps) > 1:
            sub_dgms = Parallel(n_jobs=n_jobs, prefer=prefer)(
                delayed(run_pipeline_on_component)(component) for component in comps
            )
            return [bar for dgm in sub_dgms for bar in dgm]
        elif len(comps) == 0:
            return []
        else:
            return run_pipeline_on_component(comps[1])

    return new_pipeline
