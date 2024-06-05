from modules.uuids import uuids
from modules.isolation import get_name

__name__ = get_name()

from modules.abc import Component

class Signal:
    def __init__(self, type, *args):
        self.type = type
        self.args = args

class Computer(Component):
    def __init__(self):
        super().__init__("Computer", "googerlabs CreatCase", uuids["computer"])
        self.shut = 0
        self.event_handler = self.__def_handl__
        self.event_stack = []
        self.routines = []

    def shutdown(self):
        self.shut = 1

    def __def_handl__(self, *args, **kwargs):
        pass

    def create_signal(self, type, *args):
        return Signal(type, *args)

    def push_signal(self, signal):
        self.event_stack.append(signal)
        self.event_handler(self.event_stack, signal)

    def pull_signal(self):
        return self.event_stack.pop(0) if len(self.event_stack) > 0 else None

    def pusher(self, id, callback, args=None):
        for routine in self.routines:
            if routine[2] == id: return
        self.routines.append([callback, args, id])
