from processlib.Scanner import Scanner
from processlib.Tree import Tree

c0_ebnf = '''
PROG = BaseList
BaseList = (BASE)*
BASE = FOR | STMT ';'
FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK
STMT = 'return' id | id '=' EXP | id ('++'|'--')
BLOCK = '{' BaseList '}'
EXP = ITEM ([+-*/] ITEM)?
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
