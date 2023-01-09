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
