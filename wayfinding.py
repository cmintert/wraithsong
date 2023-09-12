import collections
import map_logic

Location = TypeVar('Location')  # Generic type for a location on the map


class Graph(Protocoll):
    
    def neighbors(self, id: Location) -> list[Location]: 
        pass

class SimpleGraph(Graph):
    
    def __init__(self):
        self.edges: dict[Location, list[Location]] = {}
    
    def neighbors(self, id: Location) -> list[Location]:
        return self.edges[id]