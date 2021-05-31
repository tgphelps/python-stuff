
# type: ignore

from sly import Parser # type: ignore
from lexer import DduLexer # type: ignore

import util

class DduParser(Parser):
    # debugfile = 'parser.out'

    tokens = DduLexer.tokens

    def error(self, p):
        if not p:
            util.msg('parse error: unexpected EOF')
        else:
            util.msg(f'parse error: {p}')

    @_('list_stmt')
    def stmt(self, p):
        return p.list_stmt

    @_('find_stmt')
    def stmt(self, p):
        return p.find_stmt

    @_('use_stmt')
    def stmt(self, p):
        return p.use_stmt

    @_('set_stmt')
    def stmt(self, p):
        return p.set_stmt

    @_('restore_stmt')
    def stmt(self, p):
        return p.restore_stmt

    @_('quit_stmt')
    def stmt(self, p):
        return p.quit_stmt

    @_('info_stmt')
    def stmt(self, p):
        return p.info_stmt

    @_('help_stmt')
    def stmt(self, p):
        return p.help_stmt

# ----------


    @_('LIST BACKUPS')
    def list_stmt(self, p):
        return ('LIST_BACKUPS', None)

    @_('LIST STRING')
    def list_stmt(self, p):
        return ('LIST', p.STRING[1:-1])

    @_('LIST FILES')
    def list_stmt(self, p):
        return ('LIST_FILES', None)

    @_('FIND STRING')
    def find_stmt(self, p):
        return ('FIND', p.STRING[1:-1])

    @_('USE ID')
    def use_stmt(self, p):
        return ('USE', p.ID)

    @_('SET DESTINATION STRING')
    def set_stmt(self, p):
        return ('SET_DEST', p.STRING[1:-1])

    @_('RESTORE STRING from_clause to_clause')
    def restore_stmt(self, p):
        return ('RESTORE', p.STRING[1:-1], p.from_clause, p.to_clause)

    @_('QUIT')
    def quit_stmt(self, p):
        return ('Q', None)

    @_('INFO')
    def info_stmt(self, p):
        return ('INFO', None)

    @_('HELP')
    def help_stmt(self, p):
        return ('HELP', None)

    @_('FROM ID')
    def from_clause(self, p):
        return ('FROM', p.ID)

    @_('empty')
    def from_clause(self, p):
        return ('FROM', '')

    @_('TO STRING')
    def to_clause(self, p):
        return ('TO', p.STRING[1:-1])

    @_('empty')
    def to_clause(self, p):
        return ('TO', '')

    @_('')
    def empty(self, p):
        pass

def main():
    lexer = DduLexer()
    parser = DduParser()

    test_data = [
             'list backups'
            ,"list 'abc'"
            ,'use bkup_1'
            ,"set destination 'mydest'"
            ,"restore '*py$'"
            ,"restore '*py$' from bkup"
            ,"restore '*py$'           to 'abc' "
            ,"restore '*py$' from bkup to 'abc' "
            ,'quit'
            ]

    for line in test_data:
        result = parser.parse(lexer.tokenize(line))
        print(result)

if __name__ == '__main__':
    main()
