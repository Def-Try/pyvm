import filesystem
import random
w, _ = component.gpu.get_resolution()
w -= 1
motdtext = "Something went wrong. Call Gary!!!"

with filesystem.open("/etc/motd") as f:
    lines = f.readlines()
    motdtext = lines[random.random(0, len(lines)-1)].strip()

_ts = ["night", "morning", "day", "evening"][int(realtime() % (24*60*60) / 3600 // 6)]
welcome = f"Good {_ts}."

print(f"+{'-'*(w-2)}+")
print(f"| {'PythOS v1':<{w-4}} |")
print(f"| {welcome:<{w-4}} |")
print(f"| {motdtext:<{w-4}} |")
print(f"+{'-'*(w-2)}+")
