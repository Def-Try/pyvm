gpu = component.gpu
y = 0
w, h = gpu.get_resolution()

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
#    e = uptime()+1
#    while uptime() < e: pass

cprint([f"[ {uptime():.6f} ] Welcome to ", 255, 255, 255], ["PythOS", 0, 255, 127], ["!", 255, 255, 255])

fs = component.hdd

log("Discovered RootFS")

def dofile(path, globs=globals(), fn=None):
    file = fs.open(path)
    code = file.read()
    file.close()
    return dostring(code, globs=globs, fn=fn)

dofile("/lib/package.py")
log("Package management ready")

for type, item in fs.list("/boot"):
    if type != "file" or not item.endswith(".py"): continue
    log(f"Running /boot/{item}...")
    _log = log
    def log(text):
        _log(f"/boot/{item}: "+str(text))
    dofile(f"/boot/{item}", fn=f"/boot/{item}")
    log = _log

log("Initialising shell...")

import shell

shell.init()

globals()["RUNTIME"] = "R"

shell.run()


component.computer.shutdown()
