import os
import sys
import time
import json
import uuid
import traceback
import struct
import random
import signal
import atexit
import _thread as thread
import threading
from collections import defaultdict

from modules.isolation import set_name
__name__ = "__PYVM_RUNNER_"+str(random.randint(10000, 99999))+"__"
set_name(__name__)

from modules import kbhit, traceback, component, components, uuids, nonblockinginput

__kbhit = None
__buffer = []

def doch(ch):
    if os.name == 'nt':
        if ch == "\r":
            return "\n"
        return ch
    else:
        if ch == "\x7f": ch = "\b"
        return ch

def quit_function(fn_name):
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush()
    thread.interrupt_main()

def exit_after(s):
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer

__shown = -1

__components = components.Components([],
    {"cpu": component.CPU,
     "gpu": component.GPU,
     "hdd": component.HDD,
     "computer": component.Computer,
     "eeprom": component.EEPROM,
     "keyboard": component.Keyboard}
)

scr = component.GPU()
scr.set_resolution(min(85, scr.max_resolution()[0]), min(25, scr.max_resolution()[1]))

__components.connect(component.CPU())
__components.connect(scr)
__components.connect(component.HDD("disks/01/", uuids.uuids["hdd0"]))
__components.connect(component.HDD("disks/02/", uuids.uuids["hdd1"]))
__components.connect(component.Computer())
__components.connect(component.EEPROM("machine/bios.py", "machine/data.bin"))
__components.connect(component.Keyboard())

starttime = 0
def uptime(): return time.time() - starttime

def error(*message):
    message = [i.split("\n") for i in message]
    msg = []
    for m in message:
        msg += m
    message = msg

    __components.gpu.set_background(0, 0, 255)
    __components.gpu.set_foreground(255, 255, 255)
    __components.gpu.fill(0, 0, *__components.gpu.get_resolution(), " ")
    w, h = __components.gpu.get_resolution()
    y = int(h / 2 - len(message) / 2)
    for n,line in enumerate(message):
        line = str(line).strip()
        x = int(w / 2 - len(line) / 2)
        __components.gpu.set(x, y+n, line)
    __components.computer.shut = 1

def _kbevent(keyboard):
    k = keyboard.pullkey()
    if not k: return
    while k:
        __components.computer.push_signal(__components.computer.create_signal("key_pushed", k))
        k = keyboard.pullkey()

__ltick = 0
def _ticker(uptime):
    global __ltick
    if __ltick + 1.0 > uptime(): return
    __components.computer.push_signal(__components.computer.create_signal("tick"))
    __ltick = uptime()

class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def dostring(code: str, *, globs=None, fn=None):
    #_, globs = run(code, globs=globs, fn=fn)
    compiled = compile(code, fn or "<dostring>", "exec")
    ret = exec(compiled, globs)
    return globs

def run(code: str, *, globs=None, fn=None):
    uninitedglobs = not globs
    rglobs = globs
    globs = globs if globs else {}

    def _unimport(*args, **kwargs): raise ImportError("Package management not ready")
    def _dostring(code, globs_=globs, fn=None):
        return dostring(code, globs=globs_, fn=fn)
    def _globals(): return {**rglobs, **globs}
    def _locals(): return locs
    def exc_info():
        e = sys.exc_info()
        return [e[0], e[1], e[2].tb_next]
    globs["__source__"] = code
    class _loader:
        def get_source(self, fullname):
            return globs["__source__"]
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
        ptbs("hasattr", hasattr)
        ptbs("setattr", setattr)
        ptbs("getattr", getattr)
        ptbs("SyntaxError", SyntaxError)
        ptbs("Exception", Exception)
        ptbs("BaseException", BaseException)
        ptbs("FileNotFoundError", FileNotFoundError)
        ptbs("ImportError", ImportError)
        ptbs("IndexError", IndexError)
        ptbs("__name__", "__pyvm__")
        globs["__loader__"] = _loader()
        globs["__name__"] = "__pyvm__"
        globs["component"] = __components
        globs["dostring"] = _dostring
        globs["len"] = len
        globs["dir"] = dir
        globs["uptime"] = uptime
        globs["error"] = error
        globs["round"] = round
        globs["range"] = range
        globs["enumerate"] = enumerate
        globs["globals"] = globals
        globs["locals"] = locals
        globs["exc_info"] = exc_info
        globs["traceback"] = traceback
        globs["realtime"] = lambda: time.mktime(time.localtime())-time.timezone

        __components.computer.pusher("kb_event",_kbevent, (__components.keyboard, ))
        __components.computer.pusher("ticker", _ticker, (globs["uptime"], ))

        globs["min"] = min
        globs["max"] = max

        globs["str"] = str
        globs["int"] = int
        globs["float"] = float
        globs["list"] = list
        globs["dict"] = dict
        globs["tuple"] = tuple

        globs["super"] = super

    compiled = compile(code, fn or "<dostring>", "exec")
    ret = exec(compiled, globs)
    return ret, globs

__kbhit = kbhit.KBHit()
@exit_after(0.25)
def keyboard_listener():
    if not __kbhit.kbhit(): return
    c = 'E'
    while c != '':
        c = __kbhit.getch()
        if c == '': break
        __components.keyboard.pushkey(doch(c))
@exit_after(0.25)
def screen_flusher():
    global __shown
    __shown = __components.gpu.show()
    print()
#    print("\033[u", end="")
    print(f"\033[{__shown + 1}A")
def vm_runner():
    with open(__components.eeprom.bios_path, 'r', encoding="utf-8") as f:
        code = f.read()
    ret = run(code, fn=__components.eeprom.bios_path)

    __components.computer.shut = -1 if __components.computer.shut == 0 else __components.computer.shut
    return ret
def shutdowner():
    sys.settrace(None)

    print("\033[?25h", end="", flush=True)
#    print("\033[F" * (__shown + 1))
    __components.gpu.show()
    print()

    with open("machine/uuids.json", 'w') as f:
        f.write(json.dumps(uuids.uuids))

    __kbhit.set_normal_term()
    # sys.exit(0)
    os._exit(0)

def intshutdown(signum=signal.SIGINT, frame=sys._getframe()):
    signal.signal(signum, signal.SIG_IGN)
    error("KeyboardInterrupt")
    __components.computer.shut = -1
    #shutdowner()

__lines = 0
__need_lines_gpuflush = 10000
__need_lines_kblisten = 10
__doing_routine = False
__last_gpuflush = None
def main_routine_dispatcher(frame, _event, arg):
    global __lines, __doing_routine, __last_gpuflush
#    print(frame, _event, arg)
#    time.sleep(0)
    print("", end="", flush=False)
    if frame.f_globals["__name__"] == __name__: return None
    if frame.f_globals.get(frame.f_code.co_name) in [*[r[0] for r in __components.computer.routines], main_routine_dispatcher]: return None

    if __components.computer.shut:
        shutdowner()
        return main_routine_dispatcher

    if __doing_routine: return None

    __doing_routine = True
    sys.settrace(None)
    for routine in __components.computer.routines:
        routine[0](*routine[1])
    sys.settrace(main_routine_dispatcher)
    __doing_routine = False

    if _event == "line":
        __lines += 1
    __doing_routine = True
    sys.settrace(None)
    if __last_gpuflush == None: __last_gpuflush = uptime()
    if uptime() - __last_gpuflush > 1 / 30:
        screen_flusher()
        __last_gpuflush = uptime()
    if __lines % __need_lines_kblisten == 0:
        with nonblockinginput.NonBlockingInput():
            keyboard_listener()
    sys.settrace(main_routine_dispatcher)
    __doing_routine = False
    return main_routine_dispatcher

starttime = time.time()
print("PyVM v1",end=" "*(__components.gpu.max_resolution()[0]-7))

signal.signal(signal.SIGINT, intshutdown)
signal.signal(signal.SIGTERM, intshutdown)

sys.settrace(main_routine_dispatcher)
try:
    print("\033[s", end="", flush=True)
    print("\033[?25l", end="", flush=True)
    vm_runner()
except SystemExit: pass
except BaseException:
    exc = sys.exc_info()
    tr = traceback.format_exception([exc[0], exc[1], exc[2].tb_next])
    fpath = f"machine/crash/{random.randint(10000, 99999)}.log"
    with open(fpath, 'w') as f:
        f.write("\n".join(reversed(tr.split("\n"))))
    finfo = f"Crash report saved to {fpath}..."
    tr_ = "\n".join(tr.split("\n")[-__components.gpu.max_resolution()[1] + 4:])
    nl = '\n'
    if len(tr_) < len(tr):
        tr_ = f"... {len(tr.split(nl)) - len(tr_.split(nl))} more lines ...\n" + tr_
    tr_ += nl + finfo
    error(tr_)

shutdowner()
