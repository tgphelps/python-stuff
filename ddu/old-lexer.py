
# type: ignore

from sly import Lexer # type:ignore

class DduLexer(Lexer):
    tokens = {ID, STRING, LIST, FIND, USE, BACKUPS, SET, DESTINATION,
              HELP, RESTORE, QUIT, INFO, FILES, FROM, TO}

    # ignore space and tab
    ignore = ' \t'

    ID = r'[a-zA-Z][a-zA-z0-9]*'

    ID['list'] = LIST
    ID['find'] = FIND
    ID['info'] = INFO
    ID['help'] = HELP
    ID['from'] = FROM
    ID['to'] = TO
    ID['files'] = FILES
    ID['quit'] = QUIT
    ID['q'] = QUIT
    ID['use'] = USE
    ID['backups'] = BACKUPS
    ID['set'] = SET
    ID['destination'] = DESTINATION
    ID['restore'] = RESTORE

    STRING = r"'(\\.|[^\'])*'"

    ignore_comment = r'#.*'

    def error(self, t):
        print(f'Illegal character {t.value[0]}')
        self.index += 1


def main():
    data = [
            r"list backups"
           ,r"list 'abc' "
           ,r"use backup bkup_123"
           ,r"set destination 'abc'"
           ,r"restore '*' from 'here'"
           ,r"list 'aa\'bc' "
           ,r"list 'aa\bc' "
           ]

    lexer = DduLexer()
    for s in data:
        for tok in lexer.tokenize(s):
            print('type=%r, value=%r, len=%r' % (tok.type, tok.value, len(tok.value)))
        print()

if __name__ == '__main__':
    main()
