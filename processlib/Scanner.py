import re
from typing import NamedTuple

from processlib.Token import ScannerToken, TokenType


class ContextEndedError(Exception):

    def __init__(self, excepted, message='掃描器已經到內容尾端了') -> None:
        super().__init__(('' if excepted is None else '預期 ' + repr(excepted) + ' 但是') + message)


class UnExceptedTokenError(Exception):
    def __init__(self, unexpected: 'UnExceptedToken', content, message=None) -> None:
        lines = content.split('\n')
        line_number_width = len(str(unexpected.line + 1))
        preview = ('...',
                   (str(unexpected.line - 1).ljust(line_number_width) + '| ' + lines[unexpected.line - 2]) if len(
                       lines) > (
                                                                                                                      unexpected.line - 2) >= 0 else '',
                   str(unexpected.line).ljust(line_number_width) + '| ' + lines[unexpected.line - 1],
                   '>'.ljust(line_number_width) + '| ' + ' ' * (unexpected.position - 1) + '^',
                   (str(unexpected.line + 1).ljust(line_number_width) + '| ' + lines[unexpected.line]) if len(
                       lines) > unexpected.line else '',
                   '...')
        preview = '\n'.join((line for line in preview if line != ''))
        super().__init__(
            '於{}:{}預期 {} 但沒有遇到符合的內容:\n{}'.format(unexpected.line, unexpected.position,
                                                 repr(unexpected.expected), preview) + (
                '，' + message if message is not None else ''))


UnExceptedToken = NamedTuple('UnExceptedToken', (('expected', str), ('line', int), ('position', int)))


class Scanner:
    TOKEN_TYPES = [
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
    TOKEN_REGEX = '|'.join(('(?P<{}>{})'.format(token_kind.name, token_kind.regex) for token_kind in TOKEN_TYPES))

    def __init__(self) -> None:
        super().__init__()
        self.content = None
        self.context = None
        self.next_token: ScannerToken = None
        self.ended = False

    def _generator(self, regex: str, content: str) -> ScannerToken:
        line = 1
        next_token_pos = 1
        for find in re.finditer(regex, content):
            kind = find.lastgroup
            value = find.group(kind)
            if kind == 'NEWLINE':
                line += 1
                next_token_pos = 1
            else:
                next_token_pos += len(value)

            if kind == 'SPACE' or kind == 'NEWLINE':
                continue
            if kind == 'OTHER':
                raise RuntimeError('未知類型token:{}'.format(value))
            yield ScannerToken(kind,
                               value, line, next_token_pos - len(value))

    def is_next(self, token: str) -> bool:
        if self.next_token.type != token and token != self.next_token.value:
            return False
        elif self.ended is True:
            raise ContextEndedError()
        return True

    def get_next(self, token: str) -> ScannerToken:
        try:
            if self.next_token.type != token and token != self.next_token.value:
                # raise RuntimeError('預期{}但得到{}\n{}\n{}^'.format(token,
                #                                                self.next_token,
                #                                                self.content.split('\n')[self.next_token.line - 1],
                #                                                ' ' * (self.next_token.position - 1)))
                raise UnExceptedTokenError(UnExceptedToken(token, self.next_token.line, self.next_token.position),
                                           self.content)
            elif self.ended is True:
                raise ContextEndedError()

            token = self.next_token
            self.next_token = next(self.context)

        except StopIteration:
            self.ended = True
        return token

    def is_end(self):
        return self.ended

    def set(self, content):
        self.content = content
        self.context = self._generator(Scanner.TOKEN_REGEX, content)
        self.next_token: ScannerToken = next(self.context)
        self.ended = False


class BNFScanner:

    def __init__(self) -> None:
        super().__init__()
        self.content = None
        self.context = None

    def _generator(self, content):
        request, step_mode = None, None
        result = None
        end = False
        line = 1
        current_token_pos = 1
        next_token_pos = 1
        while content != '' or end:
            request, step_mode = yield \
                UnExceptedToken(request, line, next_token_pos) if result is None else ScannerToken(None, result, line,
                                                                                                   current_token_pos)
            if end:
                return
            # 處理空格與換行
            while True:
                find = re.match('(\n+)|(\r+)|( +)', content)
                if find is None:
                    break

                content = content[find.end():]
                next_token_pos += find.end()
                if find is not None and '\n' in find.group(0):
                    current_token_pos = next_token_pos = 1
                    line += 1
            # 處理請求
            find = re.match(request, content)
            if find is None:
                result = None
                continue

            result = find.group(0)
            if step_mode:
                # 步進模式將會將內容截短
                content = content[find.end():]
                current_token_pos = next_token_pos
                next_token_pos += find.end()

                if len(content) is 0:
                    end = True

    def is_next(self, request, re_mode=False):
        if self.is_end():
            raise ContextEndedError(request)
        if re_mode is False:
            request = re.escape(request)
        # else:
        #     spl = re.split('(\[|\])', request)
        #     indices = [i for i, x in enumerate(spl) if x == "["]
        #     for i in indices:
        #         spl[i + 1] = re.escape(spl[i + 1])
        #     request = ''.join(spl)
        result = self.context.send((request, False))
        if isinstance(result, UnExceptedToken):
            return False
        return True

    def get_next(self, request, re_mode=False):
        if self.is_end():
            raise ContextEndedError(request)
        if re_mode is False:
            request = re.escape(request)
        # else:
        #     spl = re.split('(\[|\])', request)
        #     indices = [i for i, x in enumerate(spl) if x == "["]
        #     for i in indices:
        #         spl[i + 1] = re.escape(spl[i + 1])
        #     request = ''.join(spl)
        result = self.context.send((request, True))
        if isinstance(result, UnExceptedToken):
            raise UnExceptedTokenError(result, self.content)

        return result

    def is_end(self):
        try:
            self.context.send(('', False))
        except StopIteration:
            return True
        return False

    def set(self, content):
        self.content = content
        self.context = self._generator(content)
        # 初始化產生器
        next(self.context)


if __name__ == '__main__':
    scanner = BNFScanner()
    # scanner.set(' asd 123 asf')
    # print(scanner.is_next('asd'))
    # print(scanner.is_next('123'))
    # print(scanner.get_next('123'))
    # print(scanner.get_next('asd'))
    # print(scanner.get_next(' '))
    # print(scanner.get_next('123'))
    # print(scanner.get_next(' '))
    # print(scanner.get_next('asf'))
    # print(scanner.is_end())

    scanner.set('\n  \n asd 123 asf\n af asd s')
    print(scanner.is_next('asd'))
    print(scanner.is_next('123'))
    print(scanner.is_next('123'))
    print(scanner.get_next('[a-z]*', re_mode=True))
    # print(scanner.get_next(' '))
    print(scanner.get_next('[0-9]*', re_mode=True))
    # print(scanner.get_next(' '))
    print(scanner.get_next('[a-z]*', re_mode=True))
    print(scanner.get_next('[a-z]*', re_mode=True))
    print(scanner.get_next('[a-z]*', re_mode=True))
    print(scanner.get_next('[0-9]+', re_mode=True))
    print(scanner.get_next('[a-z]*', re_mode=True))
    print(scanner.is_end())
