import os
import sys

from modules.uuids import uuids
from modules.isolation import get_name
__name__ = get_name()

from modules.computer import Computer
from modules.abc import Component

class CPU(Component):
    def __init__(self):
        super().__init__("CPU", "GDT Rapid 8800K", uuids["cpu"])

class GPU(Component):
    def __init__(self):
        super().__init__("GPU", "googerlabs TGPU X5", uuids["gpu"])
        self.resolution = (1, 1)
        self.set_background(0, 0, 0)
        self.set_foreground(0, 255, 0)
        self.clear()

    def clear(self):
        self.screen  = []
        self.screenc = []
        self.buffer  = None
        self.bufferc = None
        for y in range(self.resolution[1]):
            self.screen .append([])
            self.screenc.append([])
            for x in range(self.resolution[0]):
                self.screen [y].append(" ")
                self.screenc[y].append([self.get_background(), self.get_foreground()])

    def show(self):
        if self.buffer == None:
            e = ""
            fg, bg = None, None
            for coline, line in zip(self.screenc, self.screen):
                for clr, smb in zip(coline, line):
                    if clr[1] != fg:
                        fg = clr[1]
                        e += f"\033[38;2;{';'.join([str(i) for i in fg])}m"
                    if clr[0] != bg:
                        bg = clr[0]
                        e += f"\033[48;2;{';'.join([str(i) for i in bg])}m"
                    e += smb
                e += '\n'
            e = e[:-1]
            sys.stdout.write(e)
            sys.stdout.flush()
#            self.buffer  = list(self.screen )
#            self.bufferc = list(self.screenc)
            return len(self.screen)

    def set_resolution(self, width, height):
        self.resolution = (width, height)
        self.screen  = self.screen [:height]
        self.screenc = self.screenc[:height]
        for y in range(max(0, height - len(self.screen))):
            self.screen .append([])
            self.screenc.append([])
            for x in range(width):
                self.screen [-1].append(" ")
                self.screenc[-1].append([self.get_background(), self.get_foreground()])
        for y in range(height):
            self.screen [y] = self.screen [y][:width] + [" "] * max(0, width - len(self.screen [y]))
            self.screenc[y] = self.screenc[y][:width] + [[self.get_background(), self.get_foreground()]] * max(0, width - len(self.screenc[y]))

    def get_resolution(self): return (*self.resolution,)

    def max_resolution(self): return (*(i-2 if n == 1 else i for n,i in enumerate(os.get_terminal_size())),)

    def set(self, x, y, string):
        string = str(string) or ' '
        for ch in str(string):
            try:
                self.screen [y][x] = self.Pcleanise(ch)
                self.screenc[y][x] = [self.get_background(), self.get_foreground()]
            except: pass
            x += 1

    def get(self, x, y):
        return self.screen[y][x], self.screenc[y][x]

    def fill(self, x, y, w, h, ch):
        if x < 0:
            w = w + x
        if y < 0:
            h = h + y
        if w > self.get_resolution()[0]:
            w = self.get_resolution()[0]
        if h > self.get_resolution()[1]:
            h = self.get_resolution()[1]
        for ox in range(w):
            for oy in range(h):
                try:
                    self.screen [y+oy][x+ox] = self.Pcleanise(ch)
                    self.screenc[y+oy][x+ox] = [self.get_background(), self.get_foreground()]
                except IndexError: pass

    def copy(self, x1, y1, w, h, x2, y2):
        screen  = self.screen .copy()
        screenc = self.screenc.copy()
        for ox in range(w):
            for oy in range(h):
                try:
                    self.screen [y2+oy][x2+ox] = screen [y1+oy][x1+ox]
                    self.screenc[y2+oy][x2+ox] = screenc[y1+oy][x1+ox]
                except IndexError: pass

    def set_foreground(self, r, g, b): self.fr, self.fg, self.fb = r, g, b

    def set_background(self, r, g, b): self.br, self.bg, self.bb = r, g, b

    def get_foreground(self): return self.fr, self.fg, self.fb

    def get_background(self): return self.br, self.bg, self.bb

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
