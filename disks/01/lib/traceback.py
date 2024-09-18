def trace_exc(trace):
    traceback = ""
    if not "tb_frame" in dir(trace):
        return "HOW??"
    if "tb_next" in dir(trace) and trace.tb_next:
        traceback += trace_exc(trace.tb_next) + "\n"
    traceback += f"File {trace.tb_frame.f_code.co_filename} line {trace.tb_lineno}"
    return traceback

def format_exception(e):
    klass, objekt, trace = e
    print(klass, objekt, trace)
    traceback = trace_exc(trace)
    formatted = f"{traceback}\n{getattr(klass, '__name__', '???')}: {objekt}"
    return formatted
