import networkx as nx
from grpphati.pipelines.grounded import make_grounded_pipeline
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration
from grpphati.backends import EireneBackend
from grpphati.optimisations import all_optimisations_serial
from pprint import pprint

pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=EireneBackend(
        runtime_path="/home/tom/Downloads/julia/julia-1.6.6/bin/julia"
    ),
    optimisation_strat=all_optimisations_serial,
)

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3, {"weight": 10})]
)
result = pipe(G)
print(result.barcode)
pprint(result.reps)
