import networkx as nx
import dig_phat as dp

flag_path= "/home/tom/phd/ox/code/ZeroBirthPH/lib/flagser/flagser"

N = 10
G = nx.DiGraph()
for i in range(N):
    G.add_node(i)
for i in range(N):
    G.add_edge(i, (i+1) % N, weight=2.9)

G.add_node(N)
G.add_node(N+1)
G.add_node(N+2)
G.add_node(N+3)
G.add_edge(N, N+1)
G.add_edge(N, N+2)
G.add_edge(N+3, N+1)
G.add_edge(N+3, N+2)

print(dp.grpph(G))
print(dp.grounded_ph(G, dp.filtrations.ShortestPathFiltration(G), dp.homology.DirectedFlagComplexHomology))

G2 = nx.DiGraph()
for i in range(N):
    G2.add_node(i)
for i in range(0, N-1):
    G2.add_edge(i, i+1, weight=0.5)
G2.add_edge(0, N-1, weight=0.5)

print(dp.grpph(G2))
print(dp.grounded_ph(G2, dp.filtrations.ShortestPathFiltration(G2), dp.homology.DirectedFlagComplexHomology))
