import os
import sys
import time
import json
import uuid
import traceback
import struct
import random
from collections import defaultdict

from modules.kbhit import KBHit

uuids = defaultdict(lambda: str(uuid.uuid4()))

try:
    open("machine/uuids.json", 'r').close()
except: pass
with open("machine/uuids.json", 'r') as f:
    uuids_ = json.load(f)

for k,uuid in uuids_.items():
    uuids[k] = uuid

with open("machine/uuids.json", 'w') as f:
    f.write(json.dumps(uuids))

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import fcntl

__name__ = "__PYVM_RUNNER_"+str(random.randint(10000, 99999))+"__"

__buffer = []
__kbhit = KBHit()

def doch(ch):
    if os.name == 'nt':
        if ch == "\r":
            return "\n"
        return ch
    else:
        if ch == "\x7f": ch = "\b"
        return ch

def trace_exc(trace):
    traceback = ""
    if trace.tb_next:
        traceback += trace_exc(trace.tb_next) + "\n"
    traceback += f"File {trace.tb_frame.f_code.co_filename} line {trace.tb_lineno}"
    return traceback

def format_exception(e):
    klass, objekt, trace = e
    traceback = trace_exc(trace)
    formatted = f"{traceback}\n{objekt}"
    return formatted

__fds = []
def mkfile(fd=None):
    pass

shutdown = 0

class Component:
    def __init__(self, name, brand, uuid):
       self.name = name
       self.brand = brand
       self.uuid = uuid
    def str(self): return f"{self.name} - {self.brand}"
    def __str__(self): return self.str()

class CPU(Component):
    def __init__(self):
        super().__init__("CPU", "GDT Rapid 8800K", uuids["cpu"])

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
                try:
                    self.screen[y+oy][x+ox] = self.Pget_ansi_codes()+self.Pcleanise(ch)+"\033[0m"
                except IndexError: pass

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
        return  os.path.isfile(self.root + "/" + path) or os.path.isdir(self.root + "/" + path)
    def list(self, path):
        root = self.root + self._form_path(path)
        for item in os.listdir(root):
            if os.path.isfile(root+"/"+item):
                yield "file", item
                continue
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
        shutdown = 1

class Keyboard(Component):
    def __init__(self):
        super().__init__("Keyboard", "Treeius OC 28520", uuids["keyboard"])
        self.keybuffer = []
    def pullkey(self):
        key = ""
        if len(self.keybuffer) > 0:
            key = self.keybuffer[0]
            self.keybuffer = self.keybuffer[1:]
        return key
    def pushkey(self, key):
        self.keybuffer.append(key)

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

class Event:
    def __init__(self, type, *args):
        self.type = type
        self.args = args

routines = []

def listlambda(): return list()
class Events:
    def __init__(self):
        self.listeners = defaultdict(listlambda)
        self.stack = []

    def create_event(self, type, *args): return Event(type, *args)

    def push(self, event):
        self.stack.append(event)
        for listener in self.listeners[event.type]:
            listener(event)

    def listen(self, type, callback):
        self.listeners[type].append(callback)

    def pull(self, type):
        return self.stack.pop(0) if len(self.stack) > 0 else None

    def pusher(self, id, callback, args=None):
        global routines
        for routine in routines:
            if routine[2] == id: return
        routines.append([callback, args, id])

components = Components([],
    {"cpu": CPU,
     "gpu": Screen,
     "hdd": HDD,
     "computer": Computer,
     "eeprom": EEPROM,
     "keyboard": Keyboard}
)

scr = Screen()
scr.set_resolution(75, 25)

components.connect(CPU())
components.connect(scr)
components.connect(HDD("disks/01/", uuids["hdd0"]))
components.connect(HDD("disks/02/", uuids["hdd1"]))
components.connect(Computer())
components.connect(EEPROM("machine/bios.py", "machine/data.bin"))
components.connect(Keyboard())

starttime = 0
def uptime(): return time.time() - starttime

def error(*message):
    global shutdown

    message = [i.split("\n") for i in message]
    msg = []
    for m in message:
        msg += m
    message = msg

    components.gpu.set_background(0, 0, 255)
    components.gpu.set_foreground(255, 255, 255)
    components.gpu.fill(0, 0, *components.gpu.get_resolution(), " ")
    w, h = components.gpu.get_resolution()
    y = int(h / 2 - len(message) / 2)
    for n,line in enumerate(message):
        line = str(line).strip()
        x = int(w / 2 - len(line) / 2)
        components.gpu.set(x, y+n, line)
    shutdown = 1

def dofile(filepath: str):
    with open(filepath, 'r', encoding="utf-8") as f:
        code = f.read()
    return dostring(code)

def dostring(code: str, *, globs=None, fn=None):
    _, globs = run(code, globs=globs, fn=fn)
    return globs


def _kbevent(event, keyboard):
    k = keyboard.pullkey()
    if not k: return
    while k:
        event.push(event.create_event("key_pushed", k))
        k = keyboard.pullkey()

__ltick = 0
def _ticker(event, uptime):
    global __ltick
    if __ltick + 1.0 > uptime(): return
    event.push(event.create_event("tick"))
    __ltick = uptime()

events = Events()

def run(code: str, *, globs=None, fn=None):
    global components
    global dofile

    uninitedglobs = not globs
    globs = globs or {}

    def _unimport(*args, **kwargs): raise ImportError("Package management not ready")
    def _dostring(code, globs=globs, fn=None): return dostring(code, globs=globs, fn=fn)
    def _globals(): return globs
    def _locals(): return locs
    if uninitedglobs:
        globs["__builtins__"] = dotdict()
        def ptbs(name, obj):
            nonlocal globs
            globs["__builtins__"].__dict__[name] = obj
            globs["__builtins__"][name] = obj

        ptbs("__import__", _unimport)
        if isinstance(__builtins__, dict):
            ptbs("__build_class__", __builtins__["__build_class__"])
            ptbs("isinstance", __builtins__["isinstance"])
        else:
            ptbs("__build_class__", __builtins__.__build_class__)
            ptbs("isinstance", __builtins__.isinstance)
        ptbs("object", object)
        ptbs("__name__", "__pyvm__")
        globs["__name__"] = "__pyvm__"
        globs["components"] = components
        globs["dostring"] = _dostring
        globs["len"] = len
        globs["uptime"] = uptime
        globs["error"] = error
        globs["round"] = round
        globs["range"] = range
        globs["enumerate"] = enumerate
        globs["Exception"] = Exception
        globs["event"] = events
        globs["globals"] = globals
        globs["locals"] = locals
        globs["mkfile"] = mkfile

        globs["event"].pusher("kb_event",_kbevent, (globs["event"], components.keyboard))
        globs["event"].pusher("ticker", _ticker, (globs["event"], globs["uptime"]))

        globs["str"] = str
        globs["int"] = int
        globs["float"] = float
        globs["list"] = list
        globs["dict"] = dict
        globs["tuple"] = tuple

    compiled = compile(code, fn or "<dostring>", "exec")
    ret = exec(compiled, globs)
    return ret, globs

def keyboard_listener():
    if not __kbhit.kbhit(): return
    components.keyboard.pushkey(doch(__kbhit.getch()))
__shown = -1
def screen_flusher():
    global __shown
    print("\033[F" * (__shown + 1))
    __shown = components.gpu.show()
    print()
def vm_runner():
    global shutdown
    ret = dofile(components.eeprom.bios_path)
    shutdown = -1 if shutdown == 0 else shutdown
    return ret
def shutdowner():
    sys.settrace(None)

    print("\033[F" * (__shown + 1))
    components.gpu.show()
    print()

    with open("machine/uuids.json", 'w') as f:
        f.write(json.dumps(uuids))

    __kbhit.set_normal_term()
    sys.exit(0)

__lines = 0
__need_lines_gpuflush = 100
__need_lines_kblisten = 1
__doing_routine = False
def main_routine_dispatcher(frame, event, arg):
    global routines, __lines, shutdown, __doing_routine
    if frame.f_globals["__name__"] == __name__: return None
    if frame.f_globals.get(frame.f_code.co_name) in [*[r[0] for r in routines], main_routine_dispatcher]: return None

    if shutdown:
        shutdowner()
        return None

    if __doing_routine: return None

    __doing_routine = True
    sys.settrace(None)
    a = time.perf_counter()
    for routine in routines:
        routine[0](*routine[1])
    sys.settrace(main_routine_dispatcher)
    __doing_routine = False

    if event == "line":
        __lines += 1
    if __lines % __need_lines_gpuflush == 0:
        screen_flusher()
    if __lines % __need_lines_kblisten == 0:
        keyboard_listener()
    return main_routine_dispatcher

starttime = time.time()
print("PyVM v1",end="")
sys.settrace(main_routine_dispatcher)
try:
    vm_runner()
except SystemExit: pass
except BaseException:
    exc = sys.exc_info()
    error(*format_exception([exc[0], exc[1], exc[2].tb_next]).split("\n"))

shutdowner()
