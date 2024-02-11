import io

def print(*args):
    for i in args:
        io.stdout.write(i)
    io.stdout.write("\n")
