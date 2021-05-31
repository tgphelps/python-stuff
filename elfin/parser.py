
# type: ignore
# flake8: noqa

from sly import Parser
from lexer import ElfLexer

class ElfParser(Parser):
    tokens = ElfLexer.tokens

    @_('help_stmt',
       'quit_stmt',
       'dump_stmt',
       'print_stmt')
    def stmt(self, p):
        return p[0]

    # XXX: The "HELP ID" is there just to use the ID token, and avoid a warning
    @_('HELP',
       'HELP ID')
    def help_stmt(self, p):
        return (p[0], None)

    @_('QUIT')
    def quit_stmt(self, p):
        return ('quit', None)

    @_('PRINT HDR',
       'PRINT PHT',
       'PRINT STR',
       'PRINT SHT')
    def print_stmt(self, p):
        return ('print', p[1])

    @_('DUMP entry',
       'DUMP range',
       'DUMP HDR')
    def dump_stmt(self, p):
        return ('dump', p[1])

    @_('PHT NUMBER',
       'SHT NUMBER')
    def entry(self, p):
        return (p[0], p[1])

    @_('NUMBER NUMBER')
    def range(self, p):
        return (p[0], p[1])


if __name__ == '__main__':
    lexer = ElfLexer()
    parser = ElfParser()

    while True:
        try:
            text = input('cmd > ')
            result = parser.parse(lexer.tokenize(text))
            print(result)
        except EOFError:
            break
