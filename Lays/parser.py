from Lays.scanner import Scanner
from Lays.treer import Tree


class Parser:

    def __init__(self, scanner: Scanner) -> None:
        super().__init__()
        self.parsed_tree = self.parse_prog(scanner)

    def parse_prog(self, scanner: Scanner):
        """PROG = BaseList """
        return Tree('PROG').append(self.parse_base_list(scanner))

    def parse_base_list(self, scanner: Scanner):
        """BaseList = (BASE)*"""
        tree = Tree('BaseList')

        while not scanner.is_end() and not scanner.is_next('}'):
            tree.append(self.parse_base(scanner))
        return tree

    def parse_base(self, scanner: Scanner):
        """BASE = FOR | STMT ';' """
        tree = Tree('BASE')
        if scanner.is_next('for'):
            tree.append(self.parse_for(scanner))
        else:
            tree.append(self.parse_stmt(scanner))
        tree.append(scanner.get_next(';'))
        return tree

    def parse_for(self, scanner: Scanner):
        """FOR = 'for' '(' STMT ';' COND ';' STMT ')' BLOCK """
        tree = Tree('FOR') \
            .append(scanner.get_next('for')) \
            .append(scanner.get_next('(')) \
            .append(self.parse_stmt(scanner)) \
            .append(scanner.get_next('END')) \
            .append(self.parse_cond(scanner)) \
            .append(scanner.get_next('END')) \
            .append(self.parse_stmt(scanner)) \
            .append(scanner.get_next(')')) \
            .append(self.parse_block(scanner))
        return tree

    def parse_stmt(self, scanner: Scanner):
        """STMT = 'return' id | id '=' EXP | id ('++'|'--') """
        tree = Tree('STMT')
        if scanner.is_next('return'):
            tree.append(scanner.get_next('return')) \
                .append(self.parse_id(scanner))
        else:
            tree.append(self.parse_id(scanner))
            if scanner.is_next('ASSIGN'):
                tree.append(scanner.get_next('ASSIGN')) \
                    .append(self.parse_exp(scanner))
            else:
                tree.append(scanner.get_next('UnaryOP'))

        return tree

    def parse_block(self, scanner: Scanner):
        """BLOCK = '{' BaseList '}' """
        tree = Tree('BLOCK') \
            .append(scanner.get_next('{')) \
            .append(self.parse_base_list(scanner)) \
            .append(scanner.get_next('}'))
        return tree

    def parse_exp(self, scanner: Scanner):
        """EXP = ITEM ([+-*/] ITEM)? """
        tree = Tree('EXP') \
            .append(self.parse_item(scanner))
        if scanner.is_next('OP'):
            tree.append(scanner.get_next('OP')) \
                .append(self.parse_item(scanner))
        return tree

    def parse_cond(self, scanner: Scanner):
        """COND = EXP ('=='|'!='|'<='|'>='|'<'|'>') EXP"""
        tree = Tree('COND') \
            .append(self.parse_exp(scanner)) \
            .append(scanner.get_next('COND')) \
            .append(self.parse_exp(scanner))
        return tree

    def parse_item(self, scanner: Scanner):
        """ITEM = id | number """
        tree = Tree('ITEM')
        if scanner.is_next('ID'):
            tree.append(self.parse_id(scanner))
        else:
            tree.append(self.parse_number(scanner))
        return tree

    def parse_id(self, scanner: Scanner):
        """id = [A-Za-z_][A-Za-z0-9_]*"""
        tree = Tree('ID') \
            .append(scanner.get_next('ID'))
        return tree

    def parse_number(self, scanner: Scanner):
        """number = [0-9]+"""
        tree = Tree('Number') \
            .append(scanner.get_next('NUMBER'))
        return tree