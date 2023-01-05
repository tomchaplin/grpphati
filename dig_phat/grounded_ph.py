import networkx as nx
from enum import Enum
import numpy as np
from dig_phat.filtrations import shortest_path_filtration
from dig_phat.homology import Homology
import phat
import time
from pprint import pprint

ColType = Enum('ColType', ['NODE', 'EDGE', 'DOUBLE_EDGE', 'EYEGLASSES', 'DIRECTED_TRIANGLE', 'LONG_SQUARE'])

class Column:
    def __init__(self, col_type, data, entrance_time=None):
        self.col_type = col_type
        self.data = data
        self.entrance_time = entrance_time

    def __repr__(self):
        return f"{self.col_type.name}{self.data.__repr__()} at {self.entrance_time}"

    # Entrance time is just some data we attach to the column
    # We want to be able to hash by the basis element alone
    def __eq__(self, other):
        return (self.col_type, self.data) == (other.col_type, other.data)

    def __hash__(self):
        return hash((self.col_type, self.data))

    def dimension(self):
        if self.col_type == ColType.NODE:
            return 0
        elif self.col_type == ColType.EDGE:
            return 1
        else:
            return 2
    
    def sparse_boundary(self, col2idx_map):
        return (self.dimension(), Column._sparsify(self.boundary(), col2idx_map))

    def _sparsify(bdry, col2idx_map):
        sparse_bdry = []
        for col in bdry:
            idx = col2idx_map[col]
            sparse_bdry.append(idx)
        return sorted(sparse_bdry)

    def boundary(self):
        if self.col_type == ColType.NODE:
            return []
        if self.col_type == ColType.EDGE:
            return [Column.NODE(self.data[0]), Column.NODE(self.data[1])]
        if self.col_type == ColType.DOUBLE_EDGE:
            return [Column.EDGE((self.data)), Column.EDGE(tuple(reversed(self.data)))]
        if self.col_type == ColType.EYEGLASSES:
            # TODO: Implement
            raise Exception
        if self.col_type == ColType.DIRECTED_TRIANGLE:
            return [Column.EDGE((self.data[0], self.data[1])),
                    Column.EDGE((self.data[1], self.data[2])),
                    Column.EDGE((self.data[0], self.data[2]))]
        if self.col_type == ColType.LONG_SQUARE:
            return [Column.EDGE((self.data[0], self.data[1])),
                    Column.EDGE((self.data[1], self.data[3])),
                    Column.EDGE((self.data[0], self.data[2])),
                    Column.EDGE((self.data[2], self.data[3]))]


def _add_column_type_method(cls, col_type):
    def setter(data, entrance_time=None):
        return cls(col_type, data, entrance_time)
    setattr(cls, col_type.name, setter)

for c in ColType:
    _add_column_type_method(Column, c)

def _add_paired(pairs, cols):
    dgm = []

    for [birth_idx, death_idx] in pairs:
        birth_time = cols[birth_idx].entrance_time
        death_time = cols[death_idx].entrance_time
        # Don't add 0 persistence points?
        if birth_time == death_time:
            continue
        dimension = cols[birth_idx].dimension()
        # Only computing in dimension 1
        if dimension != 1:
            continue
        dgm.append([birth_time, death_time])

    return dgm

def _add_unpaired(dgm, pairs, cols):
    all_paired_idxs = [idx for pair in pairs for idx in pair]
    dim_1_idxs = [idx for idx, col in enumerate(cols) if col.dimension() == 1]
    unpaired_idxs = [idx for idx in dim_1_idxs if idx not in all_paired_idxs]
    for idx in unpaired_idxs:
        birth_time = cols[idx].entrance_time
        dgm.append([birth_time, np.inf])
    return dgm

def _non_trivial_dict(sp_iter):
    return {
        source: {
            target: distance
            for target, distance in distances.items()
            if target != source
        }
        for source, distances in sp_iter
    }

def _sorted_two_paths(G):
    sp_lengths = _non_trivial_dict(nx.all_pairs_dijkstra_path_length(G));
    paths = [
            ((source, midpoint, target) , max(first_hop_dist, second_hop_dist))
            for source, distances in sp_lengths.items()
            for midpoint, first_hop_dist in distances.items()
            for target, second_hop_dist in sp_lengths[midpoint].items()
            ]
    paths.sort(key=lambda tup: tup[1])
    return paths

def _split_off_bridges(filtration, paths):
    cols = []
    bridges = {}
    for path, entrance_time in paths:
        if path[0] == path[2]:
            cols.append(Column.DOUBLE_EDGE((path[0], path[1]), entrance_time))
        elif filtration((path[0], path[2])) <= entrance_time:
            cols.append(Column.DIRECTED_TRIANGLE((path[0], path[1], path[2]), entrance_time))
        else:
            try:
                bridges[(path[0], path[2])].append((path[1], entrance_time))
            except KeyError:
                bridges[(path[0], path[2])] = [(path[1], entrance_time)]
    return (cols, bridges)

def _add_ls_collapsing_directed_triangles(cols, bridges, filtration):
    for endpoints, sub_bridges in bridges.items():
        collapse_time = filtration(endpoints)
        # We add a directed triangle to collapse the first bridge to the shortcut between endpoints
        new_triangle = (endpoints[0], sub_bridges[0][0], endpoints[1])
        cols.append(Column.DIRECTED_TRIANGLE((new_triangle), collapse_time))
    return cols

def _add_long_squares(cols, bridges):
    for endpoints, sub_bridges in bridges.items():
        if len(sub_bridges) <= 1:
            continue
        first_bridge_node = sub_bridges[0][0]
        for bridge_idx in range(1, len(sub_bridges)):
            second_bridge_node = sub_bridges[bridge_idx][0]
            entrance_time = sub_bridges[bridge_idx][1]
            cols.append(Column.LONG_SQUARE(
                (endpoints[0], first_bridge_node, second_bridge_node, endpoints[1]),
                entrance_time
            ))
    return cols

def _add_nodes(G, cols):
    for node in G.nodes:
        cols.append(Column.NODE(node, 0))
    return cols

def _add_underlying_edges(G, cols):
    for edge in G.edges:
        cols.append(Column.EDGE(edge, 0))
    return cols

def _add_filtration_edges(G, filtration, cols):
    sp_lengths = _non_trivial_dict(nx.all_pairs_dijkstra_path_length(G));
    for source, distances in sp_lengths.items():
        for target, dist in distances.items():
            if G.has_edge(source, target):
                continue
            cols.append(Column.EDGE((source, target), dist))
    return cols

def _build_columns(G, filtration):
    cols = _add_nodes(G, [])
    cols = _add_underlying_edges(G, cols)
    cols = _add_filtration_edges(G, filtration, cols)
    two_paths = list(_sorted_two_paths(G))
    (new_cols, bridges) = _split_off_bridges(filtration, two_paths)
    cols.extend(new_cols)
    cols = _add_ls_collapsing_directed_triangles(cols, bridges, filtration)
    cols = _add_long_squares(cols, bridges)
    return cols

def _convert_to_sparse(cols):
    sparse_cols = []
    col2idx_map = {}
    for col in cols:
        sparse_bdry = col.sparse_boundary(col2idx_map)
        insertion_idx = len(sparse_cols)
        sparse_cols.append(sparse_bdry)
        col2idx_map[col] = insertion_idx
    return sparse_cols

# TODO: Change filtration interface so that it will return a map of filtered edges
# FOR NOW ASSUMES REG_PATH
def grounded_ph(G, filtration, homology, verbose=True):
    ## Build boundary matrix
    if verbose:
      print("Building boundary matrix")
      tic = time.time()
    
    # Build up the basis that we will filter by
    cols = _build_columns(G, filtration)
    # Sort according to entrance time and dimension
    cols.sort(key=lambda col: (col.entrance_time, col.dimension()))
    # Convert to sparse format for PHAT
    sparse_cols = _convert_to_sparse(cols)

    ## Compute persistence pairs
    if verbose:
      print(f"Basis of size {len(cols)}")
      print("Computing PH")

    boundary_matrix = phat.boundary_matrix(
        columns=sparse_cols,
        representation=phat.representations.sparse_pivot_column
    )
    
    pairs = boundary_matrix.compute_persistence_pairs(reduction=phat.reductions.chunk_reduction)
    pairs.sort()

    ## Add finite points to persistence diagram, recovering times
    dgm = _add_paired(pairs, cols)

    ## TODO: Add unpaired edges
    dgm = _add_unpaired(dgm, pairs, cols)
    
    if verbose:
        print(
            "Computation took %.3g seconds"
            % (time.time() - tic)
        )
    
    return dgm

def grpph(G, verbose=True):
    return grounded_ph(G, shortest_path_filtration(G), Homology.REG_PATH, verbose)
