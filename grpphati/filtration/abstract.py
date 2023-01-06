from abc import ABC, abstractmethod


class Filtration(ABC):
    def __init__(self, G):
        self.G = G

    @abstractmethod
    def time(self, edge):
        pass

    @abstractmethod
    def edge_iter(self):
        pass

    @abstractmethod
    def edge_dict(self):
        pass
