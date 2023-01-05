import numpy as np
import networkx as nx

def shortest_path_filtration(G):
    distances = dict(nx.all_pairs_dijkstra_path_length(G))
    def filtration_time(edge):
        try:
            return distances[edge[0]][edge[1]]
        except KeyError:
            # No path so never enters
            return np.inf

    return filtration_time
