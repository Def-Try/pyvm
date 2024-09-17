from abc.io import InvalidOperation

class IOStream:
    def __init__(self, direction, onwrite, onread):
        self.direction = direction
        self.onwrite = onwrite
        self.onread = onread

    def write(self, data):
        if self.direction == "ro":
            raise InvalidOperation("Disallowed write on read only stream.")
        return self.onwrite(self, data)
    def read(self, amount=2**31-1):
        if self.direction == "wo":
            raise InvalidOperation("Disallowed read on write only stream.")
        return self.onread(self, amount)
