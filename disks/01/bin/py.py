import filesystem
import term

from codeop import CommandCompiler, compile_command
import executor

def main(raw, flags, args, env):
    if len(args) < 1:
        return interactive()
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

def interactive():
    print("Python Interactive Interpreter v1")
    ps1, ps2 = ">>> ", "... "
    source = ""
    _quit = False
    def _exit(*__, **_):
        _quit = True
        return
    compile = CommandCompiler()
    locals = {}
    while not _quit:
        try:
            term.write(ps1 if not source.endswith("\n") else ps2)
            source += term.read()
        except: pass
        try:
            code = compile(source, "<stdin>")
        except (OverflowError, SyntaxError, ValueError):
            print("Compile error")
            source = ""
        if code is None:
            source += "\n"
        try:
            executor.runcompiled(code, locals)
        except:
            print("Runtime error")
