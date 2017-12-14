import re
from collections import namedtuple



Token = namedtuple('Token', ['type', 'value'])
TokenType = namedtuple('TokenType', ['name', 'alias'])


class Scanner:
    token_kinds = [
        ('KEYWORD', r'for|return', ('for', 'return')),
        ('NUMBER', r'[0-9]+', ()),
        ('ASSIGN', r'=', ('=',)),
        ('END', r';', (';',)),
        ('SYMBOL', r'[(){}]', ('(', ')', '{', '}')),
        ('ID', r'[A-Za-z_][A-Za-z0-9_]*', ()),
        ('UnaryOP', r'--|\+\+', ()),
        ('OP', r'[+\-*/]', ()),
        ('COND', r'==|!=|<=|>=|<|>', ()),
        ('NEWLINE', r'\n', ()),
        ('SPACE', r'[ \t]+', ()),
        ('OTHER', r'.', ())
    ]
    token_regex = '|'.join(('(?P<{}>{})'.format(*token_kind) for token_kind in token_kinds))

    def __init__(self, content: str) -> None:
        super().__init__()
        self.context = self._generator(Scanner.token_kinds, content)
        self.next_token = next(self.context)
        self.ended = False

    def _generator(self, regex, content):
        for find in re.finditer(Scanner.token_regex, content):
            token_kind = find.lastgroup
            token = find.group(token_kind)
            if token_kind == 'SPACE' or token_kind == 'NEWLINE':
                continue
            if token_kind == 'OTHER':
                print('未知類型token:{}'.format(token))
            yield Token(TokenType(token_kind,
                                  next(token_type for token_type in Scanner.token_kinds if token_type[0] == token_kind)[
                                      2]),
                        token)

    def is_next(self, token_type: str):
        if self.next_token.type.name != token_type and token_type not in self.next_token.type.alias:
            return False
        elif self.ended is True:
            raise RuntimeError('已經讀到文件結尾了')
        return True

    def get_next(self, token_type: str):
        token = None
        try:
            if self.next_token.type.name != token_type and token_type not in self.next_token.type.alias:
                print('預期{}但得到{}'.format(token_type, self.next_token))
            elif self.ended is True:
                raise RuntimeError('已經讀到文件結尾了')

            token = self.next_token
            self.next_token = next(self.context)

        except StopIteration:
            self.ended = True
        return token

    def is_end(self):
        return self.ended
