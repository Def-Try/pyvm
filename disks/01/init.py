gpu = component.gpu
y = 0
w, h = gpu.get_resolution()

_dostring = dostring
def dostring(code, globs=globals(), fn=None, influence_globals=False):
    if not influence_globals and globs == globals(): globs = globals().copy()
    return _dostring(code, globs_=globs, fn=fn)

globals()["RUNTIME"] = "I"

def cprint(*stuff):
    global y, h, w, gpu
    if y == h:
        gpu.copy(0, 1, w, h, 0, 0)
        y -= 1
    x = 0
    for i in stuff:
        gpu.set_foreground(*i[1:])
        gpu.set(x, y, i[0])
        x += len(i[0])
    y += 1

def log(text):
    cprint([f"[ {uptime():.6f} ] [", 255, 255, 255], [" OK ", 0, 255, 0], [f"] {text}", 255, 255, 255])

cprint([f"[ {uptime():.6f} ] Welcome to ", 255, 255, 255], ["PythOS", 0, 255, 127], ["!", 255, 255, 255])

fs = component.hdd
def dofile(path, globs=globals(), fn=None, influence_globals=False):
    file = fs.open(path)
    code = file.read()
    file.close()
    return dostring(code, globs=globs, fn=(fn or path), influence_globals=influence_globals)

log("Discovered RootFS")

dofile("/lib/package.py", influence_globals=True)
log("Package management ready")

for type, item in fs.list("/boot"):
    if type != "file" or not item.endswith(".py"): continue
    log(f"Running /boot/{item}...")
    _log = log
    def log(text):
        _log(f"/boot/{item}: "+str(text))
    dofile(f"/boot/{item}", fn=f"/boot/{item}", influence_globals=True)
    log = _log

log("Initialising IO...")
import io

log("Initialising filesystem...")
import filesystem
def dofile(path, globs=globals(), fn=None, influence_globals=False):
    file = filesystem.open(path)
    code = file.read()
    file.close()
    return dostring(code, globs=globs, fn=(fn or path), influence_globals=influence_globals)



log("Initialising Shell...")
io.stdout.y = y
import shell

shell.init()
globals()["RUNTIME"] = "R"
shell.run()

component.computer.shutdown()
