import filesystem
import term

def main(raw, flags, args, env):
    path = env.get("cwd") * int(not args[0].startswith("/"))+"/"+args[0]
    if not filesystem.exists(path):
        print(f"ls: no such file or directory: {args[0]}")
        return 1
    if not filesystem.isdirectory(path):
        print(path)
        return 0
    for file in filesystem.list(path):
        if file[0] != "dir":
            term.write(file[1]+"\t")
        else:
            term.write("\033[38;2;0;127;255m"+file[1]+"\033[0m\t")
    print()
