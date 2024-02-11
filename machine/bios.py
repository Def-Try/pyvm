gpu = components.gpu
y = 0
w, h = gpu.get_resolution()

def print(stuff):
    global y, h, w
    if y == h:
        components.gpu.copy(0, 1, w, h, 0, 0)
        y -= 1
    components.gpu.set(0, y, stuff)
    y += 1

def delay(s):
    st = uptime()
    while uptime() - st < s: pass

gpu.fill(0, 0, w, h, "█")
delay(0.25)
gpu.fill(0, 0, w, h, " ")
delay(0.25)

gpu.set_resolution(*gpu.max_resolution())
w, h = gpu.get_resolution()
gpu.set_foreground(255, 255, 255)

gpu.fill(0, 0, w, h, "█")
delay(0.25)
gpu.fill(0, 0, w, h, " ")
delay(1)

print("Starting up...")
delay(0.25)
print("Component listing:")
delay(0.25)

for v in components.list():
    print(f"  {v.str()}")
    delay(0.1)

def try_boot(fs):
    global print, delay, gpu, y, w, h
    if not fs.exists("/init.py"):
        print(f"{fs.uuid}: no /init.py found")
        return -1
    print(f"{fs.uuid}: /init.py found")
    try:
        file = fs.open("/init.py", 'r')
        code = file.read()
        file.close()
    except:
        print(f"{fs.uuid}: failed to read boot code")
        return -1
    print(f"{fs.uuid}: booting!")
    components.eeprom.data = fs.uuid
    components.set_primary(fs)
    delay(1)
    gpu.clear()
    delay(.2)
    del y, w, h, print, delay, file, gpu
    dostring(code, fn="init.py")
    error("system halted")
    while True: pass

if components.eeprom.data != "":
    for v in components.all("hdd"):
        if v.uuid != components.eeprom.data: continue
        try_boot(v)
    print(f"Boot from {v.uuid} unavailable...")

print("Searching for bootable drive...")
delay(1)

for v in components.all("hdd"):
    try_boot(v)

