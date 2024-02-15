import json
from collections import defaultdict
from modules.isolation import get_name

__name__ = get_name()

uuids = defaultdict(lambda: str(uuid.uuid4()))

try:
    open("machine/uuids.json", 'r').close()
except: pass
with open("machine/uuids.json", 'r') as f:
    uuids_ = json.load(f)

for k,uuid in uuids_.items():
    uuids[k] = uuid

with open("machine/uuids.json", 'w') as f:
    f.write(json.dumps(uuids))