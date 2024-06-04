import filesystem
import components

for hdd in components.all("hdd"):
    mount = f"/mnt/{hdd.uuid[:3]}" if not hdd == components.hdd else "/"
    if mount == "/":
        if not filesystem.exists("/mnt"):
            filesystem.mkdir("/mnt")

    log(f"Mounting {hdd.uuid} to {mount}...")

    filesystem.mount(hdd, mount)
