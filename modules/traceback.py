import linecache
from modules.isolation import get_name

__name__ = get_name()

def trace_exc(trace):
    traceback = ""
    if not "tb_frame" in dir(trace):
        return "HOW??"
    if "tb_next" in dir(trace) and trace.tb_next:
        traceback += trace_exc(trace.tb_next) + "\n"
    traceback += f"File {trace.tb_frame.f_code.co_filename} line {trace.tb_lineno}"
#    line = linecache.getline(trace.tb_frame.f_code.co_filename, trace.tb_lineno, trace.tb_frame.f_globals)
#    if line:
#        traceback += f"\n{line.strip()}"
    return traceback

def format_exception(e):
    klass, objekt, trace = e
    traceback = trace_exc(trace)
    formatted = f"{traceback}\n{getattr(klass, "__name__", "???")}: {objekt}"
    return formatted
