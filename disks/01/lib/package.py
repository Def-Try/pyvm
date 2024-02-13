loaded = {}

class Module:
    def __init__(self, mdict):
        for k,v in mdict.items():
            self.__setattr__(k, v if not isinstance(v, dict) else Module(v))

def importer(name, globals, locals, names, level):
    if name in loaded:
        return loaded[name]

    mod = dofile(f"/lib/{name}.py", globs=globals, fn=f"/lib/{name}.py")
    mod = Module(mod)
    loaded[name] = mod
    return mod

__builtins__.__dict__["__import__"] = importer
__builtins__.__import__ = importer
