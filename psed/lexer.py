
from sly import Lexer

class PsedLexer(Lexer):
    tokens = {ID, NUMBER, STRING, LPAREN, RPAREN}

    ignore = ' \t\n'

    ID      = r"[a-zA-Z_!+\-<>@#$%&*=':/?][a-zA-Z0-9_!+\-<>@#$%&*=':/?]*"
    STRING  = r'"(\\.|[^\"])*"'
    LPAREN  = r'\('
    RPAREN  = r'\)'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    ignore_newline = r'\n+'
    ignore_comment = r';.*'
    # ignore_comment = r';'


def main():
    data = r'''(< 1 2) (abc? de$ "abc") ; comment
                1 2'''
    # data = r"<"
    lexer = PsedLexer()
    for tok in lexer.tokenize(data):
        print('type=%r, value=%r' % (tok.type, tok.value))

if __name__ == "__main__":
    main()
