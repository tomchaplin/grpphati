import numpy as np


# Returns the time at which a directed cone appears (a node pointing to all nodes / from all nodes)
def cone_time(filtration, grounded: bool):
    nodes = [node for node, _node_t in filtration.node_iter()]
    trunc_time = np.inf
    edge_dict = filtration.edge_dict()
    # Compute outgoing cone
    for source, distances in edge_dict.items():
        # Check if source has a path to every other node
        if all(node in distances.keys() for node in nodes if node != source):
            # Then we can truncate at max time
            proposed_time = max(t for t in distances.values())
            trunc_time = min(trunc_time, proposed_time)
    # Computing incoming cone
    for node in nodes:
        sources = [
            source_node
            for source_node, distances in edge_dict.items()
            if node in distances.keys()
        ]
        # Check if there is a path from all other_nodes to node
        if all(other_node in sources for other_node in nodes if other_node != node):
            # Then we can truncate at max time
            proposed_time = max(
                distances[node] for distances in edge_dict.values() if node in distances
            )
            trunc_time = min(trunc_time, proposed_time)
    if grounded:
        # Need to wait for all underlying edges to appear if grounded
        max_edge_time = max(t for _edge, t in filtration.edge_iter())
        return max(max_edge_time, trunc_time)
    else:
        return trunc_time
