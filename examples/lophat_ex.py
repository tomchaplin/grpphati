import sys
import os

sys.path.append(os.getcwd())

import networkx as nx
from grpphati.pipelines.grounded import make_grounded_pipeline
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration
from grpphati.backends import LoPHATBackend
from grpphati.optimisations import all_optimisations
from pprint import pprint


pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=LoPHATBackend(num_threads=4, min_chunk_len=10),
    optimisation_strat=all_optimisations,
)

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3, {"weight": 10})]
)
result = pipe(G)
print(result.barcode)
