
import struct
import sys
from typing import BinaryIO

from dumper import Hexdump

DEBUG = True
FILE_HDR_LEN = 24
PKT_HDR_LEN = 16

ETYPE = {
    0x0800: 'IP',
    0x0806: 'ARP'
    }

PROTOCOL = {
    0x06: 'TCP',
    0x01: 'ICMP',
    0x11: 'UDP'
    }


class Globals():
    bo: str
    pkt_num: int


g = Globals()
g.bo = '<'  # byte order
g.pkt_num = 0


def main() -> None:
    fname = sys.argv[1]
    with open(fname, 'rb') as f:
        read_header(f)
        while True:
            pkt_len = read_pkt_header(f)
            if pkt_len > 0:
                process_packet(f, pkt_len)
            else:
                if DEBUG:
                    print('DONE')
                break


def read_header(f: BinaryIO) -> None:
    hdr = f.read(FILE_HDR_LEN)
    if not hdr:
        assert False
    magic = (struct.unpack('<I', hdr[0:4]))[0]
    if magic == 0xa1b2c3d4:
        pass
    elif magic == 0x4d3c2b1a:
        g.bo = '>'
    else:
        assert False
    major, minor, tz, ts, max_len, link_type = \
        struct.unpack(g.bo + '4xHHIIII', hdr)
    if False:
        print(f'major = {major}')
        print(f'minor = {minor}')
        print(f'tz = {tz}')
        print(f'ts = {ts}')
        print(f'max_len = {max_len}')
        print(f'link_type = {link_type}')
    assert major == 2
    assert minor == 4


def read_pkt_header(f: BinaryIO) -> int:
    hdr = f.read(PKT_HDR_LEN)
    # print(f'hdr: {hdr}')
    if not hdr:
        return 0
    else:
        assert len(hdr) == PKT_HDR_LEN
        g.pkt_num += 1
        secs, usecs, pkt_len, raw_len = struct.unpack(g.bo + 'IIII', hdr)
        if DEBUG:
            print(f'PKT {g.pkt_num}: size = {pkt_len}')
        return pkt_len


def process_packet(f: BinaryIO, size: int) -> None:
    # print(f'process packet {len}')
    assert size < 2000  # sanity check
    pkt = f.read(size)
    buff = pkt[12:14]
    etype = struct.unpack('>H', buff)[0]
    if etype in ETYPE:
        print(f'etype = {ETYPE[etype]}')
    else:
        print(f'etype = {etype:04x}')
    payload = pkt[14:]
    size = len(payload)
    if etype in PKT_CODE:
        PKT_CODE[etype](pkt[14:], size)
    else:
        print(f'UNKNOWN packet. Size = {size}')
        dump_pkt(payload, size)


def do_ip_pkt(pkt: bytes, size: int) -> None:
    print(f'IP packet. Size = {size}')

    # b1 = struct.unpack('B', pkt[0])
    b1 = pkt[0]
    version = b1 >> 4
    hdr_size = 4 * (b1 & 0x0f)
    print(f'ver = {version}, hdr size = {hdr_size}')
    if version == 4:
        do_ip_hdr(pkt[0:hdr_size])
        payload = pkt[hdr_size:]
        print('IP data:')
        dump_pkt(payload, len(payload))
    else:
        dump_pkt(pkt, size)


def do_ip_hdr(buff: bytes) -> None:
    print('IPv4 header:')
    p = buff[9]
    if p in PROTOCOL:
        prot = PROTOCOL[p]
        print(f'protocol = {prot}')
    else:
        prot = ''
        print(f'protocol = {p:02x}')
    src = ip_addr(buff[12:16])
    dst = ip_addr(buff[16:20])
    print(f'{src} -> {dst}')
    dump_pkt(buff, len(buff))


def dump_pkt(buff: bytes, size: int):
    "Print one buffer of the file, in lines of LINESIZE bytes"
    offset = 0
    dump = Hexdump()
    while size:
        this = min(size, 16)
        print(dump.dump(buff[offset: offset+this]))
        offset += this
        size -= this
        assert size >= 0


def ip_addr(b: bytes) -> str:
    return f'{b[0]}.{b[1]}.{b[2]}.{b[3]}'


PKT_CODE = {
    0x0800: do_ip_pkt
    }


if __name__ == '__main__':
    main()
