import sys
import os

sys.path.append(os.getcwd())

from grpphati.pipelines.grounded import GrPPH, GrPdFlH
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)], weight=3)
grpph_bar = GrPPH(G).barcode
grpdflh_bar = GrPdFlH(G).barcode

print(grpph_bar)
print(grpdflh_bar)
