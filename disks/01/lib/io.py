class IOStream:
    def __init__(self, direction, onwrite, onread):
        self.direction = direction
        self.onwrite = onwrite
        self.onread = onread

    def write(self, data):
        if self.direction == "ro": raise Exception("Disallowed write on read only stream.")
        return self.onwrite(self, data)
    def read(self, amount=2**31-1):
        if self.direction == "wo": raise Exception("Disallowed read on write only stream.")
        return self.onread(self, amount)