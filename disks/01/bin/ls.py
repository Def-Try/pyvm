import filesystem

def main(raw, flags, args, env):
    path = env.get("cwd") * int(not args[0].startswith("/"))+"/"+args[0]
    if not filesystem.exists(path):
        print(f"ls: no such file or directory: {args[0]}")
        return 1
    if not filesystem.isdirectory(path):
        print(path)
        return 0
    for file in filesystem.list(path):
        # TODO: ANSI codes support frfr
        if file[0] == "dir":
            cclr = component.gpu.get_foreground()
            component.gpu.set_foreground(0, 127, 255)
        print(file[1], end="\t")
        if file[0] == "dir":
            component.gpu.set_foreground(*cclr)
    print()
