from modules.component import Component
from modules.isolation import get_name

__name__ = get_name()

class Components:
    def __init__(self, components, types):
        self.components = components
        self.types = types
        self.primaries = {}
    def __getattr__(self, attr):
        if attr in self.primaries:
            return self.primaries[attr]
        if attr in self.types:
            type = self.types[attr]
            for c in self.components:
                 if not isinstance(c, type): continue
                 self.primaries[attr] = c
                 return c
        raise IndexError(f"No such component: {attr}")
    def connect(self, component: Component):
        self.components.append(component)
        return component
    def list(self):
        for c in self.components: yield c
    def all(self, type):
        _type = self.types[type]
        for c in self.components:
            if isinstance(c, _type): yield c
    def set_primary(self, component):
        type = None
        for k,t in self.types.items():
            if isinstance(component, t): type = k
        self.primaries[type] = component