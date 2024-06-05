"""
SOD
type=library
name=components
libclass=components
needsinit=false
EOD
"""

class NoSuchComponent(Exception): pass

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
        self.primaries[type] = components

components = Components(component.components, component.types)
components.__components = component
