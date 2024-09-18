import filesystem
import random
import components

w, _ = components.gpu.get_resolution()
w -= 1
motdtext = "Something went wrong. Call Gary!!!"

with filesystem.open("/etc/motd") as f:
    lines = f.readlines()
    motdtext = lines[random.random(0, len(lines)-1)].strip()

welcome = f"{components.computer.total_ram // 1024.0}K ram available"

print(f"+{'-'*(w-2)}+")
print(f"| {'PythOS v1':<{w-4}} |")
print(f"| {welcome:<{w-4}} |")
print(f"| {motdtext:<{w-4}} |")
print(f"+{'-'*(w-2)}+")
