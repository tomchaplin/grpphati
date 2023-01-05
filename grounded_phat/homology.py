from grounded_phat.columns import Column
from grounded_phat.filtrations import Filtration
from abc import ABC, abstractclassmethod


class Homology(ABC):
    @classmethod
    def get_cells(cls, dimensions: list[int], filtration: Filtration):
        return [
            cell for k in dimensions for cell in cls._get_cells_in_dim(k, filtration)
        ]

    # Return cells in basis for k^th grounded chain group
    # Along with the times at which they enter
    @classmethod
    def _get_cells_in_dim(cls, dimension: int, filtration: Filtration):
        if dimension == 0:
            return cls.get_zero_cells(filtration)
        elif dimension == 1:
            return cls.get_one_cells(filtration)
        elif dimension == 2:
            return cls.get_two_cells(filtration)
        else:
            raise ValueError("get_cells only supports dimensions 0, 1, 2")

    @classmethod
    def get_zero_cells(cls, filtration: Filtration):
        return [Column.NODE(node, 0) for node in filtration.G.nodes]

    @classmethod
    def get_one_cells(cls, filtration: Filtration):
        return [Column.EDGE(edge, 0) for edge in filtration.G.edges] + [
            Column.EDGE(edge, dist)
            for edge, dist in filtration.edge_iter()
            if not filtration.G.has_edge(*edge)
        ]

    @abstractclassmethod
    def get_two_cells(cls, filtration: Filtration):
        pass


class RegularPathHomology(Homology):
    @classmethod
    def get_two_cells(cls, filtration):
        two_paths = list(_sorted_two_paths(filtration))
        (cols, bridges) = _split_off_bridges(filtration, two_paths)
        cols = _add_ls_collapsing_directed_triangles(cols, bridges, filtration)
        cols = _add_long_squares(cols, bridges)
        return cols


class DirectedFlagComplexHomology(Homology):
    @classmethod
    def get_two_cells(cls, filtration):
        sp_lengths = filtration.edge_dict()
        return [
            Column.DIRECTED_TRIANGLE(
                (source, midpoint, target),
                max(first_hop_dist, second_hop_dist, filtration.time((source, target))),
            )
            for source, distances in sp_lengths.items()
            for midpoint, first_hop_dist in distances.items()
            for target, second_hop_dist in sp_lengths[midpoint].items()
            if source != target
        ]


class OrderedTuplesHomology(Homology):
    @classmethod
    def get_two_cells(cls, filtration):
        sp_lengths = filtration.edge_dict()
        return [
            Column.DIRECTED_TRIANGLE(
                (source, midpoint, target),
                max(first_hop_dist, second_hop_dist, filtration.time((source, target))),
            )
            if source != target
            else Column.DOUBLE_EDGE(
                (source, midpoint), max(first_hop_dist, second_hop_dist)
            )
            for source, distances in sp_lengths.items()
            for midpoint, first_hop_dist in distances.items()
            for target, second_hop_dist in sp_lengths[midpoint].items()
        ]


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
            cols.append(Column.DOUBLE_EDGE((path[0], path[1]), entrance_time))
        elif filtration.time((path[0], path[2])) <= entrance_time:
            cols.append(
                Column.DIRECTED_TRIANGLE((path[0], path[1], path[2]), entrance_time)
            )
        else:
            try:
                bridges[(path[0], path[2])].append((path[1], entrance_time))
            except KeyError:
                bridges[(path[0], path[2])] = [(path[1], entrance_time)]
    return (cols, bridges)


def _add_ls_collapsing_directed_triangles(cols, bridges, filtration):
    for endpoints, sub_bridges in bridges.items():
        collapse_time = filtration.time(endpoints)
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
            cols.append(
                Column.LONG_SQUARE(
                    (endpoints[0], first_bridge_node, second_bridge_node, endpoints[1]),
                    entrance_time,
                )
            )
    return cols