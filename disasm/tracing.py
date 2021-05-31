
from typing import Optional, Set, IO, Any
import sys
import dumper


class Globals:
    # fp: Optional[TextIO]
    fp: Optional[IO[Any]]
    traces: Set[str]
    max_size: int
    cur_size: int
    dumper: dumper.Hexdump


g = Globals()
g.fp = None
g.traces = set()
g.max_size = 100000
g.cur_size = 0


def trace_open(fname: str, mode='wt') -> None:
    "If the trace file isn't already open, open it and disable all traces."
    if g.fp is None:
        g.fp = open(fname, mode)
        g.traces = set()
        g.traces.add('always')
        trace('always', 'trace file open')
    else:
        print('trace file already open', file=sys.stderr)


def trace_close() -> None:
    "If the trace file is open, close it."
    if g.fp:
        trace('always', 'trace file close')
        g.fp.close()


def trace_on(tp: str) -> None:
    "Enable trace point."
    g.traces.add(tp)


def trace_off(tp: str) -> None:
    "Disable trace point."
    g.traces.discard(tp)


def trace_max_size(n: int) -> None:
    "Set the max trace file entries we will allow."
    g.max_size = n


# def trace_flush() -> None:


def tracing(tp: str) -> bool:
    "Return status of a trace point."
    if tp in g.traces:
        return True
    else:
        return False


LINESIZE = 16


def _trace_buff(buff: bytes, size: int, dumper: dumper.Hexdump) -> None:
    "Print one buffer of the file, in lines of LINESIZE bytes."
    offset = 0
    while size:
        this = min(size, LINESIZE)
        print(dumper.dump(buff[offset: offset+this]), file=g.fp)
        offset += this
        size -= this
        assert size >= 0


def trace(tp: str, msg: str, buff=b'') -> None:
    "Write a trace entry."
    if g.fp:
        if g.cur_size < g.max_size:
            g.cur_size += 1
            print(f'{tp}:{msg}', file=g.fp)
            if buff != b'':
                g.dumper = dumper.Hexdump()
                _trace_buff(buff, len(buff), g.dumper)
            if g.cur_size >= g.max_size:
                print('max trace entries', file=g.fp)
                trace_close()


def trace_if(tp: str, msg: str, buff=b'') -> None:
    "Write a trace entry, if the trace point is enabled."
    if g.fp and tp in g.traces:
        # print(f'{tp}:{msg}', file=g.fp)
        trace(tp, msg, buff)


# ---------- test code

def main() -> None:
    trace_open("TRACE.txt")
    trace_max_size(5)
    if tracing('always'):
        trace('always', 'good one')
    trace_on('not')
    trace_if('not', 'good one')
    trace_off('not')
    trace_if('not', 'bad one')
    trace_if('always', 'buffer', b'abcdefghijklmnopqrst')
    trace_close()


if __name__ == '__main__':
    main()
