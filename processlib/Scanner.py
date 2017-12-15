import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value'])
TokenType = namedtuple('TokenType', ['name', 'regex'])


class Scanner:
    token_kinds = [
        TokenType('KEYWORD', r'for|return'),
        TokenType('NUMBER', r'[0-9]+'),
        TokenType('ASSIGN', r'='),
        TokenType('END', r';'),
        TokenType('SYMBOL', r'[(){}]'),
        TokenType('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
        TokenType('UnaryOP', r'--|\+\+'),
        TokenType('OP', r'[+\-*/]'),
        TokenType('COND', r'==|!=|<=|>=|<|>'),
        TokenType('NEWLINE', r'\r\n|\n'),
        TokenType('SPACE', r'[ \t]+'),
        TokenType('OTHER', r'.')
    ]
    token_regex = '|'.join(('(?P<{}>{})'.format(token_kind.name, token_kind.regex) for token_kind in token_kinds))

    def __init__(self, content: str) -> None:
        super().__init__()
        self.context = self._generator(Scanner.token_regex, content)
        self.next_token = next(self.context)
        self.ended = False

    def _generator(self, regex, content):
        for find in re.finditer(regex, content):
            token_kind = find.lastgroup
            token = find.group(token_kind)
            if token_kind == 'SPACE' or token_kind == 'NEWLINE':
                continue
            if token_kind == 'OTHER':
                raise RuntimeError('未知類型token:{}'.format(token))
            yield Token(next(token_type for token_type in Scanner.token_kinds if token_type.name == token_kind),
                        token)

    def is_next(self, token: str):
        if self.next_token.type.name != token and token != self.next_token.value:
            return False
        elif self.ended is True:
            raise RuntimeError('已經讀到文件結尾了')
        return True

    def get_next(self, token: str):
        # token = None
        try:
            if self.next_token.type.name != token and token != self.next_token.value:
                raise RuntimeError('預期{}但得到{}'.format(token, self.next_token))
            elif self.ended is True:
                raise RuntimeError('已經讀到文件結尾了')

            token = self.next_token
            self.next_token = next(self.context)

        except StopIteration:
            self.ended = True
        return token

    def is_end(self):
        return self.ended
