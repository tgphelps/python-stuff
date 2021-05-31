
import struct
from typing import BinaryIO, Optional


FILE_HDR_SIZE = 24
PKT_HDR_SIZE = 16
LINK_HDR_SIZE = 14


class Packet:
    "Class to hold a packet from a pcap file."
    def __init__(self, num: int, header: bytes, data: bytes):
        self.num = num
        self.header = header

        # Extract the link header and set ethertype
        # Warning: This assumes this an Ethernet II frame!
        # (It's all I've tested with.)
        self.link_hdr = data[0:LINK_HDR_SIZE]
        buff = data[12:14]
        self.ethertype = struct.unpack('>H', buff)[0]
        self.data = data[LINK_HDR_SIZE:]
        self.data_len = len(self.data)


class IP_packet:
    "Class to hold an IP packet."
    def __init__(self, buff: bytes):
        b1 = buff[0]
        self.version = b1 >> 4
        self.hdr_size = 4 * (b1 & 0x0f)
        assert self.version == 4  # XXX Can't handle IPv6 yet
        self.hdr = buff[0:self.hdr_size]
        self.data = buff[self.hdr_size:]
        self.data_len = len(self.data)
        self.protocol = self.hdr[9]
        self.src = ip_addr(buff[12:16])
        self.dst = ip_addr(buff[16:20])


class UDP_packet:
    "Class to hold a UDP packet."
    def __init__(self, buff: bytes):
        hdr_len = 8
        self.hdr = buff[0:hdr_len]
        self.data = buff[hdr_len:]
        self.data_len = len(self.data)
        p = self.hdr[0:2]
        self.src = (struct.unpack('>H', p))[0]
        p = self.hdr[2:4]
        self.dst = (struct.unpack('>H', p))[0]


class TCP_packet:
    "Class to hold a TCP packet."
    def __init__(self, buff: bytes):
        p = buff[0:2]
        self.src = (struct.unpack('>H', p))[0]
        p = buff[2:4]
        self.dst = (struct.unpack('>H', p))[0]
        self.hdr_len = 4 * (buff[12] >> 4)
        # print(f'hdr len = {self.hdr_len}')
        self.hdr = buff[0:self.hdr_len]
        self.data = buff[self.hdr_len:]
        self.data_len = len(self.data)

    def decode_flags(self):
        "Return a string showing what flags are set."
        b = self.hdr[9]
        flags = ''
        if (b & 0x20):
            flags += ' URG'
        if (b & 0x10):
            flags += ' ACK'
        if (b & 0x08):
            flags += ' PSH'
        if (b & 0x04):
            flags += ' RST'
        if (b & 0x02):
            flags += ' SYN'
        if (b & 0x01):
            flags += ' FIN'
        return flags


class Reader:
    "Class that can read packets from a pcap file."
    def __init__(self, pcap_file: BinaryIO, debug=False):
        self.pf = pcap_file
        self.fhdr = self.pf.read(FILE_HDR_SIZE)
        self.bo = '<'
        self.pkt_num = 0
        assert len(self.fhdr) == FILE_HDR_SIZE
        magic = (struct.unpack('<I', self.fhdr[0:4]))[0]
        if magic == 0xa1b2c3d4:
            pass
        elif magic == 0x4d3c2b1a:
            self.bo = '>'
        else:
            assert False
        self.major, self.minor, self.tz, self.ts, \
            self.max_len, self.link_type = \
            struct.unpack(self.bo + '4xHHIIII', self.fhdr)
        if debug:
            print(f'major = {self.major}')
            print(f'minor = {self.minor}')
            print(f'tz = {self.tz}')
            print(f'ts = {self.ts}')
            print(f'max_len = {self.max_len}')
            print(f'link_type = {self.link_type}')
        # Tested only with a version 2.4 file, using an Ethernet link.
        assert self.major == 2
        assert self.minor == 4
        assert self.link_type == 1

    def get_packet(self) -> Optional[Packet]:
        "Return next packet from the file, if any."
        hdr = self.pf.read(PKT_HDR_SIZE)
        if not hdr:
            return None
        else:
            assert len(hdr) == PKT_HDR_SIZE
            self.pkt_num += 1
            _, _, pkt_len, _ = struct.unpack(self.bo + 'IIII', hdr)
            assert pkt_len < 2000  # sanity
            data = self.pf.read(pkt_len)
            assert len(data) == pkt_len
            return Packet(self.pkt_num, hdr, data)


def main():
    with open('tgp.pcap', 'rb') as f:
        rdr = Reader(f, debug=True)
        while True:
            pkt = rdr.get_packet()
            if not pkt:
                break
            else:
                print(f'packet {pkt.num}: len = {pkt.data_len} type = \
                    {pkt.ethertype:0x}')
                if pkt.ethertype == 0x800:
                    ip_pkt = IP_packet(pkt.data)
                    print(f'IP ver {ip_pkt.version}')
                    prot = ip_pkt.protocol
                    src = ip_pkt.src
                    dst = ip_pkt.dst
                    print(f'prot = {prot}: {src} -> {dst}')
                    if prot == 6:
                        dgram = TCP_packet(ip_pkt.data)
                        flags = dgram.decode_flags()
                        print(f'TCP port: {dgram.src} -> {dgram .dst}  flags: {flags}')
                        dumper.dump_bytes(dgram.hdr, dgram.hdr_len)
                        print('DATA')
                        if dgram.data_len > 0:
                            dumper.dump_bytes(dgram.data, dgram.data_len)
                            print('ASCII')
                            dumper.dump_ascii(dgram.data)
                        else:
                            print('NO DATA')
                    elif prot == 17:
                        dgram = UDP_packet(ip_pkt.data)
                        print(f'UDP port {dgram.src} -> {dgram.dst}')
                        dumper.dump_bytes(dgram.data, dgram.data_len)
                    else:
                        dumper.dump_bytes(ip_pkt.data, pkt.data_len)
                else:
                    dumper.dump_bytes(pkt.data, pkt.data_len)


def ip_addr(b: bytes) -> str:
    return f'{b[0]}.{b[1]}.{b[2]}.{b[3]}'


if __name__ == '__main__':
    import dumper
    main()
