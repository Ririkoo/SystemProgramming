from processlib import Parser, Tree
from processlib.Token import ScannerToken, SemanticToken
from processlib.Tools import TreeTools


class SemanticAnalyser:
    def __init__(self, parser: Parser) -> None:
        super().__init__()
        self.parser: Parser = parser

    def parse(self, content):
        return self._parse_semantic(self.parser.parse(content))

    def _parse_semantic(self, tree: Tree):
        for node, depth, parent, index in TreeTools.flatten(tree):
            if isinstance(node, ScannerToken):
                if node.type.name == 'ID':
                    parent.children[index] = SemanticToken(node.type.name, node.value, 'number', node.line,
                                                           node.position)
                else:
                    parent.children[index] = SemanticToken(node.type.name, node.value, None, node.line,
                                                           node.position)
        return tree
