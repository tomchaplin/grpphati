import sys
import os

sys.path.append(os.getcwd())

import networkx as nx
from grpphati.pipelines.grounded import make_grounded_pipeline, GrPPH
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration
from grpphati.backends import LoPHATBackend
from grpphati.optimisations import all_optimisations
from pprint import pprint


pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=LoPHATBackend(num_threads=4, with_reps=True),
    optimisation_strat=all_optimisations,
)

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3, {"weight": 10})]
)
result = pipe(G)
pprint(result.barcode)
pprint(result.reps)

pipe2 = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=LoPHATBackend(num_threads=4, with_reps=False),
    optimisation_strat=all_optimisations,
)

result2 = pipe2(G)
pprint(result2.barcode)
pprint(result2.reps)
