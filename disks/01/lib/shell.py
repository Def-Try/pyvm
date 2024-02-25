import filesystem
import package
import io

with filesystem.open("/etc/shell", mode='r') as f:
    _sh_name = f.read().strip()
    _sh_bin = package.Module(dofile(_sh_name))
_fallback_bin = package.Module(dofile("/bin/sh.py"))

def init():
    _sh_bin.init()

def run():
    try:
        _sh_bin.run()
    except Exception as e:
        print(f"Failed to run shell {_sh_name}: {e}")
        print(traceback.format_exception(exc_info()))
    print("Shell exited. Bailing out. You are now on your own. Good luck")
    err = None
    try:
        _fallback_bin.run()
    except Exception as e:
        err = e
    print("Fallback shell exited!")
    if err:
        print(f"Caught exception: {err}")
    print("Kernel panic - not syncing: shell killed!")
    component.computer.shutdown()
