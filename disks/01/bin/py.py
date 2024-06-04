import filesystem

def main(raw, flags, args, env):
    """
    path = env.get("cwd") * int(not args[0].startswith("/"))+"/"+args[0]
    if not filesystem.exists(path):
        print(f"cat: no such file or directory: {args[0]}")
        return 1
    if filesystem.isdirectory(path):
        print(f"cat: is a directory: {args[0]}")
        return 1

    with filesystem.open(path) as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(0, 0)
        while f.tell() < size:
            print(f.read(1024))
    """
    try:
        dostring(raw)
    except Exception as e:
        print(e)
