import filesystem
import term
import shell_utils
import traceback
import executor

def main(raw, env):
    flags, args = shell_utils.parse(raw)
    if len(args[0]) < 1:
        return interactive()

def interactive():
    print("Python Interactive Interpreter v1")
    ps1, ps2 = ">>> ", "... "
    source, code = "", None
    _quit = False
    def _exit(*__, **_):
        _quit = True
        return
    locals = globals().copy()
    while not _quit:
        try:
            term.write(ps1 if not source.endswith("\n") else ps2)
            source += term.read()
        except: pass
        try:
            code = executor.compile(source, "<stdin>", "exec", 0x4200, True)
        except SyntaxError:
            print("Compile error")
            source = ""
        if code is None:
            source += "\n"
        if not source.endswith("\n"):
            try:
                executor.exec(code, locals)
                source = ""
            except Exception as e:
                print("Runtime error")
                print(traceback.format_exception(exc_info()))
                source = ""
