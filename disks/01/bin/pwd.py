def main(raw, flags, args, env):
    print(env.get("cwd", "failed to get cwd"))
