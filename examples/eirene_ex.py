import networkx as nx
import time
from grpphati.pipelines.grounded import make_grounded_pipeline
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration
from grpphati.backends import EireneBackend, PHATBackend
from grpphati.optimisations import all_optimisations_serial
from pprint import pprint

pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=EireneBackend(
        runtime_path="/home/tom/Downloads/julia/julia-1.6.6/bin/julia",
        sysimage="/home/tom/Documents/dev/tda/grpphati/patched_sys.so",
    ),
    optimisation_strat=all_optimisations_serial,
)

print("Done setting up Eirene")

phat_pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=PHATBackend(),
    optimisation_strat=all_optimisations_serial,
)


def timed(f):
    tic = time.time()
    output = f()
    toc = time.time()
    elapsed = f"{toc - tic}s"
    return (output, elapsed)


G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3, {"weight": 10})]
)
result = pipe(G)
print(result.barcode)
pprint(result.reps)

print("--> G3")
N = 100
G3_1 = nx.complete_graph(N, create_using=nx.DiGraph)
G3_2 = nx.complete_graph(N, create_using=nx.DiGraph)
G3 = nx.disjoint_union(G3_1, G3_2)
# (out, elap) = timed(lambda: pipe(G3))
out = pipe(G3)
print(len(out.barcode))
print(out.reps[0])
# print(elap)
# (out, elap) = timed(lambda: phat_pipe(G3))
out = phat_pipe(G3)
print(len(out.barcode))
# print(elap)
