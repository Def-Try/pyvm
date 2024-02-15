import filesystem

for hdd in component.all("hdd"):
    mount = f"/mnt/{hdd.uuid[:3]}" if not hdd == component.hdd else "/"
    log(f"Mounting {hdd.uuid} to {mount}...")
    filesystem.mount(hdd, mount)
