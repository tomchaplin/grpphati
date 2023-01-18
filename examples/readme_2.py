import sys
import os

sys.path.append(os.getcwd())

import networkx as nx
import time
from grpphati.pipelines.grounded import (
    GrPPH,
    GrPPH_par_wedge,
)


def timed(f):
    tic = time.time()
    output = f()
    toc = time.time()
    elapsed = toc - tic
    return (output, elapsed)


N = 50
G_1 = nx.relabel_nodes(
    nx.complete_graph(N, create_using=nx.DiGraph), lambda x: (x, 1) if x > 0 else x
)
G_2 = nx.relabel_nodes(
    nx.complete_graph(N, create_using=nx.DiGraph), lambda x: (x, 2) if x > 0 else x
)
G_wedge = nx.compose(G_1, G_2)
print(f"{G_wedge.number_of_nodes()} nodes in wedge graph")

(out, elap) = timed(lambda: GrPPH(G_wedge))
print("Serial:")
print(f"Size of barcode = {len(out.barcode)}")
print(f"Time elapsed = {elap}s")

print("Parallel over wedges:")
(out, elap) = timed(lambda: GrPPH_par_wedge(G_wedge))
print(f"Size of barcode = {len(out.barcode)}")
print(f"Time elapsed = {elap}s")
