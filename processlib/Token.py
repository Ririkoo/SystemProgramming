from collections import namedtuple

ScannerToken = namedtuple('ScannerToken', ['type', 'value', 'line', 'position'])
SemanticToken = namedtuple('SemanticToken', ['type', 'value', 'kind', 'line', 'position'])
TokenType = namedtuple('TokenType', ['name', 'regex'])
