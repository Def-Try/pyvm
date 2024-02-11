import os
import sys
import time
import json
import uuid
import traceback
from multiprocessing import Process
from multiprocessing.managers import SyncManager as Manager
try:
    open("machine/uuids.json", 'r').close()
except:
    uuids = {
    "cpu": str(uuid.uuid4()),
    "gpu": str(uuid.uuid4()),
    "computer": str(uuid.uuid4()),
    "bios": str(uuid.uuid4()),
    "hdd": [str(uuid.uuid4())]
    }
    with open("machine/uuids.json", 'w') as f:
        f.write(json.dumps(uuids))
with open("machine/uuids.json", 'r') as f:
    uuids = json.load(f)

if os.name == 'nt':
    import msvcrt
else:
    import select

def _listener(keybuffer):
    def kbhit():
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            dr,dw,de = select.select([sys.stdin], [], [], 0)
            return dr != []
    def getch():
        if not kbhit(): return ""
        if os.name == 'nt':
            return msvcrt.getch().decode()
        else:
            return sys.stdin.read(1)
    while True:
        if not kbhit(): continue
        keybuffer.append(getch())
    

keybuffer = []

def get_key():
    global keybuffer
    return keybuffer.pop(0) if len(keybuffer) > 0 else ""

shutdown = 0

class Component:
    def __init__(self, name, brand, uuid):
       self.name = name
       self.brand = brand
       self.uuid = uuid
    def str(self): return f"{self.name} - {self.brand} / {self.uuid}"
    def __str__(self): return self.str()

class CPU(Component):
    def __init__(self):
        super().__init__("CPU", "GDT Rapid 8800K", uuids["cpu"])

# This is a shared object!
# do NOT use private methods and variables it it:
#  they can NOT be piped by manager!
class Screen(Component):
    def __init__(self):
        super().__init__("GPU", "googerlabs TGPU X5", uuids["gpu"])
        self.resolution = (*os.get_terminal_size(),)
        self.set_background(0, 0, 0)
        self.set_foreground(0, 255, 0)
        self.clear()

    def clear(self):
        self.screen = []
        for y in range(self.resolution[1]):
            self.screen.append([])
            for x in range(self.resolution[0]):
                self.screen[y].append(self.Pget_ansi_codes()+" \033[0m")

    def show(self):
        e = ""
        scr = self.screen.copy()
        for line in scr:
            e += "".join(line) + "\n"
        print(e.strip(), end="", flush=True)
        return len(scr)

    def set_resolution(self, width, height):
        self.resolution = (width, height)
        self.screen = self.screen[:height]
        for y in range(max(0, height - len(self.screen))):
            self.screen.append([])
            for x in range(width):
                self.screen[-1].append(" ")
        for y in range(height):
            self.screen[y] = self.screen[y][:width] + [" "] * max(0, width - len(self.screen[y]))

    def get_resolution(self): return (*self.resolution,)

    def max_resolution(self): return (*(i-2 if n == 1 else i for n,i in enumerate(os.get_terminal_size())),)

    def set(self, x, y, string):
        string = str(string)
        for ch in str(string):
            try:
                self.screen[y][x] = self.Pget_ansi_codes()+self.Pcleanise(ch)+"\033[0m"
            except: pass
            x += 1

    def fill(self, x, y, w, h, ch):
        if x < 0:
            w = w + x
        if y < 0:
            h = h + y
        if w > self.get_resolution()[0]:
            w = self.get_resolution()[0]
        if h > self.get_resolution()[1]:
            h = self.get_resolution()[1]
        for ox in range(w):
            for oy in range(h):
                self.screen[y+oy][x+ox] = self.Pget_ansi_codes()+self.Pcleanise(ch)+"\033[0m"

    def copy(self, x1, y1, w, h, x2, y2):
        screen = self.screen.copy()
        for ox in range(w):
            for oy in range(h):
                try:
                    self.screen[y2+oy][x2+ox] = screen[y1+oy][x1+ox]
                except IndexError: pass

    def set_foreground(self, r, g, b): self.fr, self.fg, self.fb = r, g, b

    def set_background(self, r, g, b): self.br, self.bg, self.bb = r, g, b

    def get_foreground(self): return self.fr, self.fg, self.fb

    def get_background(self): return self.br, self.bg, self.bb

    def Pget_ansi_codes(self):
        return f"\033[38;2;{self.fr};{self.fg};{self.fb}m\033[48;2;{self.br};{self.bg};{self.bb}m"

    def Pcleanise(self, char):
        return char.replace("\n", "").replace("\r", "").replace("\b", "")

class HDD(Component):
    def __init__(self, root, uuid):
        super().__init__("HDD", "ohiodevs HDD", uuid)
        self.root = root
    def open(self, path, mode='r'):
        file = open(self.root + self._form_path(path), mode=mode)
        return file
    def _form_path(self, path):
        formed_path = []
        for n,i in enumerate(path.split("/")):
            if i == "": continue
            elif i == ".": continue
            elif i == "..": formed_path = formed_path[:-1]
            else: formed_path.append(i)
        return "/"+"/".join(formed_path)
    def exists(self, path):
        try:
            self.open(path, 'r').close()
            return True
        except:
            return False
    def list(self, path):
        root = self.root + self._form_path(path)
        for item in os.listdir(root):
            if os.path.isfile(root+"/"+item): yield "file", item
            yield "dir", item

class EEPROM(Component):
    def __init__(self, bios_path, data_path):
        super().__init__("EEPROM", "Supernova BIOS", uuids["bios"])
        self.bios_path = bios_path
        self.data_path = data_path
    @property
    def bios(self):
        code = None
        try:
            with open(self.bios_path, 'r') as f: code = f.read()
        except: pass
        return code or "error('No BIOS found')"
    @bios.setter
    def bios(self, _): raise Exception("Not allowed to change BIOS code!")
    @property
    def data(self):
        data = None
        try:
            with open(self.data_path, 'r') as f: data = f.read()
        except: pass
        return data or ""
    @data.setter
    def data(self, data):
        with open(self.data_path, 'w') as f: f.write(data)

class Computer(Component):
    def __init__(self):
        super().__init__("Computer", "googerlabs CreatCase", uuids["computer"])
    def shutdown(self):
        global shutdown
        shutdown.value = 1
        while True: pass

class Keyboard(Component)

class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

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

components = Components([],
    {"cpu": CPU,
     "gpu": Screen,
     "hdd": HDD,
     "computer": Computer,
     "eeprom": EEPROM}
)

scr = Screen()
scr.set_resolution(25, 25)

components.connect(CPU())
components.connect(scr)
components.connect(HDD("disks/01/", uuids["hdd"][0]))
components.connect(Computer())
components.connect(EEPROM("machine/bios.py", "machine/data.bin"))

starttime = 0
def uptime(): return time.time() - starttime

def error(*message):
    global shutdown
    components.gpu.set_background(0, 0, 255)
    components.gpu.set_foreground(255, 255, 255)
    components.gpu.fill(0, 0, *components.gpu.get_resolution(), " ")
    w, h = components.gpu.get_resolution()
    y = int(h / 2 - len(message) / 2)
    for n,line in enumerate(message):
        line = str(line).strip()
        x = int(w / 2 - len(line) / 2)
        components.gpu.set(x, y+n, line)
    shutdown.value = 1

def dofile(filepath: str):
    with open(filepath, 'r', encoding="utf-8") as f:
        code = f.read()
    return dostring(code)

def dostring(code: str, *, globs=None, fn=None):
    _, globs = run(code, globs=globs, fn=fn)
    return globs

def run(code: str, *, globs=None, fn=None):
    global components
    global dofile

    uninitedglobs = not globs
    globs = globs or {}

    def _unimport(*args, **kwargs): raise ImportError("Package management not ready")
    def _dostring(code, fn=None):
        return dostring(code, globs=globs, fn=fn)
    if uninitedglobs:
        globs["__builtins__"] = dotdict()
        def ptbs(name, obj):
            nonlocal globs
            globs["__builtins__"].__dict__[name] = obj
            globs["__builtins__"][name] = obj
        ptbs("__import__", _unimport)
        ptbs("__build_class__", __builtins__["__build_class__"])
        ptbs("isinstance", __builtins__["isinstance"])
        ptbs("object", object)
        ptbs("__name__", __name__)
        globs["components"] = components
        globs["dostring"] = _dostring
        globs["len"] = len
        globs["uptime"] = uptime
        globs["error"] = error
        globs["round"] = round
        globs["range"] = range
        globs["getkey"] = get_key
        globs["Exception"] = Exception

        globs["str"] = str
        globs["int"] = int
        globs["float"] = float
        globs["list"] = list
        globs["dict"] = dict
        globs["tuple"] = tuple

    compiled = compile(code, fn or "<dostring>", "exec")
    try:
        ret = exec(compiled, globs, globs)
    except Exception:
        exc = sys.exc_info()
        error(*[i.strip() for i in traceback.format_exception(exc[0], exc[1], exc[2].tb_next)])
        while True: pass
        return None, globs
    return ret, globs

def _updater(shutdown_,gpu):
    global shutdown
    global components
    shutdown = shutdown_
    components.gpu = gpu
    shown = -1

    while not shutdown.value:
        print("\033[F"*(shown+1))
        shown = gpu.show()
        print()
        time.sleep(1/24)

def _runner(shutdown_,gpu, keybuffer_):
    global shutdown
    global components
    global keybuffer
    keybuffer = keybuffer_
    shutdown = shutdown_
    components.gpu = gpu
    try:
        ret = dofile(components.eeprom.bios_path)
    except BaseException as e:
        error(*traceback.format_exc().split("\n"))
        shutdown.value = 1
        return ret

    shutdown.value = -1
    return ret

starttime = time.time()

if __name__ == "__main__":
    Manager.register('Screen', Screen)
    manager = Manager()
    manager.start()
    inst = manager.Screen()
    inst.set_resolution(*components.gpu.get_resolution())
    components.gpu = inst
    shutdown = manager.Value('shutdown', 0)
    keybuffer = manager.list()

    print("PyVM v1",end="")
    rnrr = Process(target=_runner, args=(shutdown,components.gpu,keybuffer,))
    updr = Process(target=_updater, args=(shutdown,components.gpu,))
    lstr = Process(target=_listener, args=(keybuffer,))
    rnrr.start()
    updr.start()
    lstr.start()

    updr.join()

    rnrr.kill()
    lstr.kill()

    if shutdown.value == -1: error("system halted")

    print("\033[F"*(components.gpu.get_resolution()[1]+1))
    components.gpu.show()
    print()
