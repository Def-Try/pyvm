gpu = components.gpu
y = 0
w, h = gpu.get_resolution()

def range(x, y=None, z=None):
    start, end, step = x, y, z
    if not z:
        step = 1 if x < y else -1
    if not y:
        end = start
        start = 0
    i = start
    while (i < end if start < end else i > end):
        yield i
        i += step

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
    global cprint
    cprint([f"[ {uptime():.6f} ] [", 255, 255, 255], [" OK ", 0, 255, 0], [f"] {text}", 255, 255, 255])

cprint([f"[ {uptime():.6f} ] Welcome to ", 255, 255, 255], ["PythOS", 0, 255, 127], ["!", 255, 255, 255])

fs = components.hdd

log("Discovered RootFS")

def dofile(path):
    file = fs.open(path)
    code = file.read()
    file.close()
    return dostring(code)

dofile("/lib/package.py")
log("Package management ready")

for type, item in fs.list("/boot"):
    if type != "file" or not item.endswith(".py"): continue
    log(f"Running /boot/{item}...")
    dofile(f"/boot/{item}")

k = ""
while k != "q":
    k = getkey()
    if k == "": continue
    log("Key pressed: "+k+". Press 'q' to exit")
log("Key delivering works.")

components.computer.shutdown()
