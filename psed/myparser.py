
import sys
import tree
from sly import Parser
from lexer import PsedLexer

class PsedParser(Parser):
    # debugfile = 'parser.out'

    tokens = PsedLexer.tokens

    def error(self, p):
        if not p:
            print("parse error: unexpected EOF", file=sys.stderr)
        else:
            print("parse error", p)
        sys.exit(1)

#---- program -> stmts

    @_('stmts')
    def program(self, p):
        return tree.to_list(p.stmts)
        # return p.stmts

#---- stmts -> alist | alist stmts

    @_('alist')
    def stmts(self, p):
        return (p.alist, None)

    # @_('stmt SEMI stmts')
    @_('alist stmts')
    def stmts(self, p):
        return (p.alist, p.stmts)

#---- stmt -> alist | null

    # @_('alist')
    # def stmt(self, p):
        # return tree.to_list(p.alist)

    # @_('empty')
    # def stmt(self, p):
        # pass

#----

    @_('')
    def empty(self, p):
        pass

#---- alist -> ( forms )

    @_('LPAREN forms RPAREN')
    def alist(self, p):
        return tree.to_list(p.forms)

#---- forms -> form forms | null

    @_('empty')
    def forms(self, p):
        pass

    @_('form forms')
    def forms(self, p):
        return (p.form, p.forms)


#---- form -> ID | NUMBER | STRING | alist

    # @_('ID', 'NUMBER', 'STRING', 'alist')
    @_('alist')
    def form(self, p):
        # print("form -> alist", p.alist)
        # return tree.to_list(p.alist)
        return p.alist

    @_('ID')
    def form(self, p):
        return ('ID', p.ID)

    @_('NUMBER')
    def form(self, p):
        return p.NUMBER

    @_('STRING')
    def form(self, p):
        return p.STRING[1:-1] # strip off the quotes


def main():
    lexer = PsedLexer()
    parser = PsedParser()

    # text = '(test 1  "2"  3)'
    text = '(test 1  "2"  3 abc); (act (a4 5)  6)'
    result = parser.parse(lexer.tokenize(text))
    print(result)
    # print(len(result))


if __name__ == '__main__':
    main()
