import io
import filesystem
import locations
import term
import traceback

ENV = {}

builtins = {}
exit_now = False
def exit(raw):
    global exit_now
    exit_now = True
builtins["exit"] = exit

def init():
    global ENV
    ENV = {"cwd": "/"}

def run(fallback=False):
    global ENV, exit_now
    if not fallback:
        for type,file in filesystem.list("/etc/autorun"):
            if type == "dir": continue
            if not file.endswith(".py"): continue
            try:
                dofile("/etc/autorun/"+file, fn="/etc/autorun/"+file)
            except Exception as e:
                print(f"Failed to run /etc/autorun/{file}: {e}")
    else:
        print("+--------------------------+")
        print("|       !! WARNING !!      |")
        print("| RUNNING IN FALLBACK MODE |")
        print("+--------------------------+")
    while not exit_now:
        print("$ ", end="")
        inp = term.read()
        if " " in inp:
            command = inp[:inp.index(" ")]
            string = inp[len(command)+1:]
        else:
            command = inp
            string = ""
        if command in builtins:
            builtins[command](string)
            continue
        if command.strip() == '': continue
        ok = False
        for location in locations.binaries:
            path = location+"/"+command+".py" if not command.startswith(".") or command.startswith("/") else command
#            print(path, filesystem.exists(path))
            if filesystem.exists(path):
                try:
                    prg = dofile(path, fn=path)
                    if prg.get("main"): prg.get("main")(string, ENV)
                except Exception:
                    print("Exception catched by shell")
                    print(traceback.format_exception(exc_info()))
                ok = True
            if ok or not path.startswith(location): break
        if not ok:
            print("sh: no such file or directory: "+command)
    exit_now = False
    return 0

def main(raw, env):
    return run(False)
