
import sys
from typing import Any, Tuple, Generator

from lexer import Lexer, LexerError, Token
# import log

ERROR = Token('<error>')
# EOF = Token('<eof>')
INVALID = (None,)

lexer_rules = [
    ('[a-zA-Z][a-zA-Z0-9_]*',    'ID'),
    (r"'(\\.|[^\'])*'",         'STR'),
    ('<end>',                   '<end>'),
    ('#.*', 'ignore')
]

aliases = {
        'q': 'quit'
        }

keywords = ['list', 'find', 'info', 'help', 'from', 'quit', 'q',
            'to', 'files', 'use', 'set', 'backups', 'destination', 'restore'
            ]

# -----------------


class Globals:
    # last_stmt: str
    token: Token
    prev_token: Token
    lex: Lexer
    quit: bool


g = Globals()
g.token = ERROR

# -----------------


def get_next_token() -> None:
    """Sets g.token to the next token from the stream.

    If a lexical error occurs, set g.token to the 'error' token.
    """
    try:
        g.prev_token = g.token
        g.token = g.lex.next_token()
        # log.log(f'next token: {g.token}')
        if not g.token.iseof():
            fixup_token(g.token)
        # log.log(f'token after fixup: {g.token}')
    except LexerError as err:
        print(f'LexerError at position {err.pos}')
        # print(g.last_stmt)
        print(g.lex.curr_buff())
        print(' ' * (err.pos-1), '^')
        g.token = ERROR


def parse_error(msg: str) -> None:
    """Print a parsing error message."""
    print('ERROR:', msg, file=sys.stderr)


def accept(tok: str) -> bool:
    """If g.token matches 'tok', get the next token and return True."""
    # log.log(f'accept {tok}')
    if g.token.type == tok:
        # log.log('YES')
        get_next_token()
        return True
    else:
        # log.log('NO')
        return False


def expect(tok: str) -> bool:
    """If g.token matches 'tok', get another one. Else ERROR."""
    # log.log(f'expect {tok}')
    if accept(tok):
        return True
    else:
        parse_error(f'Expecting {tok}, got {g.token})')
        # print(g.last_stmt)
        print(g.lex.curr_buff())
        print(' ' * (g.token.pos-1), '^')
        return False

# -----------------


def read_statement() -> Generator[str, None, None]:
    """Read a complete statement from stdin.

    The  statement may extend over several lines by ending all lines
    except the last one with a backslash.
    """
    stmt = ''
    prompt = '-> '
    while True:
        try:
            line = input(prompt)
        except EOFError:
            line = 'q'
        if line.endswith('\\'):
            stmt += ' ' + line[0:-1]
            prompt = '** '
        else:
            stmt += ' ' + line
            break
    # g.last_stmt = stmt
    result = stmt + ' <end>'
    yield result


def fixup_token(tok: Token) -> None:
    """Adjust the token to make it easier to work with.

        1. If the token is a keyword that is aliased to another one,
           change it to be the real one.
        2. If it's an 'INT', store the integer value in the token.
        3. If it's an 'STR', strip off the quotes at either end of the string.
    """
    if tok.type in aliases:
        tok.type = aliases[tok.type]
    if tok.type == 'INT':
        tok.val_int = int(tok.val)
    if tok.type == 'STR':
        # Strip off the quotes
        tok.val = tok.val[1:-1]


def execute(ast: Tuple[Any, ...]) -> None:
    """Execute the ast. If it's a 'quit' command, set the quit flag."""
    cmd = ast[0]
    if cmd == 'QUIT':
        g.quit = True
    elif cmd == 'HELP':
        print('help message...')
    elif cmd == 'INFO':
        print('print info here')
    elif cmd == 'USE':
        print(f'using {ast[1]}')
    elif cmd == 'FIND':
        print(f'finding {ast[1]}')
    elif cmd == 'LIST_FILES':
        print('listing files')
    elif cmd == 'LIST_BACKUPS':
        print('listing backups}')
    elif cmd == 'LIST':
        print(f'listing {ast[1]}')
    elif cmd == 'RESTORE':
        print(f'listing {ast[1]}')
    else:
        print(f'unknown: {ast}')

# -----------------


def info() -> Tuple[Any, ...]:
    # log.log('info stmt')
    return ('INFO', None)


def help() -> Tuple[Any, ...]:
    # log.log('help stmt')
    return ('HELP', None)


def quit() -> Tuple[Any, ...]:
    # log.log('quit stmt')
    return ('QUIT', None)


def find() -> Tuple[Any, ...]:
    """FIND string"""
    # log.log('find stmt')
    if expect('STR'):
        return ('FIND', g.prev_token.val)
    else:
        parse_error('Should be: find string')
        return INVALID


def use() -> Tuple[Any, ...]:
    """USE ID"""
    # log.log('use stmt')
    if expect('ID'):
        return ('USE', g.prev_token.val)
    else:
        parse_error('Should be: use backup-name')
        return INVALID


def set() -> Tuple[Any, ...]:
    """SET DESTINATION string"""
    # log.log('set stmt')
    if expect('destination'):
        if expect('STR'):
            return ('SET_DEST', g.prev_token.val)
        else:
            parse_error('Should be: set destination string')
            return INVALID
    else:
        return INVALID


def list_arg() -> Tuple[Any, ...]:
    """FILES | BACKUPS | string"""
    # log.log('list_arg stmt')
    if accept('files'):
        return ('LIST_FILES', None)
    elif accept('backups'):
        return ('LIST_BACKUPS', None)
    elif accept('STR'):
        return ('STR', g.prev_token.val, None)
    else:
        # flush_tokens()
        return INVALID


def list() -> Tuple[Any, ...]:
    """LIST list_arg"""
    # log.log('list stmt')
    result = list_arg()
    if result == INVALID:
        return INVALID
    else:
        if result[0] == 'STR':
            return ('LIST', result[1])
        else:
            return result


def from_clause() -> Tuple[Any, ...]:
    """"FROM STR | NULL"""
    if accept('from'):
        if expect('ID'):
            return ('FROM', g.prev_token.val)
        else:
            # log.log('FROM path invalid. Should be: from string', show=True)
            return INVALID
    else:
        return ('FROM', '')


def to_clause() -> Tuple[Any, ...]:
    """"TO STR | NULL"""
    if accept('to'):
        if expect('STR'):
            return ('TO', g.prev_token.val)
        else:
            # log.log('TO path invalid. Should be: to string', show=True)
            return INVALID
    else:
        return ('TO', '')


def restore() -> Tuple[Any, ...]:
    """RESTORE string from_clause to_clause"""
    if expect('STR'):
        path = g.prev_token.val
        fromm = from_clause()
        if fromm == INVALID:
            return INVALID
        else:
            to = to_clause()
            if to == INVALID:
                return INVALID
            else:
                return ('RESTORE', path, fromm, to)
    else:
        # log.log('invalid restore pattern')
        return INVALID


def statement() -> Tuple[Any, ...]:
    """One of the statement types, followed by '<end>'."""
    # log.log('statement')
    if accept('quit'):
        result = quit()
    elif accept('help'):
        result = help()
    elif accept('info'):
        result = info()
    elif accept('use'):
        result = use()
    elif accept('set'):
        result = set()
    elif accept('find'):
        result = find()
    elif accept('list'):
        result = list()
    elif accept('restore'):
        result = restore()
    else:
        parse_error('invalid statement')
        result = INVALID

    if result == INVALID:
        # flush_tokens()
        return INVALID

    if expect('<end>'):
        return result
    else:
        # flush_tokens()
        return INVALID


def init() -> None:
    g.lex = Lexer(lexer_rules, keywords, skip_whitespace=True)


def run(gen: Generator[str, None, None]) -> Tuple[Any, ...]:
    g.lex.start(gen)
    get_next_token()
    return statement()

# -----------------


def main() -> None:
    try:
        # log.log_open()
        init()
        g.quit = False
        while True:
            # g.lex.start(read_statement())
            # get_next_token()
            ast = run(read_statement())
            if ast[0]:
                print(f'ast: {ast}')
                execute(ast)
                if g.quit:
                    break
        print('done')
    finally:
        pass
        # log.log_close()


if __name__ == '__main__':
    main()
