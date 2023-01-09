from abc import ABC, abstractclassmethod
from grpphati.filtrations import Filtration
from grpphati.columns import NodeCol, EdgeCol


class Homology(ABC):
    @classmethod
    def get_cells(cls, dimensions, filtration: Filtration):
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
        return [NodeCol(node, time) for node, time in filtration.node_iter()]

    @classmethod
    def get_one_cells(cls, filtration: Filtration):
        return [EdgeCol(edge, time) for edge, time in filtration.edge_iter()]

    @abstractclassmethod
    def get_two_cells(cls, filtration: Filtration):
        pass
