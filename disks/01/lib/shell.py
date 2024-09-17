import filesystem
import components
import package
import io
import traceback

with filesystem.open("/etc/shell", mode='r') as f:
    _sh_name = f.read().strip()
    _sh_bin = package.Module("__shell__", dofile(_sh_name))
_fallback_bin = package.Module("__fallback_shell__", dofile("/bin/sh.py"))

def init():
    _sh_bin.init()

def run():
    try:
        while _sh_bin.run(False) == 0: pass
    except BaseException as e:
        print(f"Failed to run shell {_sh_name}: {e}")
        print(traceback.format_exception(exc_info()))
    _fallback_bin.init()
    print("Shell exited. Bailing out. You are now on your own. Good luck")
    err = None
    try:
        while _fallback_bin.run(True) == 0: pass
    except BaseException as e:
        err = e
    error("Kernel panic - not syncing: shell killed!")
