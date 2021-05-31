
import struct


class Shent:
    "Section header table entry"
    def __init__(self, ent: bytes):
        self.name: str
        a, b, c, d, e, f, g, h, i, j = \
            struct.unpack('<IIQQQQIIQQ', ent)
        self.data = ent
        self.sh_name = a
        self.sh_type = b
        self.sh_flags = c
        self.sh_addr = d
        self.sh_offset = e
        self.sh_size = f
        self.sh_link = g
        self.sh_info = h
        self.sh_addralign = i
        self.sh_entsize = j

    def __str__(self):
        return f"name={self.name} type={self.sh_type:#0x} " \
               f"size={self.sh_size} flags={self.sh_flags:#010x}"
