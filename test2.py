import networkx as nx
from grounded_phat.pipelines import GrPPH, GrPdFlH

flag_path = "/home/tom/phd/ox/code/ZeroBirthPH/lib/flagser/flagser"

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

print(GrPPH(G1, verbose=True))
print(GrPdFlH(G1, verbose=True))
print(" ")

print("--> G2")
G2 = nx.DiGraph()
for i in range(N):
    G2.add_node(i)
for i in range(0, N - 1):
    G2.add_edge(i, i + 1, weight=0.5)
G2.add_edge(0, N - 1, weight=0.5)

print(GrPPH(G2, verbose=True))
print(GrPdFlH(G2, verbose=True))
print(" ")

print("--> G3")
G3 = nx.complete_graph(100, create_using=nx.DiGraph)
print(len(GrPPH(G3, verbose=True)))
print(len(GrPdFlH(G3, verbose=True)))
print(" ")
