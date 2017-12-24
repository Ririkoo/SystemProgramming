import re
from typing import List, Union, Dict

from processlib.BNF import RuleType, ModifierType, BNFBaseRule, BNFRule
from processlib.Scanner import Scanner, BNFScanner, ContextEndedError, UnExceptedTokenError
from processlib.Token import TokenType, ScannerToken
from processlib.Tools import TreeTools
from processlib.Tree import Tree

c0_ebnf = '''
PROG = BaseList
BaseList = (BASE)*
BASE = FOR | STMT ';'
FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK
STMT = 'return' id | id ('=' EXP |  ('++'|'--'))
BLOCK = '{' BaseList '}'
EXP = ITEM ([+\-*/] ITEM)?
COND = EXP ('=='|'!='|'<='|'>='|'<'|'>') EXP
ITEM = id | number
id = [A-Za-z_][A-Za-z0-9_]*
number = [0-9]+
'''


class Parser:

    def __init__(self, scanner: Scanner) -> None:
        super().__init__()
        self._scanner: Scanner = scanner
        # self._parsed_tree = self._parse_prog()

    def parse(self, content):
        self._scanner.set(content)
        return self._parse_prog()

    def _parse_prog(self):
        """PROG = BaseList """
        return Tree('PROG').append(self._parse_base_list())

    def _parse_base_list(self):
        """BaseList = (BASE)*"""
        tree = Tree('BaseList')

        while not self._scanner.is_end() and not self._scanner.is_next('}'):
            tree.append(self._parse_base())
        return tree

    def _parse_base(self):
        """BASE = FOR | STMT ';' """
        tree = Tree('BASE')
        if self._scanner.is_next('for'):
            tree.append(self._parse_for())
        else:
            tree.append(self._parse_stmt())
            tree.append(self._scanner.get_next(';'))

        return tree

    def _parse_for(self):
        """FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK """
        tree = Tree('FOR') \
            .append(self._scanner.get_next('for')) \
            .append(self._scanner.get_next('(')) \
            .append(self._parse_stmt()) \
            .append(self._scanner.get_next('END')) \
            .append(self._parse_cond()) \
            .append(self._scanner.get_next('END')) \
            .append(self._parse_stmt()) \
            .append(self._scanner.get_next(')')) \
            .append(self._parse_block())
        return tree

    def _parse_stmt(self):
        """STMT = 'return' id | id '=' EXP | id ('++'|'--') """
        tree = Tree('STMT')
        if self._scanner.is_next('return'):
            tree.append(self._scanner.get_next('return')) \
                .append(self._parse_id())
        else:
            tree.append(self._parse_id())
            if self._scanner.is_next('ASSIGN'):
                tree.append(self._scanner.get_next('ASSIGN')) \
                    .append(self._parse_exp())
            else:
                tree.append(self._scanner.get_next('UnaryOP'))

        return tree

    def _parse_block(self):
        """BLOCK = '{' BaseList '}' """
        tree = Tree('BLOCK') \
            .append(self._scanner.get_next('{')) \
            .append(self._parse_base_list()) \
            .append(self._scanner.get_next('}'))
        return tree

    def _parse_exp(self):
        """EXP = ITEM ([+-*/] ITEM)? """
        tree = Tree('EXP') \
            .append(self._parse_item())
        if self._scanner.is_next('OP'):
            tree.append(self._scanner.get_next('OP')) \
                .append(self._parse_item())
        return tree

    def _parse_cond(self):
        """COND = EXP ('=='|'!='|'<='|'>='|'<'|'>') EXP"""
        tree = Tree('COND') \
            .append(self._parse_exp()) \
            .append(self._scanner.get_next('COND')) \
            .append(self._parse_exp())
        return tree

    def _parse_item(self):
        """ITEM = id | number """
        tree = Tree('ITEM')
        if self._scanner.is_next('ID'):
            tree.append(self._parse_id())
        else:
            tree.append(self._parse_number())
        return tree

    def _parse_id(self):
        """id = [A-Za-z_][A-Za-z0-9_]*"""
        tree = Tree('ID') \
            .append(self._scanner.get_next('ID'))
        return tree

    def _parse_number(self):
        """number = [0-9]+"""
        tree = Tree('Number') \
            .append(self._scanner.get_next('NUMBER'))
        return tree


class ParseError(Exception):

    def __init__(self, unexpected: UnExceptedTokenError) -> None:
        super().__init__(str(unexpected) + '\n已經無法回溯，解析失敗')


class BNFParser:

    def __init__(self, bnf_rules, enter_point: str, scanner: BNFScanner) -> None:
        super().__init__()
        self.last_unexpected_error = None
        self.rules: Dict[str, BNFRule] = self.bnf_parse(bnf_rules)
        self.scanner: BNFScanner = scanner
        self.enter_point: str = enter_point

    TOKEN_TYPES = [
        TokenType('range_token', "(\[.*\](\+|\*)?)+"),
        TokenType('token', r"'[^ ']+'"),
        TokenType('group', r'[()]'),
        TokenType('divider', r'\|'),
        TokenType('other_rules', r'[a-zA-Z]+'),
        TokenType('modifier', r'\+|\*|\?'),
        TokenType('space', r'[ \t]+'),
        TokenType('what_ever', r'.')
    ]
    TOKEN_REGEX = '|'.join(('(?P<{}>{})'.format(token_kind.name, token_kind.regex) for token_kind in TOKEN_TYPES))

    def bnf_parse(self, rules: str):
        rules = rules.strip().split('\n')
        rules = [rule.strip() for rule in rules]
        rules = [[r.strip() for r in rule.split('=', 1)] for rule in rules]
        # 解析成token
        rules = [(rule[0], self.bnf_parse_rule_token(rule[1]), RuleType.normal) for rule in rules]
        # print('\n'.join(str(x) for x in rules))
        # 解析成樹
        rules = self.bnf_parse_rules_tree(rules)
        return rules

    def bnf_parse_rule_token(self, rule: str):
        regex = re.compile(self.TOKEN_REGEX)
        result = []
        for find in re.finditer(regex, rule):
            kind = find.lastgroup
            value = find.group(kind)
            result.append((kind, value))
        return tuple(result)

    def bnf_parse_rules_tree(self, rules):
        internal_rule_tree = {}
        rule_list_tree = {}

        def internal_id_generator():
            x = 0
            while True:
                yield 'internal_' + str(x)
                x += 1

        internal_id = internal_id_generator()

        for rule in rules:
            sub_rules: List[List[BNFBaseRule]] = []
            sub_rule: List[BNFBaseRule] = []
            token_generator = iter(rule[1])
            while True:
                try:
                    token = next(token_generator)

                    if token[0] == 'token':
                        sub_rule.append(BNFBaseRule(RuleType.string, token[1][1:-1], ModifierType.none))
                    elif token[0] == 'range_token':
                        sub_rule.append(BNFBaseRule(RuleType.regex, token[1], ModifierType.none))
                    elif token[0] == 'other_rules':
                        sub_rule.append(BNFBaseRule(RuleType.link, token[1], ModifierType.none))
                    elif token[0] == 'divider':
                        sub_rules.append(sub_rule)
                        sub_rule = []
                    elif token[0] == 'modifier':
                        sub_rule[-1] = sub_rule[-1]._replace(modifier=ModifierType(token[1]))
                    elif token[0] == 'spcae':
                        continue
                    elif token[0] == 'group':
                        depth = 0
                        id = next(internal_id)
                        internal_rule = (id, [], RuleType.internal)
                        while True:
                            if token[0] == 'group':
                                if token[1] == '(':
                                    if depth != 0:
                                        internal_rule[1].append(token)
                                    depth += 1
                                elif token[1] == ')':
                                    depth -= 1
                                    if depth != 0:
                                        internal_rule[1].append(token)
                                if depth == 0:
                                    break
                            else:
                                internal_rule[1].append(token)

                            token = next(token_generator)
                        rules.append(internal_rule)
                        sub_rule.append(BNFBaseRule(RuleType.link, id, ModifierType.none))
                except StopIteration:
                    sub_rules.append(sub_rule)
                    rule_list_tree[rule[0]] = BNFRule(rule[2], rule[0], sub_rules)
                    break

        result = {}
        result.update(rule_list_tree)
        result.update(internal_rule_tree)
        return result

    def parse(self, code):
        self.scanner.set(content=code)
        result = self.parse_tree(self.rules[self.enter_point])
        if not self.scanner.is_end():
            raise self.last_unexpected_error
        return result

    def parse_tree(self, rule: BNFRule):
        tree = Tree(rule.name)
        for sub_rule in rule.sub_rules:
            first_try = True
            next_sub = False
            for token in sub_rule:
                try:
                    if token.modifier is ModifierType.none:
                        result = self.get_token(token)
                        tree.append(result, concat=isinstance(result, Tree) and 'internal' in result.name)
                    elif token.modifier is ModifierType.repeat_what_ever:
                        while True:
                            try:
                                result = self.try_get_token(token)
                            except ContextEndedError:
                                break

                            if result is None:
                                break
                            else:
                                tree.append(result, concat=isinstance(result, Tree) and 'internal' in result.name)
                    elif token.modifier is ModifierType.repeat_once_or_nothing_happened:
                        try:
                            result = self.try_get_token(token)
                        except ContextEndedError:
                            result = None
                        if result is not None:
                            tree.append(result, concat=isinstance(result, Tree) and 'internal' in result.name)
                    elif token.modifier is ModifierType.repeat_more_than_once:
                        result = self.get_token(token)
                        tree.append(result, concat=isinstance(result, Tree) and 'internal' in result.name)
                        while True:
                            try:
                                result = self.try_get_token(token)
                            except ContextEndedError:
                                break
                            if result is None:
                                break
                            else:
                                tree.append(result, concat=isinstance(result, Tree) and 'internal' in result.name)
                except (UnExceptedTokenError, ContextEndedError) as e:
                    self.last_unexpected_error = e
                    if first_try is True:
                        next_sub = True
                        break
                    else:
                        raise ParseError(e)

                # tree.append(result)
                first_try = False
            if next_sub:
                continue

            return tree
        raise self.last_unexpected_error

    def get_token(self, token) -> Union[Tree, ScannerToken]:
        result = None

        if token.type is RuleType.string:
            result = self.scanner.get_next(token.content)
        elif token.type is RuleType.regex:
            result = self.scanner.get_next(token.content, re_mode=True)
        elif token.type is RuleType.link:
            result = self.parse_tree(self.rules[token.content])

        if isinstance(result, Tree) and len(result.children) == 0:
            return None
        if isinstance(result, Tree) and len(result.children) == 1 and \
                isinstance(result.children[0], ScannerToken) and \
                result.children[0].type is None and \
                'internal' not in result.name:
            return result.children[0]._replace(type=result.name)
        return result

    def try_get_token(self, token) -> Union[Tree, ScannerToken]:
        try:
            return self.get_token(token)
        except UnExceptedTokenError:
            pass
        return None

    def process_internal_node(self):
        pass


if __name__ == '__main__':
    bnf_parser = BNFParser(c0_ebnf, 'PROG', BNFScanner())
    # BNFTools.dump_rules_str(bnf_parser.rules)
    progs = ['''sum = 0;
for (i=1; i<=9; i++)
{
  for (j=1; j<=9; j++)
  {
    p = i * j;
    sum = sum + p;
  }
}

return sum;
''', '''a = 1;
b = 2;
c = a + b;
return c;''', '''sum = 0;
for (i=0; i<=10; i++)
{
  p = i * i;
  sum = sum + p;
}
return sum
''']
    for prog in progs:
        print(prog)
        _result = bnf_parser.parse(prog)
        # print(_result)
        TreeTools.dump_to_console(_result)
        print('=======')
