import json
import os
import random
import signal
import sys
import time

from modules.isolation import set_name

print("Preparing __name__")
__name__ = "__PYVM_RUNNER_" + str(random.randint(10000, 99999)) + "__"
set_name(__name__)
print(f"Our __name__ is \"{__name__}\"!")

print("Setting VM start time")
pyvm_start_time = time.time()

from modules import keyboard
from modules import component
from modules import components as _components
from modules import uuids
from modules import dotdict
from modules import traceback

print("Initialising keyboard capture...", end="")
kbhit = keyboard.KBHit()
nbi = keyboard.NonBlockingInput()
print("OK")
shown = -1
print("Initialising components...")
ctypes = {"cpu": component.CPU,
          "gpu": component.GPU,
          "hdd": component.HDD,
          "ram": component.RAM,
          "computer": component.Computer,
          "eeprom": component.EEPROM,
          "keyboard": component.Keyboard}
components = _components.Components([], ctypes)

with open("machine/machine.json", 'r') as f:
    config = json.load(f)
for type_, data in config:
    if not ctypes.get(type_):
        print(f"  UNKNOWN COMPONENT TYPE: {type_}")
        sys.exit(1)
    print(f"  Installed: {type_} / {data['id']}")
    component_ = ctypes.get(type_)(data, uuids.uuids[data["id"]])
    components.connect(component_)

try: components.computer
except: print(f"  FAIL: NO COMPUTER INSTALLED"); sys.exit(1)

try: components.cpu
except: print(f"  FAIL: NO CPU INSTALLED"); sys.exit(1)

try: components.ram
except: print(f"  FAIL: NO RAM INSTALLED"); sys.exit(1)

try: components.gpu
except: print(f"  FAIL: NO GPU INSTALLED"); sys.exit(1)

try: components.eeprom
except: print(f"  FAIL: NO EEPROM INSTALLED"); sys.exit(1)

components.computer.components = components

vm_globals = dotdict.dotdict({"__builtins__": dotdict.dotdict()})


def getch():
    with nbi:
        return keyboard.doch(kbhit.getch())


last_gpu_flush = 0
linecount = 0


def shutdowner():

    sys.settrace(None)

    print(f"\033[{shown + 1}A")
    print("\033[?25h", end="", flush=True)
    #    print("\033[F" * (__shown + 1))
    components.gpu.show()
    print()

    with open("machine/uuids.json", 'w') as f:
        f.write(json.dumps(uuids.uuids))

    kbhit.set_normal_term()
    # sys.exit(0)
    os._exit(0)


def intshutdown(signum=signal.SIGINT, frame=None):
    signal.signal(signum, signal.SIG_IGN)
    error("KeyboardInterrupt")
    components.computer.shut = -1
    #shutdowner()


def main_routine_dispatcher(frame, _event, arg):
    global shown, last_gpu_flush, linecount
    if _event == 'line':
        linecount += 1
    if linecount % components.cpu.speed == 0:
        [print("", end="", flush=False) for i in range(10000)]
        linecount += 1
    name = frame.f_globals.get("__name__")
    # print(name)
    if components.computer.shut:
        shutdowner()
        return None
    if name == __name__:
        return None
    f = [frame]
    while f[-1].f_back != None:
        f += [f[-1].f_back]
    if f[-3].f_code.co_name != "run":
        return None
    size = 0
    know = []
    fr = f[:-4]
    for frame_ in fr:
        for k,v in frame_.f_globals.items():
            if str(k) + str(v) in know: continue
            know += [str(k) + str(v)]
            size += sys.getsizeof(k) + sys.getsizeof(v)
    try:
        raise ValueError()
    except ValueError as e:
        tb = e.__traceback__
    if size > components.computer.total_ram:
        error(f"ram overflowed ({size} > {components.computer.total_ram})",
              f"at {str(f[0].f_code.co_filename)}:{str(f[0].f_lineno)}",
              f"function {str(f[0].f_code.co_name)}")
        return None
        sys.excepthook(MemoryError, MemoryError("too much ram used"), tb)

    # print(name)
    if vm_globals.uptime() - last_gpu_flush > 1 / components.gpu.refreshrate:
        print(f"\033[{shown + 1}A")
        shown = components.gpu.show()
        print()
        last_gpu_flush = vm_globals.uptime()
    got_char = getch()
    if got_char and got_char != '':
        for ch in got_char:
            components.computer.push_signal(components.computer.create_signal("key_pushed", ch))
        # components.keyboard.pushkey(got_char)

    return main_routine_dispatcher


def except_hook(*args, **kwargs):
    sys.settrace(None)
    exc = args
    tr = traceback.format_exception([exc[0], exc[1], exc[2]])
    fpath = f"machine/crash/{random.randint(10000, 99999)}.log"
    with open(fpath, 'w') as f:
        f.write("\n".join(reversed(tr.split("\n"))))
    finfo = f"Crash report saved to {fpath}..."
    tr_ = "\n".join(tr.split("\n")[-components.gpu.max_resolution()[1] + 4:])
    nl = '\n'
    if len(tr_) < len(tr):
        tr_ = f"... {len(tr.split(nl)) - len(tr_.split(nl))} more lines ...\n" + tr_
    tr_ += nl + finfo
    error(tr_)
    sys.__excepthook__(*args, **kwargs)
    shutdowner()


def run(code, globals_=None, fn="<stdin>"):
    globals_ = globals_ or vm_globals
    exec(compile(code, fn or "<dostring>", "exec"), globals_)
    return globals_


def error(*message):
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
    components.computer.shut = 1


def run_vm():
    with open(components.eeprom.bios_path, 'r', encoding="utf-8") as f:
        code = f.read()
    ret = run(code, globals_=vm_globals, fn=components.eeprom.bios_path)

    components.computer.shut = -1 if components.computer.shut == 0 else components.computer.shut
    return ret


vm_globals.component = components
vm_globals.dostring = run
vm_globals.globals = lambda: vm_globals
vm_globals.uptime = lambda: time.time() - pyvm_start_time

vm_globals.__builtins__.__build_class__ = __builtins__.__build_class__
vm_globals.__builtins__.isinstance = __builtins__.isinstance
vm_globals.__builtins__.issubclass = __builtins__.issubclass
vm_globals.__builtins__.id = __builtins__.id
vm_globals.__builtins__.type = __builtins__.type
vm_globals.__builtins__.object = __builtins__.object
vm_globals.__builtins__.hasattr = __builtins__.hasattr
vm_globals.__builtins__.getattr = __builtins__.getattr
vm_globals.__builtins__.setattr = __builtins__.setattr
vm_globals.__builtins__.dir = __builtins__.dir
vm_globals.__builtins__.Exception = Exception
vm_globals.__builtins__.BaseException = BaseException
vm_globals.__builtins__.SyntaxError = SyntaxError
vm_globals.__builtins__.FileNotFoundError = FileNotFoundError

vm_globals.executor = dotdict.dotdict()
vm_globals.executor.compile = compile
vm_globals.executor.exec = exec

vm_globals.__name__ = "__main__"

vm_globals.__builtins__.len = __builtins__.len
vm_globals.__builtins__.min = __builtins__.min
vm_globals.__builtins__.max = __builtins__.max
vm_globals.__builtins__.round = __builtins__.round
vm_globals.__builtins__.range = __builtins__.range

vm_globals.__builtins__.exc_info = sys.exc_info
vm_globals.__builtins__.error = error

vm_globals.__builtins__.str = __builtins__.str
vm_globals.__builtins__.int = __builtins__.int
vm_globals.__builtins__.float = __builtins__.float
vm_globals.__builtins__.list = __builtins__.list
vm_globals.__builtins__.dict = __builtins__.dict
vm_globals.__builtins__.tuple = __builtins__.tuple
vm_globals.__builtins__.super = __builtins__.super
vm_globals.__builtins__.enumerate = __builtins__.enumerate
vm_globals.__builtins__.realtime = lambda: time.time()
print("VM globals done")

signal.signal(signal.SIGINT, intshutdown)
signal.signal(signal.SIGTERM, intshutdown)
print("Signal shutdown done")

print("Main routine dispatcher enable")
sys.settrace(main_routine_dispatcher)
sys.excepthook = except_hook

print(f"PREP took {time.time() - pyvm_start_time:02f} seconds")

print("\033[s", end="", flush=True)
print("\033[?25l", end="", flush=True)

run_vm()