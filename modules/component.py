import os
import sys

from modules.uuids import uuids
from modules.isolation import get_name

__name__ = get_name()

class Component:
    def __init__(self, name, brand, uuid):
       self.name = name
       self.brand = brand
       self.uuid = uuid
    def str(self): return f"{self.name} - {self.brand}"
    def __str__(self): return self.str()

class CPU(Component):
    def __init__(self):
        super().__init__("CPU", "GDT Rapid 8800K", uuids["cpu"])

class BufBit:
    def __init__(self, br, bg, bb, fr, fg, fb, chr):
        self.br = br
        self.bg = bg
        self.bb = bb
        self.fr = fr
        self.fg = fg
        self.fb = fb
        self.chr = chr

    def same(self, other):
        return \
            self.br == other.br and \
            self.bg == other.bg and \
            self.bb == other.bb and \
            self.fr == other.fr and \
            self.fg == other.fg and \
            self.fb == other.fb and \
            self.chr == other.chr

    @staticmethod
    def default():
        return BufBit(0, 0, 0, 255, 255, 255, ' ')

class ImgBuf:
    def __init__(self, width, height):
        self.buf = [0 for _ in range(width * height * 7)]
        self.width = width
        self.height = height
        self.clear()

    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                cursor = (x + y * self.width) * 7
                self.buf[cursor]     = 0
                self.buf[cursor + 1] = 0
                self.buf[cursor + 2] = 0
                self.buf[cursor + 3] = 255
                self.buf[cursor + 4] = 255
                self.buf[cursor + 5] = 255
                self.buf[cursor + 6] = ' '

    def fill_bg(self, r, g, b):
        for x in range(self.width):
            for y in range(self.height):
                cursor = (x + y * self.width) * 7
                self.buf[cursor]     = r
                self.buf[cursor + 1] = g
                self.buf[cursor + 2] = b

    def fill_fg(self, r, g, b, chr = ' '):
        for x in range(self.width):
            for y in range(self.height):
                cursor = (x + y * self.width) * 7
                self.buf[cursor + 3] = r
                self.buf[cursor + 4] = g
                self.buf[cursor + 5] = b
                self.buf[cursor + 6] = chr

    def insert(self, x, y, ref):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        cursor = (x + y * self.width) * 7

        self.buf[cursor]     = ref.br
        self.buf[cursor + 1] = ref.bg
        self.buf[cursor + 2] = ref.bb
        self.buf[cursor + 3] = ref.fr
        self.buf[cursor + 4] = ref.fg
        self.buf[cursor + 5] = ref.fb
        self.buf[cursor + 6] = ref.chr

    def at(self, x, y, ref):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        cursor = (x + y * self.width) * 7

        ref.br  = self.buf[cursor]
        ref.bg  = self.buf[cursor + 1]
        ref.bb  = self.buf[cursor + 2]
        ref.fr  = self.buf[cursor + 3]
        ref.fg  = self.buf[cursor + 4]
        ref.fb  = self.buf[cursor + 5]
        ref.chr = self.buf[cursor + 6]

    def copy_to(self, buf):
        buf.buf = self.buf.copy()
        buf.width = self.width
        buf.height = self.height

    def copy(self):
        buf = ImgBuf(self.width, self.height)
        self.copy_to(buf)
        return buf

    def same_res(self, other):
        return self.width == other.width and self.height == other.height

    def each(self, bit = None):
        if bit is None:
            bit = BufBit.default()
        for y in range(self.height):
            for x in range(self.width):
                self.at(x, y, bit)
                yield x, y, bit

class GPU(Component):
    def __init__(self):
        super().__init__("GPU", "googerlabs TGPU X5", uuids["gpu"])

        self.buffer = ImgBuf(1, 1)
        self.bit = BufBit.default()
        self.prev_buf = None

    def clear(self):
        self.buffer.clear()
        self.prev_buf = None

    def show(self):
        buffer = "\033[H"

        if self.prev_buf is None or not self.prev_buf.same_res(self.buffer):
            self.prev_buf = self.buffer.copy()
            lastcol = (-1, -1, -1, -1, -1, -1)
            for x, y, bit in self.buffer.each():
                if x == 0 and y != 0:
                    buffer += "\n"
                col = (bit.fr, bit.fg, bit.fb, bit.br, bit.bg, bit.bb)
                if col is not lastcol:
                    buffer += f"\033[38;2;{bit.fr};{bit.fg};{bit.fb}m\033[48;2;{bit.br};{bit.bg};{bit.bb}m"
                    lastcol = col
                buffer += bit.chr
        else:
            other = BufBit.default()
            last = (-1, -1)
            lastcol = (-1, -1, -1, -1, -1, -1)
            for x, y, bit in self.buffer.each():
                self.prev_buf.at(x, y, other)
                if not other.same(bit):
                    self.prev_buf.insert(x, y, bit)
                    continue
                if y == last[1]:
                    if x + 1 != last[0]:
                        buffer += f"\033[{last[0] - x}C"
                else:
                    buffer += f"\033[{y+1};{x+1}H" # xterm starts at 1, not 0!
                col = (bit.fr, bit.fg, bit.fb, bit.br, bit.bg, bit.bb)
                if col is not lastcol:
                    buffer += f"\033[38;2;{bit.fr};{bit.fg};{bit.fb}m\033[48;2;{bit.br};{bit.bg};{bit.bb}m"
                    lastcol = col
                buffer += bit.chr
                last = (x, y)

        print(buffer, end="", flush=True)
        return len(buffer)

    def set_resolution(self, width, height):
        self.buffer = ImgBuf(width, height)

    def get_resolution(self): return (self.buffer.width, self.buffer.height)

    def max_resolution(self): return (*(i-2 if n == 1 else i for n,i in enumerate(os.get_terminal_size())),)

    def set(self, x, y, string):
        for ch in str(string):
            self.bit.chr = self.Pcleanise(ch)
            self.buffer.insert(x, y, self.bit)
            x += 1

    def fill(self, x, y, w, h, ch):
        if x < 0:
            w = w + x
        if y < 0:
            h = h + y
        if w > self.get_resolution()[0]:
            w = self.get_resolution()[0]
        if h > self.get_resolution()[1]:
            h = self.get_resolution()[1]
        self.bit.chr = ch
        for ox in range(w):
            for oy in range(h):
                self.buffer.insert(x+ox, y+oy, self.bit)

    def copy(self, x1, y1, w, h, x2, y2):
        buf = self.buffer.copy()
        for ox in range(w):
            for oy in range(h):
                buf.at(x1+ox, y1+oy, self.bit)
                self.buffer.insert(x2+ox, y2+oy, self.bit)

    def set_foreground(self, r, g, b): self.bit.fr, self.bit.fg, self.bit.fb = r, g, b

    def set_background(self, r, g, b): self.bit.br, self.bit.bg, self.bit.bb = r, g, b

    def get_foreground(self): return self.bit.fr, self.bit.fg, self.bit.fb

    def get_background(self): return self.bit.br, self.bit.bg, self.bit.bb

    def Pcleanise(self, char):
        return char.replace("\n", "").replace("\r", "").replace("\b", "")

class HDD(Component):
    def __init__(self, root, uuid):
        super().__init__("HDD", "ohiodevs HDD", uuid)
        self.root = root
    def open(self, path, mode='r'):
        file = open(self.root + self._form_path(path), mode=mode)
        return file
    def _form_path(self, path):
        formed_path = []
        for n,i in enumerate(path.split("/")):
            if i == "": continue
            elif i == ".": continue
            elif i == "..": formed_path = formed_path[:-1]
            else: formed_path.append(i)
        return "/"+"/".join(formed_path)
    def exists(self, path):
        return  os.path.isfile(self.root + "/" + path) or os.path.isdir(self.root + "/" + path)
    def list(self, path):
        root = self.root + self._form_path(path)
        for item in os.listdir(root):
            if os.path.isfile(root+"/"+item):
                yield "file", item
                continue
            yield "dir", item
    def mkdir(self, path):
        path = self.root + self._form_path(path)
        return os.mkdir(path)


class EEPROM(Component):
    def __init__(self, bios_path, data_path):
        super().__init__("EEPROM", "Supernova BIOS", uuids["bios"])
        self.bios_path = bios_path
        self.data_path = data_path
    @property
    def bios(self):
        code = None
        try:
            with open(self.bios_path, 'r') as f: code = f.read()
        except: pass
        return code or "error('No BIOS found')"
    @bios.setter
    def bios(self, _): raise Exception("Not allowed to change BIOS code!")
    @property
    def data(self):
        data = None
        try:
            with open(self.data_path, 'r') as f: data = f.read()
        except: pass
        return data or ""
    @data.setter
    def data(self, data):
        with open(self.data_path, 'w') as f: f.write(data)

class Computer(Component):
    def __init__(self):
        super().__init__("Computer", "googerlabs CreatCase", uuids["computer"])
        self.shut = 0
    def shutdown(self):
        self.shut = 1

class Keyboard(Component):
    def __init__(self):
        super().__init__("Keyboard", "Treeius OC 28520", uuids["keyboard"])
        self.keybuffer = []
    def pullkey(self):
        key = ""
        if len(self.keybuffer) > 0:
            key = self.keybuffer[0]
            self.keybuffer = self.keybuffer[1:]
        return key
    def pushkey(self, key):
        self.keybuffer.append(key)
