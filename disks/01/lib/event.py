"""
SOD
type=library
name=event
needsinit=false
EOD
"""

import components
import random

computer = components.computer

listeners = {}

def handler(stack, signal):
    stack.pop()
    for listener in listeners.get(signal.type, []):
        listener[0](signal)

computer.event_handler = handler

def listen(event, callback):
    listeners[event] = listeners.get(event, [])
    listeners[event].append([callback, random.random(10000, 99999)])
    return listeners[event][-1][-1]
