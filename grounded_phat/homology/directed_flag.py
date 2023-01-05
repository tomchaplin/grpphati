from .abstract import Homology
from grounded_phat.columns import Column


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
