from abc import *
class V(metaclass=ABCMeta):
    @abstractmethod
    def self_print(self):
        print("V")

class W(V):
    def self_print(self):
        super().self_print()
        print("W")

