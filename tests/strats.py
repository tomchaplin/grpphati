from hypothesis_networkx import graph_builder
from hypothesis import event, strategies as st
import networkx as nx

valid_edge_weight = st.floats(
    allow_nan=False,
    min_value=1e-30,
    max_value=1e15,
    allow_infinity=False,
)

_node_data = st.fixed_dictionaries({"number": st.integers()})
_edge_data = st.fixed_dictionaries({"weight": valid_edge_weight})

builder = graph_builder(
    graph_type=nx.DiGraph,
    node_keys=None,
    node_data=_node_data,
    edge_data=_edge_data,
    min_nodes=2,
    max_nodes=30,
    min_edges=1,
    max_edges=None,
    self_loops=False,
    connected=True,
)


def report_graph_size(test):
    def new_test(**args):
        for val in args.values():
            if not isinstance(val, nx.DiGraph):
                continue
            event(f"Graph size {(val.number_of_nodes(), val.number_of_edges())}")
        test(**args)

    return new_test
