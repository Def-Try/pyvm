import io
import filesystem
import locations

def init():
    component.gpu.clear()

def input(prompt="", echo=True):
    io.stdout.write(prompt)
    _ = ""
    while True:
        __ = io.stdin.read()
        if __ == "\b":
            _ = _[:-1]
            if echo:
                io.stdout.write("\b \b")
            continue
        if echo:
            io.stdout.write(__)
        if __ == "\n": return _
        _ += __

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

def run():
    for type,file in filesystem.list("/etc/autorun/"):
        if type == "dir": continue
        if not file.endswith(".py"): continue
        try:
            dofile("/etc/autorun/"+file, fn="/etc/autorun/"+file)
        except Exception as e:
            print(f"Failed to run /etc/autorun/{file}: {e}")
    while True:
        inp = input("$ ")
        if " " in inp:
            command = inp[:inp.index(" ")]
            string = inp[len(command):]
        else:
            command = inp
            string = ""
        ok = False
        for location in locations.binaries:
            try:
                dofile(location+"/"+command+".py", fn=location+"/"+command)
                ok = True
            except Exception as e:
                try:
                    dofile(location+"/"+command, fn=location+"/"+command)
                    ok = True
                except Exception as e: pass
        if not ok:
            print("sh: no such file or directory: "+command)
