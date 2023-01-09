from .abstract import Homology
from grpphati.columns import DirectedTriangleCol


class DirectedFlagComplexHomology(Homology):
    @classmethod
    def get_two_cells(cls, filtration):
        sp_lengths = filtration.edge_dict()
        return [
            DirectedTriangleCol(
                (source, midpoint, target),
                max(
                    first_hop_dist,
                    second_hop_dist,
                    filtration.edge_time((source, target)),
                ),
            )
            for source, distances in sp_lengths.items()
            for midpoint, first_hop_dist in distances.items()
            for target, second_hop_dist in sp_lengths[midpoint].items()
            if source != target
        ]
