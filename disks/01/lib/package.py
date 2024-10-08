dglbs = globals().copy()

loaded = {}

class Module:
    name = "UNK"
    def __init__(self, name, mdict):
        self.name = name
        for k,v in mdict.items():
            setattr(self, k, v if not isinstance(v, dict) else Module(k, v))
    def __str__(self): return f"Module(name='{self.name}')"
    def __repr__(self): return str(self)

locations = Module("locations", {"libs": ['/lib']})

filesystem = Module("abc.filesystem",
                    dofile(f"/lib/abc/filesystem.py",
                           globs={'__name__': 'abc.filesystem', **globals()},
                           fn=f"/lib/abc/filesystem.py")
                    )
ImportError = Module("abc.package",
                     dofile(f"/lib/abc/package.py",
                            globs={'__name__': 'abc.package', **globals()},
                            fn=f"/lib/abc/package.py")
                     ).ImportError
ModuleNotFound = Module("abc.package",
                        dofile(f"/lib/abc/package.py",
                               globs={'__name__': 'abc.package', **globals()},
                               fn=f"/lib/abc/package.py")
                        ).ModuleNotFound

def importer(name, globals, locals, names, level, influence_globals=False):
    if name in loaded:
        return loaded[name]
    mod = None
    for location in locations.libs:
        try:
            mod = dofile(f"{location}/{name.replace('.', '/')}.py", fn=f"{location}/{name.replace('.', '/')}.py", influence_globals=influence_globals)
            break
        except filesystem.NoSuchFileOrDirectory:
            pass
        except Exception as e:
            raise ImportError(e) from e
        if mod: break
        try:
            mod = dofile(f"{location}/{name.replace('.', '/')}/__init__.py", fn=f"{location}/{name.replace('.', '/')}/__init__.py", influence_globals=influence_globals)
            break
        except filesystem.NoSuchFileOrDirectory:
            pass
        except Exception as e:
            raise ImportError(e) from e
        if mod: break
    if mod is None:
        raise ModuleNotFound(f"Module '{name}' can not be found.")
    mod = Module(name, mod)
    if mod.__doc__ and "SOD" in mod.__doc__:
        doc = mod.__doc__
        defin = doc[doc.index("SOD")+3:doc.index("EOD")].strip()
        props = {i.split("=")[0]: "=".join(i.split("=")[1:])for i in defin.split("\n")}
        if props.get("needsinit", False) in ('1', 'y', 'true', 'yes'):
            mod.init()
        mod.name = props.get("name", mod.name)
        if props.get("libclass", None):
            mod2 = mod
            mod = getattr(mod2, props.get("libclass"))
            mod.__lib__ = mod2
    loaded[name] = mod
    return mod

__builtins__.__dict__["__import__"] = importer
__builtins__.__import__ = importer

import locations
import filesystem

loaded["components"] = importer("components", dglbs, {}, [], 0)
del globals()["component"]
loaded["executor"] = executor
del globals()["executor"]

loaded["package"] = Module("package", globals())
