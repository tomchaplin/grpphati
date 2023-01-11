from abc import ABC, abstractmethod
from grpphati.results import Result


class Backend(ABC):
    @abstractmethod
    def compute_ph(self, cols) -> Result:
        pass
