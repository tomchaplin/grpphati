from abc import ABC, abstractmethod


class Column(ABC):
    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def dimension(self):
        pass

    @abstractmethod
    def boundary(self):
        pass

    def get_entrance_time(self):
        return self.entrance_time
