from typing import Dict

from processlib import Parser
from processlib.Token import ScannerToken, SemanticToken
from processlib.Tools import TreeTools
from processlib.Tree import Tree


class AnalysisError(Exception):

    def __init__(self, token: ScannerToken, content, message) -> None:
        lines = content.split('\n')
        line_number_width = len(str(token.line + 1))
        preview = ('...',
                   (str(token.line - 1).ljust(line_number_width) + '| ' + lines[token.line - 2]) if len(
                       lines) > (
                                                                                                            token.line - 2) >= 0 else '',
                   str(token.line).ljust(line_number_width) + '| ' + lines[token.line - 1],
                   '>'.ljust(line_number_width) + '| ' + ' ' * (token.position - 1) + '^',
                   (str(token.line + 1).ljust(line_number_width) + '| ' + lines[token.line]) if len(
                       lines) > token.line else '',
                   '...')
        preview = '\n'.join((line for line in preview if line != ''))
        super().__init__(
            '於{}:{} => {}:\n{}'.format(token.line, token.position, message, preview))


class SemanticAnalyser:
    def __init__(self, parser: Parser) -> None:
        super().__init__()
        self.parser: Parser = parser
        self.content = None
        self.variables: Dict[str, str] = {}

    def parse(self, content):
        self.content = content
        self.variables = {}
        return self._parse_semantic(self.parser.parse(content))

    def _parse_semantic(self, tree: Tree):

        for node, depth, parent, index in TreeTools.flatten(tree):
            if isinstance(node, Tree):
                if node.name == 'STMT':
                    if node.children[0].value == 'return':
                        if node.children[1].value not in self.variables:
                            raise AnalysisError(node.children[1], self.content, '變數' + node.children[1].value + '沒有宣告')
                    elif node.children[1].value == '=':
                        kind = self._check_exp(node.children[2])
                        tmp_var = node.children[0]
                        node.children[0] = SemanticToken(tmp_var.type, tmp_var.value, kind,
                                                         tmp_var.line,
                                                         tmp_var.position)
                        if (tmp_var.value in self.variables and
                                self.variables[tmp_var.value] != kind):
                            raise AnalysisError(tmp_var, self.content, '變數' + repr(tmp_var.value) + '已經宣告為 ' +
                                                repr(self.variables[tmp_var.value]) +
                                                '型態了，不能設定為 '
                                                + repr(kind) + ' 型態')
                        self.variables[node.children[0].value] = kind
                    else:
                        tmp_var = node.children[0]
                        if tmp_var.value not in self.variables:
                            raise AnalysisError(tmp_var, self.content, '變數' + tmp_var.value + '沒有宣告')
                        node.children[0] = SemanticToken(tmp_var.type, tmp_var.value, self.variables[tmp_var.value],
                                                         tmp_var.line,
                                                         tmp_var.position)
                if node.name == 'COND':
                    for exp_node in (exp for exp in node.children if isinstance(exp, Tree)):
                        self._check_exp(exp_node)
            elif isinstance(node, ScannerToken):
                parent.children[index] = SemanticToken(node.type, node.value, None,
                                                       node.line,
                                                       node.position)

        return tree

    def _check_exp(self, exp_node: Tree):
        kind = None
        last_operator = None
        for ITEM in exp_node.children:
            if isinstance(ITEM, Tree) and ITEM.name == 'ITEM':
                item = ITEM.children[0]
                if isinstance(item, Tree) and item.name == 'string':
                    ITEM.children[0] = SemanticToken('string', item.children[1].value, None,
                                                     item.children[1].line,
                                                     item.children[1].position)
                else:
                    ITEM.children[0] = SemanticToken(item.type, item.value, kind,
                                                     item.line,
                                                     item.position)
                item = ITEM.children[0]
            else:
                last_operator = ITEM
                continue

            item_kind = None
            if item.type == 'id':
                if item.value not in self.variables:
                    raise AnalysisError(item, self.content, '變數' + repr(item.value) + '沒有宣告')
                item_kind = self.variables[item.value]
                ITEM.children[0] = SemanticToken(item.type, item.value, item_kind,
                                                 item.line,
                                                 item.position)
            elif item.value:
                item_kind = item.type

            if kind is None:
                kind = item_kind
                continue
            elif kind != item_kind:
                raise AnalysisError(last_operator, self.content, '無法將' + repr(kind) + '與' + repr(item_kind) + '進行 ' +
                                    repr(last_operator.value) + ' 操作')
        return kind
