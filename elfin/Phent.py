
import struct


class Phent:
    "Program header table entry"
    def __init__(self, ent: bytes):
        a, b, c, d, e, f, g, h = \
            struct.unpack("<IIQQQQQQ", ent)
        self.data = ent
        self.p_type = a
        self.p_flags = b
        self.p_offset = c
        self.p_vaddr = d
        _ = e
        self.p_filesz = f
        self.p_memsz = g
        self.p_align = h

    def __str__(self):
        return f"type={self.p_type:#0x} flags={self.p_flags:#010x} " \
               f"off={self.p_offset:#010x} vaddr={self.p_vaddr:#010x} " \
               f"memsz={self.p_memsz:#010x}"
