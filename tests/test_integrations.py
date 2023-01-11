import networkx as nx
import numpy as np
from grpphati.pipelines.grounded import (
    GrPPH,
    GrPdFlH,
)
from .utils import grounded_barcodes_equal


def _double_edge_graph(edge_weight):
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 0)], weight=edge_weight)
    return G


def test_double_edge_GrPPH():
    G = _double_edge_graph(3)
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 3]])


def test_double_edge_GrPdFlH():
    G = _double_edge_graph(3)
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, np.inf]])


def _appendage_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (1, 0), (0, 2)])
    return G


def test_appendage_graph_GrPPH():
    G = _appendage_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 1]])


def test_appendage_graph_GrPdFlH():
    G = _appendage_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 2]])


def _balanced_triangle_graph():
    G = nx.DiGraph()
    G.add_edges_from(
        [(0, 1, {"weight": 2}), (1, 2, {"weight": 2}), (0, 2, {"weight": 3})]
    )
    return G


def test_balanced_triangle_GrPPH():
    G = _balanced_triangle_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 3]])


def test_balanced_triangle_GrPdFlH():
    G = _balanced_triangle_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 3]])


def _lobsided_triangle_graph():
    G = nx.DiGraph()
    G.add_edges_from(
        [(0, 1, {"weight": 5}), (1, 2, {"weight": 5}), (0, 2, {"weight": 2})]
    )
    return G


def test_lobsided_triangle_GrPPH():
    G = _lobsided_triangle_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 5]])


def test_lobsided_triangle_GrPdFlH():
    G = _lobsided_triangle_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 5]])


def _balanced_ls_graph():
    G = nx.DiGraph()
    G.add_edges_from(
        [
            (0, 1, {"weight": 2}),
            (1, 3, {"weight": 2}),
            (0, 2, {"weight": 1.5}),
            (2, 3, {"weight": 1.5}),
        ]
    )
    return G


def test_balanced_ls_GrPPH():
    G = _balanced_ls_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 2]])


def test_balanced_ls_GrPdFlH():
    G = _balanced_ls_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 3]])


def _diverging_square_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (0, 2), (3, 1), (3, 2)])
    return G


def test_diverging_square_GrPPH():
    G = _diverging_square_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, np.inf]])


def test_diverging_square_GrPdFlH():
    G = _diverging_square_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, np.inf]])


def _diverging_square_with_sink_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (0, 2), (3, 1), (3, 2), (1, 4), (2, 4)])
    return G


def test_diverging_square_with_sink_GrPPH():
    G = _diverging_square_with_sink_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 1], [0, 1]])


def test_diverging_square_with_sink_GrPdFlH():
    G = _diverging_square_with_sink_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 2], [0, 2]])


def _diverging_square_with_source_graph():
    G = nx.DiGraph()
    G.add_edges_from([(0, 1), (0, 2), (3, 1), (3, 2), (4, 1), (4, 2)])
    return G


def test_diverging_square_with_source_GrPPH():
    G = _diverging_square_with_source_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, np.inf], [0, np.inf]])


def test_diverging_square_with_source_GrPdFlH():
    G = _diverging_square_with_source_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, np.inf], [0, np.inf]])


# Second graph in Figure 13
def _collapsed_graph(W):
    G = nx.DiGraph()
    G.add_edges_from(
        [
            (0, 1, {"weight": 1.5}),
            (1, 2, {"weight": 1}),
            (2, 0, {"weight": 1.5}),
            (0, 3, {"weight": 1.5}),
            (3, 4, {"weight": 1}),
            (4, 0, {"weight": 1.5}),
            (2, 3, {"weight": W}),
        ]
    )
    return G


def test_collapsed_GrPPH():
    G = _collapsed_graph(17.42)
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 2.5], [0, 2.5], [0, 3]])


# In this graph the shortuct 0->3 will appear before the edges 0->2, 2->3
# Tests collapsing long square generators
def _collapsing_ls_graph():
    G = nx.DiGraph()
    G.add_edges_from(
        [
            (0, 1, {"weight": 0.5}),
            (1, 3, {"weight": 0.2}),
            (0, 2, {"weight": 13}),
            (2, 3, {"weight": 12}),
        ]
    )
    return G


def test_collapsing_ls_GrPPH():
    G = _collapsing_ls_graph()
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 13]])


def test_collapsing_ls_GrPdFlH():
    G = _collapsing_ls_graph()
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(barcode, [[0, 13]])
