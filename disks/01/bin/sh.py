import io
import filesystem
import locations
import term

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

def parse(string):
    flags = [""]
    args = [""]
    flag = False
    one_letter_flag = False
    for ch in string:
        if ch == "-":
            if flag and one_letter_flag:
                one_letter_flag = False
                continue
            if flag and not one_letter_flag:
                flags[-1] += "-"
                continue
            flag = True
            one_letter_flag = True
            continue
        if ch == " ":
            if flag:
                flags.append("")
            else:
                args.append("")
            flag = False
            one_letter_flag = False
        if flag and not one_letter_flag:
            flags[-1] += ch
        elif flag:
            flags[-1] += ch
            flags.append("")
        else:
            args[-1] += ch
    return [i.strip() for i in flags], [i.strip() for i in args]

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
            try:
                prg = dofile(location+"/"+command+".py", fn=location+"/"+command+".py")
                if prg.get("main"): prg.get("main")(string, *parse(string), ENV)
                ok = True
            except filesystem.FSException as e:
                try:
                    prg = dofile(location+"/"+command, fn=location+"/"+command)
                    if prg.get("main"): prg.get("main")(string, *parse(string), ENC)
                    ok = True
                except filesystem.FSException as e: pass
        if not ok:
            print("sh: no such file or directory: "+command)
    exit_now = False

def main(raw, flags, args, env):
    return run(False)
