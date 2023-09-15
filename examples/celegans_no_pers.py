#!/usr/bin/env python
# coding: utf-8

# This script illustrates how you can use a custom GrPPHATI filtration
# to compute betti_1 of regular path homology (no persistence)

# Pull in deps

import pandas as pd
import networkx as nx
import numpy as np

from grpphati.filtrations import Filtration, ProperGroundedFiltration
from grpphati.optimisations import component_appendage_empty, all_optimisations
from grpphati.backends import LoPHATBackend
from grpphati.homologies import RegularPathHomology
from grpphati.pipelines.standard import make_standard_pipeline


# Make a filtration which includes all of G at t=0 and then neve changes
class TrivialFiltration(Filtration):
    def __init__(self, G):
        self.G = G

    def node_time(self, node):
        return 0

    def edge_time(self, edge):
        if self.G.has_edge(*edge):
            return 0
        else:
            return np.inf

    def node_iter(self):
        return [(node, 0) for node in self.G.nodes]

    def edge_iter(self):
        return [(edge, 0) for edge in self.G.edges]

    def edge_dict(self):
        ret_dict = {}
        for i in self.G.nodes:
            ret_dict[i] = {}
        for i, j in self.G.edges:
            ret_dict[i][j] = 0
        return ret_dict

    def ground(self, grounding_G):
        return ProperGroundedFiltration(grounding_G, self)


pipeline = make_standard_pipeline(
    TrivialFiltration,
    RegularPathHomology,
    backend=LoPHATBackend(num_threads=1, with_reps=False),
    optimisation_strat=all_optimisations,
    truncation_strat=None,
)

print("=== CELEGANS ===")

# Read in neurons

# Available here https://www.wormatlas.org/neuronalwiring.html (Section 2.1 in Excel format)
df = pd.read_csv("./NeuronConnect.csv")
print("Loaded data")

# Just look at synapses from the sending side

sending_types = ["S", "Sp", "EJ"]
sending_df = df[df["Type"].isin(sending_types)]

# Aggregate #synapses between each neuron pair

n_connections_df = (
    sending_df.groupby(["Neuron 1", "Neuron 2"])["Nbr"].sum().reset_index()
)


# Weighted digraph with weight = 1/(number of synapses)

G = nx.DiGraph()
G.add_edges_from(
    (row["Neuron 1"], row["Neuron 2"])  # , {"weight": 1.0 / row["Nbr"]})
    for _, row in n_connections_df.iterrows()
)

# grpphati-rs required integer-labelled nodes
G = nx.convert_node_labels_to_integers(G, label_attribute="Neuron")
print("Built digraph")

# Compute path homology
path_homology = pipeline(G)
print("Computed path homology")

assert all(bar == [0, np.inf] for bar in path_homology.barcode)
betti_1 = len(path_homology.barcode)
print(f"β_1 = {betti_1}")

print("\n=== TESTS ===")
# Quick test to check cycle graphs
for N in range(2, 11):
    G2 = nx.DiGraph()
    G2.add_edges_from([(i, (i + 1) % N) for i in range(N)])
    betti_1 = len(pipeline(G2).barcode)
    print(f"{N}-cycle graph: {betti_1}")
    assert betti_1 == (0 if N == 2 else 1)

# Quick test to check long square
G3 = nx.DiGraph()
G3.add_edges_from([(0, 1), (1, 2), (0, 3), (3, 2)])
betti_1 = len(pipeline(G3).barcode)
print(f"Long square: {betti_1}")
assert betti_1 == 0

# Quick test to check twin directed traingles
G3 = nx.DiGraph()
G3.add_edges_from([(0, 1), (1, 2), (0, 3), (3, 2), (0, 2)])
betti_1 = len(pipeline(G3).barcode)
print(f"Split long square: {betti_1}")
assert betti_1 == 0

# Quick test to check the above with the middle edge reversed
G3 = nx.DiGraph()
G3.add_edges_from([(0, 1), (1, 2), (0, 3), (3, 2), (2, 0)])
betti_1 = len(pipeline(G3).barcode)
print(f"Split long square (reversed): {betti_1}")
assert betti_1 == 1
