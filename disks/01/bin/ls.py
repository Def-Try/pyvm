import filesystem

def main(raw, flags, args, env):
    for file in filesystem.list(env.get("cwd") * int(not args[0].startswith("/"))+args[0]):
        # TODO: ANSI codes support frfr
        if file[0] == "dir":
            cclr = component.gpu.get_foreground()
            component.gpu.set_foreground(0, 127, 255)
        print(file[1], end="\t")
        if file[0] == "dir":
            component.gpu.set_foreground(*cclr)
    print()
