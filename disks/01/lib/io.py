class IOStream:
    def __init__(self, direction, onwrite, onread):
        self.direction = direction
        self.onwrite = onwrite
        self.onread = onread

    def write(self, data):
        if self.direction == "ro": raise Exception("Disallowed write on read only stream.")
        self.onwrite(self, data)
    def read(self, amount=2**31-1):
        if self.direction == "wo": raise Exception("Disallowed read on write only stream.")
        self.onread(self, amount)

gpu = components.gpu
def __stdout(stream, data):
    global gpu
    w, h = gpu.get_resolution()
    if stream.y >= h:
        while stream.y >= h:
            gpu.copy(0, 1, w, h, 0, 0)
            stream.y -= 1
    if len(data) == 1:
        if data == "\n":
            stream.y += 1
            stream.x = 0
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
        return
    for ch in data:
        __stdout(stream, ch)

stdout = IOStream("wo", __stdout, None)
stdout.x, stdout.y = 0, 0
