def main(raw, env):
    print("crash requested")
    raise BaseException(raw if raw.strip() else "crash requested")
