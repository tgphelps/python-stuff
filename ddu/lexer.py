
import re
from typing import List, Tuple, Dict, Generator

# -----------------


class Token():
    """ A token representing a chunk of input text.

        Contains the token type, value and position.
    """

    def __init__(self, typ: str, val='', pos=0):
        self.type = typ
        self.val = val
        self.val_int: int
        self.pos = pos

    def __str__(self) -> str:
        return f"<{self.type}:'{self.val}':{len(self.val)}>"

    def iseof(self):
        return True if self.type == EOF else False


EOF = '<eof>'
EOF_TOKEN = Token(EOF)


class LexerError(Exception):
    """ Lexer error exception.

        pos: Position in the input line where the error occurred.
    """

    def __init__(self, pos):
        self.pos = pos


class Lexer():
    """ A simple regex-based lexer/tokenizer."""

    def __init__(self, rules: List[Tuple[str, str]],
                 keywords: List[str],
                 skip_whitespace=True):
        """ Create a lexer.

            rules:
                A list of rules. Each rule is a (regex, type)
                pair, where 'regex' is the regular expression used
                to recognize the token and 'type' is a string denoting
                the type of the token to return when it's recognized.
            skip_whitespace:
                If True, leading whitespace will be skipped
                before looking for a token.
            keywords:
                List of tokens which should have token.type
                set to the keyword itself, instead of a more
                general type, like 'identifier'.
                WARNING: Every keyword must be matched by some rule.
        """
        # All the regexes are concatenated into a single one
        # with named groups. Since the group names must be valid
        # Python identifiers, but the token types used by the
        # user are arbitrary strings, we auto-generate the group
        # names and map them to token types.
        #

        self.buf: str
        self.pos: int
        self.get_text: Generator[str, None, None]
        self.keywords = keywords
        self.skip_whitespace = skip_whitespace
        self.re_whitespace = re.compile('\\S')
        idx = 1
        regex_parts: List[str] = []
        self.group_type: Dict[str, str] = {}

        for idx, pair in enumerate(rules, start=1):
            regex = pair[0]
            typ = pair[1]
            grp = f'G{idx}'
            regex_parts.append(f'(?P<{grp}>{regex})')
            self.group_type[grp] = typ

        self.regex = re.compile('|'.join(regex_parts))
        # print('Full regex:', self.regex)

    def _token(self) -> Token:
        """ Return the next token (a 'n object) found in the input buffer.

            The EOF token is returned when the end of the
            buffer was reached, and on any following calls.
            In case of a lexing error (the current chunk of the
            buffer matches no rule), a LexerError is raised with
            the position of the error.
        """
        if self.pos >= len(self.buf):
            try:
                text = next(self.get_text)
                self.buf = text
                self.pos = 0
                return self._token()  # restart
            except StopIteration:
                return EOF_TOKEN
        else:
            if self.skip_whitespace:
                m = self.re_whitespace.search(self.buf, self.pos)
                if m:
                    self.pos = m.start()
                else:
                    try:
                        text = next(self.get_text)
                        self.buf = text
                        self.pos = 0
                        return self._token()  # restart
                    except StopIteration:
                        return EOF_TOKEN

            m = self.regex.match(self.buf, self.pos)
            if m:
                g = m.lastgroup
                assert g
                tok_type = self.group_type[g]
                tok = Token(tok_type, m.group(g), self.pos)
                self.pos = m.end()
                if tok.val in self.keywords:
                    tok.type = tok.val
                return tok

            # if we're here, no rule matched
            raise LexerError(self.pos)

    def next_token(self) -> Token:
        """Return the next 'real' token, ignoring any 'ignore' tokens."""
        while True:
            tok = self._token()
            if tok is None:
                # Can this happen?
                assert False
                break
            if tok.type != 'ignore':
                break
        return tok

    # def set_input(self, text: str) -> None:
        # """Use 'text' for subsequent token scans."""
        # self.buf = text
        # self.pos = 0

    # def tokenize(self, buf: str) -> Generator[Token, None, None]:
        # """ Returns an iterator to the tokens found in the buffer."""
        # self.buf = buf
        # self.pos = 0
        # while True:
        #     tok = self.next_token()
        #     if not tok:
        #         break
        #     yield tok

    def flush(self) -> None:
        """Discard all text that has been sent to the lexer."""
        self.buf = ''
        self.pos = 0

    def curr_buff(self) -> str:
        return self.buf

    def start(self, get_text: Generator[str, None, None]) -> None:
        self.get_text = get_text
        # text = next(self.get_text)
        # if text:
        #     self.buf = text
        # else:
        #     self.buf = ''
        self.buf = ''
        self.pos = 0

# ------------------------------------- end of lexer code


rules = [
    ('\\d+',             'INT'),
    ('[a-zA-Z][a-zA-Z0-9_]*',    'ID'),
    ('\\+',              'PLUS'),
    ('\\-',              'MINUS'),
    ('\\*',              'MULT'),
    ('\\/',              'DIV'),
    ('\\(',              'LP'),
    ('\\)',              'RP'),
    ('=',               'EQ'),
    (r"'(\\.|[^\'])*'", 'STR'),
    ('#.*',             'ignore')
]

real_token = {
        'q': 'quit'
        }

keywords = ['if', 'then', 'else', 'quit', 'q']


def fixup_token(tok: Token) -> None:
    if tok.type in real_token:
        tok.type = real_token[tok.type]
    if tok == 'INT':
        tok.val_int = int(tok.val)
    if tok == 'STR':
        # Strip off the quotes
        tok.val = tok.val[1:-1]


def get_text() -> Generator[str, None, None]:
    """Send another chunk of text to the lexer."""
    global last_line
    for line in code:
        last_line = line
        yield line


last_line = ''

code = ['erw = abc8 + 12*(R4-623902)  ',
        " 'abc' 'a\\bc'",
        r" 'a\'bc'",
        'if ifa == b then a=5 else a = 0',
        '  % ',
        'quit q # this is a comment'
        ]

if __name__ == '__main__':

    lex = Lexer(rules, keywords, skip_whitespace=True)
    lex.start(get_text())
    while True:
        try:
            tok = lex.next_token()
            if tok.iseof():
                break
            fixup_token(tok)
            print(tok)
        except LexerError as err:
            print(f'LexerError at position {err.pos}')
            print(last_line)
            print(' ' * (err.pos - 1), '^')
            lex.flush()
        print('------------------')
