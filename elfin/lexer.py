
# type: ignore
# flake8: noqa

from sly import Lexer


class ElfLexer(Lexer):
    tokens = {ID, PRINT, DUMP, QUIT, HELP, HDR, PHT, SHT, STR, NUMBER}

    ignore = ' \t'

    ID = r'[a-zA-Z][a-zA-z0-9]*'

    @_(r'0[0-9a-fA-F]+',
       r'\d+')
    def NUMBER(self, t):
        "Return int value, base 10 or 16."
        if t.value.startswith('0'):
            t.value = int(t.value, 16)
        else:
            t.value = int(t.value)
        return t

    ID['p'] = PRINT
    ID['d'] = DUMP
    ID['q'] = QUIT
    ID['help'] = HELP
    ID['hdr'] = HDR
    ID['pht'] = PHT
    ID['sht'] = SHT
    ID['str'] = STR

    def error(self, t):
        print(f"Illegal character {t.value[0]}")
        self.index += 1


def main():
    data = [
        "p hdr",
        "d pht",
        "p sht",
        "q",
        "help",       
        "d 07f 999"
        ]
    lexer = ElfLexer()
    for s in data:
        for tok in lexer.tokenize(s):
            print('type=%r, value=%r, type=%r' %
                  (tok.type, tok.value, type(tok.value)))


if __name__ == '__main__':
    main()
