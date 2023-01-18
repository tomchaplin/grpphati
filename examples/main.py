import sys
import os

sys.path.append(os.getcwd())

import networkx as nx
import time
from grpphati.pipelines.grounded import (
    GrPPH,
    GrPPH_par_wedge,
    GrPdFlH,
    make_grounded_pipeline,
)
from grpphati.pipelines.standard import PPH, PdFlH
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration


GrPPH_slow = make_grounded_pipeline(ShortestPathFiltration, RegularPathHomology)


def timed(f):
    tic = time.time()
    output = f()
    toc = time.time()
    elapsed = f"{toc - tic}s"
    return (output, elapsed)


print("--> G1")
N = 10
G1 = nx.DiGraph()
for i in range(N):
    G1.add_node(i)
for i in range(N):
    G1.add_edge(i, (i + 1) % N, weight=2.9)

G1.add_node(N)
G1.add_node(N + 1)
G1.add_node(N + 2)
G1.add_node(N + 3)
G1.add_edge(N, N + 1)
G1.add_edge(N, N + 2)
G1.add_edge(N + 3, N + 1)
G1.add_edge(N + 3, N + 2)

print(GrPPH(G1).barcode)
print(GrPdFlH(G1).barcode)
print(PPH(G1).barcode)
print(PdFlH(G1).barcode)
print(" ")

print("--> G2")
G2 = nx.DiGraph()
for i in range(N):
    G2.add_node(i)
for i in range(0, N - 1):
    G2.add_edge(i, i + 1, weight=0.5)
G2.add_edge(0, N - 1, weight=0.5)

print(GrPPH(G2).barcode)
print(GrPdFlH(G2).barcode)
print(" ")

print("--> G3")
G3_1 = nx.complete_graph(100, create_using=nx.DiGraph)
G3_2 = nx.complete_graph(100, create_using=nx.DiGraph)
G3 = nx.disjoint_union(G3_1, G3_2)
(out, elap) = timed(lambda: GrPPH(G3))
print(len(out.barcode))
print(elap)
(out, elap) = timed(lambda: GrPPH_slow(G3))
print(len(out.barcode))
print(elap)
print(" ")

print("--> G4")
G4 = nx.DiGraph()
for i in range(1000):
    G4.add_node(i)
for i in range(0, 1000 - 1):
    G4.add_edge(i, i + 1, weight=i)
(out, elap) = timed(lambda: GrPPH(G4))
print(len(out.barcode))
print(elap)
(out, elap) = timed(lambda: GrPPH_par_wedge(G4))
print(len(out.barcode))
print(elap)
print(" ")

print("--> G5")
G5 = nx.DiGraph()
for i in range(7):
    G5.add_node(i)
G5.add_edge(0, 1)
G5.add_edge(1, 2)
G5.add_edge(2, 3)
G5.add_edge(3, 0)
G5.add_edge(2, 4)
G5.add_edge(2, 5)
G5.add_edge(4, 6)
G5.add_edge(5, 6)
(out, elap) = timed(lambda: GrPPH(G5))
print(out.barcode)
print(elap)
(out, elap) = timed(lambda: GrPPH_par_wedge(G5))
print(out.barcode)
print(elap)
(out, elap) = timed(lambda: GrPPH_slow(G5))
print(out.barcode)
print(elap)
print(" ")

print("--> G6")
G6_1 = nx.relabel_nodes(
    nx.complete_graph(100, create_using=nx.DiGraph), lambda x: (x, 1) if x > 0 else x
)
G6_2 = nx.relabel_nodes(
    nx.complete_graph(100, create_using=nx.DiGraph), lambda x: (x, 2) if x > 0 else x
)
G6 = nx.compose(G6_1, G6_2)
print(G6.number_of_nodes())
(out, elap) = timed(lambda: GrPPH(G6))
print(len(out.barcode))
print(elap)
(out, elap) = timed(lambda: GrPPH_par_wedge(G6))
print(len(out.barcode))
print(elap)
