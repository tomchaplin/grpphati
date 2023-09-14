import numpy as np
from grpphati.columns.edge import EdgeCol
from grpphati.columns.node import NodeCol
from grpphati.filtrations.truncated import TruncatedFiltration
from .abstract import Homology
from grpphati.columns import DoubleEdgeCol, DirectedTriangleCol, LongSquareCol


class RegularPathHomology(Homology):
    @classmethod
    def get_two_cells(cls, filtration):
        two_paths = list(_sorted_two_paths(filtration))
        (cols, bridges) = _split_off_bridges(filtration, two_paths)
        cols = _add_ls_collapsing_directed_triangles(cols, bridges, filtration)
        cols = _add_long_squares(cols, bridges)
        return cols

    @classmethod
    def compute_map(cls, domain_cells, codomain_cells, vertex_map=lambda x: x):
        cm = _cell_mapper(codomain_cells, vertex_map)
        return list(map(cm, domain_cells))


def _sorted_two_paths(filtration):
    sp_lengths = filtration.edge_dict()
    paths = [
        ((source, midpoint, target), max(first_hop_dist, second_hop_dist))
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
            cols.append(DoubleEdgeCol((path[0], path[1]), entrance_time))
        elif filtration.edge_time((path[0], path[2])) <= entrance_time:
            # Note entrance_time is finite because it comes from an edge_dict
            cols.append(DirectedTriangleCol((path[0], path[1], path[2]), entrance_time))
        else:
            try:
                bridges[(path[0], path[2])].append((path[1], entrance_time))
            except KeyError:
                bridges[(path[0], path[2])] = [(path[1], entrance_time)]
    return (cols, bridges)


def _add_ls_collapsing_directed_triangles(cols, bridges, filtration):
    for endpoints, sub_bridges in bridges.items():
        collapse_time = filtration.edge_time(endpoints)
        # We add a directed triangle to collapse the first bridge to the shortcut between endpoints
        new_triangle = (endpoints[0], sub_bridges[0][0], endpoints[1])
        if collapse_time < np.inf:
            cols.append(DirectedTriangleCol((new_triangle), collapse_time))
    return cols


def _add_long_squares(cols, bridges):
    for endpoints, sub_bridges in bridges.items():
        if len(sub_bridges) <= 1:
            continue
        first_bridge_node = sub_bridges[0][0]
        for bridge_idx in range(1, len(sub_bridges)):
            second_bridge_node = sub_bridges[bridge_idx][0]
            entrance_time = sub_bridges[bridge_idx][1]
            cols.append(
                LongSquareCol(
                    endpoints[0],
                    (first_bridge_node, second_bridge_node),
                    endpoints[1],
                    entrance_time,
                )
            )
    return cols


def _cell_mapper(codomain_cells, vertex_map):
    # Builds up an index of the codomain cells for quick lookup of image
    # index["nodes"] map from node columns to indexes
    # index["edges"] map from edge columns to indexes
    # index["double_edges"] map from double edge columns to indexes
    # index["two_paths"][(s, t)] = {} for each endpoint pair (s, t)
    # index["two_paths"][(s, t)]["base"] = first midpoint of every long square with endpoints (s, t)
    # index["two_paths"][(s, t)]["nonbase"] = map from other midpoints to index of corresponding ls column
    # index["two_paths"][(s, t)]["triangles"] = map from midpoints to index of corresponding triangle column
    def _build_index():
        index = {"double_edges": {}, "nodes": {}, "edges": {}, "two_paths": {}}

        def _init_index(base_points):
            if base_points not in index["two_paths"]:
                index["two_paths"][base_points] = {
                    "base": None,
                    "nonbase": {},
                    "triangles": {},
                }

        for idx, cell in enumerate(codomain_cells):
            if isinstance(cell, LongSquareCol):
                s = cell.start = cell.start
                t = cell.end
                _init_index((s, t))
                mids = cell.midpoints
                index["two_paths"][(s, t)]["base"] = mids[0]
                index["two_paths"][(s, t)]["nonbase"][mids[1]] = idx
            elif isinstance(cell, DirectedTriangleCol):
                s = cell.two_path[0]
                t = cell.two_path[2]
                _init_index((s, t))
                index["two_paths"][(s, t)]["triangles"][cell.two_path[1]] = idx
            elif isinstance(cell, DoubleEdgeCol):
                index["double_edges"][cell.forward_edge] = idx
            elif isinstance(cell, NodeCol):
                index["nodes"][cell.node] = idx
            elif isinstance(cell, EdgeCol):
                index["edges"][cell.edge] = idx
            else:
                raise ValueError("Received cells not produced by RegularPathHomology")
        return index

    index = _build_index()

    def _map_node(cell):
        return [index["nodes"][cell.node]]

    def _map_edge(cell):
        fu = vertex_map(cell.edge[0])
        fv = vertex_map(cell.edge[1])
        if fu == fv:
            return []
        else:
            return [index["edges"][(fu, fv)]]

    def _map_double_edge(cell):
        fu = vertex_map(cell.forward_edge[0])
        fv = vertex_map(cell.forward_edge[1])
        if fu == fv:
            return []
        else:
            return [index["double_edges"][(fu, fv)]]

    def _map_two_path(endpoints, midpoint):
        subindex = index["two_paths"][endpoints]
        if midpoint == subindex["base"]:
            return {subindex["triangles"][midpoint]}
        elif midpoint in subindex["nonbase"]:
            return {
                subindex["triangles"][subindex["base"]],
                subindex["nonbase"][midpoint],
            }
        elif midpoint in subindex["triangles"]:
            return {subindex["triangles"][midpoint]}
        else:
            two_path = f"{endpoints[0]} -> {midpoint} -> {endpoints[1]}"
            raise ValueError(
                f"Found a two-path which is not present in the image: {two_path}"
            )

    def _map_triangle(cell):
        fa = vertex_map(cell.two_path[0])
        fb = vertex_map(cell.two_path[1])
        fc = vertex_map(cell.two_path[2])
        if fa == fb or fb == fc:
            return []
        elif fa == fc:
            return [index["double_edges"][(fa, fb)]]
        else:
            return sorted(_map_two_path((fa, fc), fb))

    def _map_ls(cell):
        fs = vertex_map(cell.start)
        ft = vertex_map(cell.end)
        fu = vertex_map(cell.midpoints[0])
        fv = vertex_map(cell.midpoints[1])
        if len(set([fs, ft, fu, fv])) < 4:
            raise NotImplementedError(
                "Currently only support maps which do not identify vertices of any long squares"
            )
        columns = set()
        for midpoint in [fu, fv]:
            cols_to_add = _map_two_path((fs, ft), midpoint)
            # Add columns with symmetric difference to match Z_2 addition
            columns = columns.symmetric_difference(cols_to_add)
        return sorted(columns)

    def _get_image(cell):
        if isinstance(cell, NodeCol):
            return _map_node(cell)
        elif isinstance(cell, EdgeCol):
            return _map_edge(cell)
        elif isinstance(cell, DoubleEdgeCol):
            return _map_double_edge(cell)
        elif isinstance(cell, DirectedTriangleCol):
            return _map_triangle(cell)
        elif isinstance(cell, LongSquareCol):
            return _map_ls(cell)
        else:
            raise ValueError("Received cells not produced by RegularPathHomology")

    return _get_image
