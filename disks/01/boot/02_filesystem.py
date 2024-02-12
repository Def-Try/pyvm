import filesystem

for hdd in components.all("hdd"):
    mount = f"/mnt/{hdd.uuid[:3]}" if not hdd == components.hdd else "/"
    log(f"Mounting {hdd.uuid} to {mount}...")
    filesystem.mount(hdd, mount, silent_fail=False)
