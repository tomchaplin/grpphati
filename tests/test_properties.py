from grpphati.homologies.directed_flag import DirectedFlagComplexHomology
from .strats import builder, report_graph_size, valid_edge_weight
from .utils import grounded_barcodes_equal, wedge_vertex_0
from hypothesis import given, settings, event, strategies as st
from grpphati.pipelines.grounded import (
    GrPPH,
    GrPPH_par_wedge,
    GrPdFlH,
    make_grounded_pipeline,
)
from grpphati.homologies import RegularPathHomology, DirectedFlagComplexHomology
from grpphati.filtrations import ShortestPathFiltration
import networkx as nx
import numpy as np


unoptimised_GrPPH = make_grounded_pipeline(
    ShortestPathFiltration, RegularPathHomology, optimisation_strat=None
)

unoptimised_GrPdFlH = make_grounded_pipeline(
    ShortestPathFiltration, DirectedFlagComplexHomology, optimisation_strat=None
)


@given(G=builder)
@settings(deadline=None)
@report_graph_size
def test_births_are_zero(G):
    barcode = GrPPH(G).barcode
    assert all(bar[0] == 0 for bar in barcode)


@given(G=builder)
@settings(deadline=None)
@report_graph_size
def test_par_wedge_agrees(G):
    barcode1 = GrPPH(G).barcode
    barcode2 = GrPPH_par_wedge(G).barcode
    assert grounded_barcodes_equal(barcode1, barcode2)


@given(G=builder)
@settings(deadline=None)
@report_graph_size
def test_grpph_simple_optimisations(G):
    barcode1 = GrPPH(G).barcode
    barcode2 = unoptimised_GrPPH(G).barcode
    assert grounded_barcodes_equal(barcode1, barcode2)


# Note: We don't use par_wedge because otherwise this test is true by definition
@given(G_1=builder, G_2=builder)
@settings(deadline=None)
@report_graph_size
def test_wedges_decompose(G_1, G_2):
    barcode_1 = GrPPH(G_1).barcode + GrPPH(G_2).barcode
    barcode_2 = GrPPH(wedge_vertex_0(G_1, G_2)).barcode
    assert grounded_barcodes_equal(barcode_1, barcode_2)


# Note: We use unoptimised because otherwise this test is true by definition
@given(G_1=builder, G_2=builder)
@settings(deadline=None)
@report_graph_size
def test_unions_decompose_GrPPH(G_1, G_2):
    barcode_1 = unoptimised_GrPPH(G_1).barcode + unoptimised_GrPPH(G_2).barcode
    barcode_2 = unoptimised_GrPPH(nx.disjoint_union(G_1, G_2)).barcode
    assert grounded_barcodes_equal(barcode_1, barcode_2)


# Note: We use unoptimised because otherwise this test is true by definition
@given(G_1=builder, G_2=builder)
@settings(deadline=None)
@report_graph_size
def test_unions_decompose_GrPdFlH(G_1, G_2):
    barcode_1 = unoptimised_GrPdFlH(G_1).barcode + unoptimised_GrPdFlH(G_2).barcode
    barcode_2 = unoptimised_GrPdFlH(nx.disjoint_union(G_1, G_2)).barcode
    assert grounded_barcodes_equal(barcode_1, barcode_2)


@given(G=builder)
@settings(deadline=None)
@report_graph_size
def test_num_features_GrPPH(G):
    expected_count = G.number_of_edges() - G.number_of_nodes() + 1
    barcode = GrPPH(G).barcode
    assert len(barcode) == expected_count


@given(G=builder)
@settings(deadline=None)
@report_graph_size
def test_num_features_GrPdFlH(G):
    expected_count = G.number_of_edges() - G.number_of_nodes() + 1
    barcode = GrPdFlH(G).barcode
    assert len(barcode) == expected_count


@settings(deadline=None)
@given(n=st.integers(min_value=1, max_value=10))
def test_complete_graph_GrPPH(n):
    expected_count = n * (n - 1) - n + 1
    expected_barcode = [[0, 1] for _ in range(expected_count)]
    G = nx.complete_graph(n, create_using=nx.DiGraph)
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(expected_barcode, barcode)


@settings(deadline=None)
@given(n=st.integers(min_value=1, max_value=10))
def test_complete_graph_GrPdFlH(n):
    expected_count = n * (n - 1) - n + 1
    expected_barcode = (
        [[0, 1] for _ in range(expected_count)] if n != 2 else [[0, np.inf]]
    )
    G = nx.complete_graph(n, create_using=nx.DiGraph)
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(expected_barcode, barcode)


@settings(deadline=None)
@given(n=st.integers(min_value=2, max_value=20), weight=valid_edge_weight)
def test_cycle_graph_GrPPH(n, weight):
    is_even = n % 2 == 0
    event_msg = "Even" if is_even else "Odd"
    event(event_msg)
    expected_death = (n / 2) * weight if is_even else (n + 1) / 2 * weight
    G = nx.DiGraph()
    G.add_edges_from([(i, (i + 1) % n, {"weight": weight}) for i in range(n)])
    barcode = GrPPH(G).barcode
    assert grounded_barcodes_equal(
        barcode, [[0, expected_death]], tolerance=weight / 1e9
    )


# Have to exclude n=2 because double edge never dies
@settings(deadline=None)
@given(n=st.integers(min_value=3, max_value=20), weight=valid_edge_weight)
def test_cycle_graph_GrPdFlH(n, weight):
    is_even = n % 2 == 0
    event_msg = "Even" if is_even else "Odd"
    event(event_msg)
    expected_death = ((n / 2) + 1) * weight if is_even else (n + 1) / 2 * weight
    G = nx.DiGraph()
    G.add_edges_from([(i, (i + 1) % n, {"weight": weight}) for i in range(n)])
    barcode = GrPdFlH(G).barcode
    assert grounded_barcodes_equal(
        barcode, [[0, expected_death]], tolerance=weight / 1000
    )


@settings(deadline=None)
@given(
    lengths=st.lists(
        st.tuples(valid_edge_weight, valid_edge_weight), min_size=2, max_size=20
    )
)
def test_multiple_paths_GrPPH(lengths):
    event(f"n_paths = {len(lengths)}")
    G = nx.DiGraph()
    G.add_node("start")
    G.add_node("end")
    for (idx, (length_1, length_2)) in enumerate(lengths):
        G.add_edge("start", idx, weight=length_1)
        G.add_edge(idx, "end", weight=length_2)
    barcode = GrPPH(G).barcode
    alphas = sorted([max(l_pair) for l_pair in lengths])
    alphas.pop(0)
    expected_barcode = [[0, alpha] for alpha in alphas]
    assert grounded_barcodes_equal(expected_barcode, barcode)


@given(
    lengths=st.lists(
        st.tuples(valid_edge_weight, valid_edge_weight), min_size=2, max_size=20
    )
)
def test_multiple_paths_GrPdFlH(lengths):
    event(f"n_paths = {len(lengths)}")
    G = nx.DiGraph()
    G.add_node("start")
    G.add_node("end")
    for (idx, (length_1, length_2)) in enumerate(lengths):
        G.add_edge("start", idx, weight=length_1)
        G.add_edge(idx, "end", weight=length_2)
    barcode = GrPdFlH(G).barcode
    # Same expected barcode as GrPPH but we need to wait until
    # there is some path start->end before any directed triangles appear
    alphas = sorted([max(l_pair) for l_pair in lengths])
    shortest_path = sorted([sum(l_pair) for l_pair in lengths]).pop(0)
    alphas.pop(0)
    expected_barcode = [[0, max(shortest_path, alpha)] for alpha in alphas]
    assert grounded_barcodes_equal(expected_barcode, barcode)
