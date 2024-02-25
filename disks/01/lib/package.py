loaded = {}

class Module:
    def __init__(self, mdict):
        for k,v in mdict.items():
            self.__setattr__(k, v if not isinstance(v, dict) else Module(v))

locations = Module({"libs": ['/lib']})

def importer(name, globals, locals, names, level):
    if name in loaded:
        return loaded[name]
    mod = None
    for location in locations.libs:
        try:
            mod = dofile(f"{location}/{name}.py", globs=globals, fn=f"{location}/{name}.py")
            break
        except FileNotFoundError:
            pass
    if mod is None:
        raise ImportError("Module can not be found.")
    mod = Module(mod)
    loaded[name] = mod
    return mod

__builtins__.__dict__["__import__"] = importer
__builtins__.__import__ = importer

import locations
