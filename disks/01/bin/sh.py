import io
import filesystem
import locations

ENV = {}

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
    global ENV
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
    while True:
        inp = input("$ ")
        if " " in inp:
            command = inp[:inp.index(" ")]
            string = inp[len(command)+1:]
        else:
            command = inp
            string = ""
        if command.strip() == '': continue
        ok = False
        for location in locations.binaries:
            try:
                prg = dofile(location+"/"+command+".py", fn=location+"/"+command+".py")
                if prg.get("main"): prg.get("main")(string, *parse(string), ENV)
                ok = True
            except Exception as e:
                try:
                    prg = dofile(location+"/"+command, fn=location+"/"+command)
                    if prg.get("main"): prg.get("main")(string, *parse(string), ENC)
                    ok = True
                except Exception as e: pass
        if not ok:
            print("sh: no such file or directory: "+command)
