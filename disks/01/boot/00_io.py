import io

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
                    gpu.copy(0, 1, w, h, 0, 0)
                    gpu.fill(0, h-1, w, 1, " ")
                    stream.y -= 1
            return
        if data == "\b":
            stream.x -= 1
            return
        if data == "\r":
            stream.x = 0
            return
        gpu.set(stream.x, stream.y, data)
        stream.x += 1
        if stream.x >= w:
            stream.y += 1
            stream.x = 0
            if stream.y >= h:
                while stream.y >= h:
                    gpu.copy(0, 1, w, h, 0, 0)
                    gpu.fill(0, h-1, w, 1, " ")
                    stream.y -= 1
        return

def __stdout(stream, data):
    for ch in data:
        __stdout_drawch(stream, ch)

def __stdin(stream, amount):
    data = stream.data[:amount]
    stream.data = stream.data[amount:]
    return data

stdout = IOStream("wo", __stdout, None)
stdin = IOStream("ro", None, __stdin)
stdout.x, stdout.y = 0, 0
stdin.data = ""
def keyboard_(event):
    stdin.data += event.args[0]
    stdout.write(" \b")

fill = True
def tick_(_):
    global fill
    fill = not fill
    stdout.write("#" if not fill else " ")
    stdout.write("\b")
event.listen("key_pushed", keyboard_)
event.listen("tick", tick_)

def print(*args):
    for i in args:
        io.stdout.write(i)
    io.stdout.write("\n")

io.stdout = stdout
io.stdin = stdin