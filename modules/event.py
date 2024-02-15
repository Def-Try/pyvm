from collections import defaultdict
from modules.isolation import get_name

__name__ = get_name()

class Event:
    def __init__(self, type, *args):
        self.type = type
        self.args = args

routines = []

def listlambda(): return list()
class Events:
    def __init__(self):
        self.listeners = defaultdict(listlambda)
        self.stack = []

    def create_event(self, type, *args): return Event(type, *args)

    def push(self, event):
        self.stack.append(event)
        for listener in self.listeners[event.type]:
            listener(event)

    def listen(self, type, callback):
        self.listeners[type].append(callback)

    def pull(self, type):
        return self.stack.pop(0) if len(self.stack) > 0 else None

    def pusher(self, id, callback, args=None):
        global routines
        for routine in routines:
            if routine[2] == id: return
        routines.append([callback, args, id])
