import networkx as nx


def wedge_vertex_0(G_1, G_2):
    G_1_relabel = nx.relabel_nodes(G_1, lambda x: (x, 1) if x > 0 else x)
    G_2_relabel = nx.relabel_nodes(G_2, lambda x: (x, 2) if x > 0 else x)
    return nx.compose(G_1_relabel, G_2_relabel)


def grounded_unique_rep(barcode):
    return sorted([bar[1] for bar in barcode])


def grounded_barcodes_equal(barcode1, barcode2, tolerance=None):
    if tolerance == None:
        return grounded_unique_rep(barcode1) == grounded_unique_rep(barcode2)
    else:
        return all(
            abs(item1 - item2) < tolerance
            for (item1, item2) in zip(
                grounded_unique_rep(barcode1), grounded_unique_rep(barcode2)
            )
        )
