def main(raw, flags, args):
    print("crash requested")
    raise BaseException(raw if raw.strip() else "crash requested")
