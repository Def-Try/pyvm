import io

def init():
    component.gpu.clear()

def input(prompt="", echo=True):
    io.stdout.write(prompt)
    _ = ""
    while True:
        __ = io.stdin.read()
        if __ == "\b":
            _ = _[:-1]
            io.stdout.write("\b \b")
            continue
        io.stdout.write(__)
        if __ == "\n": return _
        _ += __

def run():
    io.stdout.write("Hello!!!\n")
    while True:
        inp = input("$ ")
