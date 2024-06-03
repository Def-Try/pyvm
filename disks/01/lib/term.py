import io

history = []

def read(echo=True):
    _ = ""
    hptr = len(history)
    cptr = 0
    history.append("")
    io.should_blink = True
    while True:
        history[hptr] = _
        __ = io.stdin.read(1)
        if __ == '': continue
        if __ == "\x1b":
            __ = io.stdin.read(1)
            if __ != "[":
                _ += "\x1b"+__
                if echo:
                    io.stdout.write("\x1b"+__)
                continue
            __ = io.stdin.read(1)
            if __ == "A": # up
                if hptr <= 0: continue
                io.stdout.write(" \b"+"\b \b"*len(_))
                hptr -= 1
                _ = history[hptr]
                io.stdout.write(_)
                cptr = len(_)
                continue
            if __ == "B": # down
                if hptr >= len(history)-1: continue
                io.stdout.write(" \b"+"\b \b"*len(_))
                hptr += 1
                _ = history[hptr]
                io.stdout.write(_)
                cptr = len(_)
                continue
            if __ == "C": # right
                if cptr == len(_): continue
                cptr += 1
                cptr = min(cptr, len(_))
                _ = _+"  "
                io.stdout.write(f"{_[cptr-1]}")
                _ = _[:-2]
            if __ == "D": # left
                if cptr == 0: continue
                cptr -= 1
                cptr = max(cptr, 0)
                io.stdout.write(f"\b"+_[cptr:]+"\b"*(len(_)-cptr))
            continue
        if __ == "\b":
            if _ == "": continue
            _ = _[:cptr-1] + _[cptr:]
            io.stdout.write("\b"*(cptr)+_+" "+"\b"*(len(_)-cptr+2))
#            io.stdout.write("\b")
            cptr -= 1
            continue
        if __ == "\n":
            io.should_blink = False
            io.stdout.write(_[cptr:])
            io.stdout.write("\n")
            return _
        if echo:
            io.stdout.write(__)
            io.stdout.write(_[cptr:]+"\b"*(len(_)-cptr))
        cptr += 1
        _ = _[:cptr - 1] + __ + _[cptr - 1:]
