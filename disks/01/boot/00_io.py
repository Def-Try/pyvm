import io
import filesystem
import components

gpu = components.gpu
def __stdout_drawch(stream, data):
    global gpu
    w, h = gpu.get_resolution()
    if stream.y >= h:
        while stream.y >= h:
            gpu.copy(0, 1, w, h, 0, 0)
            gpu.fill(0, h-1, w, 1, " ")
            stream.y -= 1
    if len(data) == 1:
        if data == "\n":
            stream.y += 1
            stream.x = 0
            if stream.y >= h:
                while stream.y >= h:
                    gpu.copy(0, 1, w+1, h+1, 0, 0)
                    gpu.fill(0, h-1, w, 1, " ")
                    stream.y -= 1
            return
        if data == "\b":
            stream.x -= 1
            if stream.x < 0:
                stream.x = w + stream.x
                stream.y -= 1
                if stream.y < 0:
                    stream.y = h + stream.y
            return
        if data == "\r":
            stream.x = 0
            return
        if data == "\t":
            stream.x = ((stream.x // 8) + 1) * 8
            if stream.x >= w:
                stream.y += 1
                stream.x = 0
                if stream.y >= h:
                    while stream.y >= h:
                        gpu.copy(0, 1, w+1, h+1, 0, 0)
                        gpu.fill(0, h-1, w, 1, " ")
                        stream.y -= 1
            return
        gpu.set(stream.x, stream.y, data)
        stream.x += 1
        if stream.x >= w:
            stream.y += 1
            stream.x = 0
            if stream.y >= h:
                while stream.y >= h:
                    gpu.copy(0, 1, w+1, h+1, 0, 0)
                    gpu.fill(0, h-1, w, 1, " ")
                    stream.y -= 1
        return

def __stdout(stream, data):
    string = list(data[::-1])
    while len(string) > 0:
        ch = string.pop()
        if ch == "\033":
            ch = string.pop() if len(string) > 0 else ''
            if ch != "[":
                __stdout_drawch(stream, ch)
                continue
            ch = string.pop() if len(string) > 0 else ''
            if ch == "H":
                stream.x = stream.y = 0
                continue
            if ch == "M":
                stream.y = max(0, stream.y - 1)
                continue
            if ch == "0":
                ch2 = string.pop() if len(string) > 0 else ''
                if ch2 == "m":
                    gpu.set_background(0, 0, 0)
                    gpu.set_foreground(255, 255, 255)
            if ch == "3" or ch == "4":
                ch2 = string.pop() if len(string) > 0 else ''
                if ch2 == "8":
                    ch3 = string.pop() if len(string) > 0 else ''
                    if ch3 != ';': continue
                    control = ""
                    while ch3 != "m":
                        ch3 = string.pop() if len(string) > 0 else ''
                        control += ch3
                    control = control[2:-1]
                    r, g, b = control.split(";")
                    if ch == "3":
                        gpu.set_foreground(r, g, b)
                    if ch == "4":
                        gpu.set_background(r, g, b)
            continue
        __stdout_drawch(stream, ch)

def __stdin(stream, amount):
    data = stream.data[:amount]
    stream.data = stream.data[amount:]
    return data

stdout = io.IOStream("wo", __stdout, None)
stdin = io.IOStream("ro", None, __stdin)
stdout.x, stdout.y = 0, 0
stdin.data = ""
def keyboard_(event):
    stdin.data += event.args[0]
    stdout.write(" \b")

fill = True
should_blink = False
washere = " "
def tick_(_):
    global fill, washere
    if not should_blink: return
    bg, fg = gpu.get_background(), gpu.get_foreground()
    gpu.set_background(*gpu.get(stdout.x, stdout.y)[1][1])
    gpu.set_foreground(*gpu.get(stdout.x, stdout.y)[1][0])
    gpu.set(stdout.x, stdout.y, gpu.get(stdout.x, stdout.y)[0])
    gpu.set_background(*bg)
    gpu.set_foreground(*fg)
event.listen("key_pushed", keyboard_)
event.listen("tick", tick_)

io.stdout = stdout
io.stdin = stdin

def print(*args, sep="\t", end="\n", file=io.stdout):
    file.write(sep.join(str(i) for i in args))
    file.write(end)

def input(prompt="", echo=True):
    io.stdout.write(prompt)
    _ = ""
    should_blink = True
    while True:
        __ = io.stdin.read(1)
        if __ == "\b":
            if _ == "": continue
            _ = _[:-1]
            io.stdout.write(" \b\b \b")
            continue
        if __ == "\n":
            should_blink = False
            io.stdout.write(" \n")
            return _
        if echo:
            io.stdout.write(__)
        _ += __

globals()["print"] = print
globals()["input"] = input
