import networkx as nx


def without_appendages(G):
    smaller_G = G
    while True:
        internal_nodes = [node for node, degree in smaller_G.degree if degree > 1]
        if len(internal_nodes) == smaller_G.number_of_nodes():
            break
        # We take subview of G to avoid nested restricted_views
        smaller_G = G.subgraph(internal_nodes)
    return smaller_G


# TODO: Find wedge in parallel? Is there a more efficient algorithm?
# Assumes G is weakly connected
# Returns appendage-thinned wedge components
def wedge_components(G, starting=None):
    starting_subgraph = G if starting is None else G.subgraph(starting)
    # Remove appendages
    subgraph = without_appendages(starting_subgraph)
    # Check for null graph
    if subgraph.number_of_edges() == 0:
        return []
    for node in subgraph.nodes:
        without_node = nx.restricted_view(subgraph, [node], [])
        # Have to check without_node is note a null graph
        # For example without_node might be a double edge graph
        is_wedge = (without_node.number_of_edges() != 0) and not nx.is_weakly_connected(
            without_node
        )
        if is_wedge:
            wedge_comps = [
                comp | {node} for comp in nx.weakly_connected_components(without_node)
            ]
            # We iterated on wedge components found at this vertex
            # We pass on G to avoid nested subviews
            return (
                subcomp
                for comp in wedge_comps
                for subcomp in wedge_components(G, starting=comp)
            )
    # No wedge found, so the only wedge component is all of the nodes
    # We have to return as an iterator with one list
    return [starting]
