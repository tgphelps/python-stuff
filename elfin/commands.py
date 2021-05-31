
from typing import Tuple, Any

import Elf
import Hex
import lexer
import parser
import util


class Globals:
    elf: Elf.Elf


g = Globals()


def run_cmd(cmd: str, elf: Elf.Elf) -> None:
    g.elf = elf
    if not elf.parse_complete:
        elf.parse()
    lex = lexer.ElfLexer()  # type: ignore
    par = parser.ElfParser()  # type: ignore
    code: Tuple[Any, ...] = par.parse(lex.tokenize(cmd))
    assert code
    handler = code[0]
    args = code[1]
    func[handler](args)


def run(elf: Elf.Elf) -> None:
    g.elf = elf
    g.elf.parse()
    lex = lexer.ElfLexer()  # type: ignore
    par = parser.ElfParser()  # type: ignore
    while True:
        try:
            text = input('cmd > ')
            code: Tuple[Any, ...] = par.parse(lex.tokenize(text))
            if not code:
                continue
            if code[0] == 'quit':
                break
            else:
                print(code)
                handler = code[0]
                args = code[1]
                func[handler](args)
        except EOFError:
            break


def cmd_help(_) -> None:
    print("cmd = help, quit, print, dump")
    print("print_stmt = p hdr | p pht | p sht | p str")
    print("dump = d hdr | d pht # | d sht # | d # #")


def cmd_print(obj: str) -> None:
    print(f"print command: {obj}")
    if obj == 'hdr':
        g.elf.print_elf_hdr()
    elif obj == 'sht':
        for n in range(g.elf.e_shnum):
            print(f"{n}:", g.elf.shent[n])
    elif obj == 'pht':
        for n in range(g.elf.e_phnum):
            print(f"{n}:", g.elf.phent[n])
    elif obj == 'str':
        Hex.dump(g.elf.str_tbl)
    else:
        assert False


def cmd_dump(obj: Any) -> None:
    # obj can be a string or a tuple
    print(f"dump command: {obj}")
    if obj == 'hdr':
        Hex.dump(g.elf.hdr)
    else:
        tbl = obj[0]
        ent = obj[1]
        if tbl == 'sht':
            data = g.elf.get_shent(ent)
            if len(data) == 0:
                util.error("no such SHT entry")
            else:
                Hex.dump(data)
        elif tbl == 'pht':
            data = g.elf.get_phent(ent)
            if len(data) == 0:
                util.error("no such PHT entry")
            else:
                Hex.dump(data)
        else:
            # 'dump range' not implemented yet
            assert False


func = {
        'help': cmd_help,
        'print': cmd_print,
        'dump': cmd_dump
        }
