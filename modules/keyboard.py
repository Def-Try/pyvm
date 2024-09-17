import os

if os.name == 'nt':
    import msvcrt

else:
    import sys
    import termios
    import atexit
    from select import select
    import fcntl
    import sys


def doch(ch):
    if os.name == 'nt':
        if ch == b'\xe0':
            ch = msvcrt.getch()
            if ch == b'H':
                ch = b"\x1b[A"
            if ch == b'P':
                ch = b"\x1b[B"
            if ch == b'K':
                ch = b"\x1b[C"
            if ch == b'M':
                ch = b"\x1b[D"
        if ch == b"\r":
            return "\n"
        return ch.decode('utf-8')
    else:
        ch = ch.decode('utf-8')
        if ch == "\x7f":
            ch = "\b"
        return ch


class KBHit:
    def __init__(self):
        if os.name == 'nt':
            pass
        else:
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
            atexit.register(self.set_normal_term)

    def set_unbuffered_term(self):
        self.set_normal_term()
        self.__init__()

    def set_normal_term(self):
        if os.name == 'nt':
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        """ Returns a keyboard character after kbhit() has been called. """
        if not self.kbhit():
            return b''
        if os.name == 'nt':
            ch = msvcrt.getch()
            return ch
        else:
            return sys.stdin.read(1).encode('utf-8')

    @staticmethod
    def kbhit():
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            dr, dw, de = select([sys.stdin], [], [], 0)
            return dr != []


class NonBlockingInput(object):
    def __enter__(self):
        if os.name == 'nt':
            return
        # canonical mode, no echo
        self.old = termios.tcgetattr(sys.stdin)
        new = termios.tcgetattr(sys.stdin)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new)

        # set for non-blocking io
        self.orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        if os.name == 'nt':
            return
        # restore terminal to previous state
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl)
