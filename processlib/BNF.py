from enum import unique, Enum, auto
from typing import NamedTuple, List, Union


@unique
class RuleType(Enum):
    string = auto()
    regex = auto()
    link = auto()
    internal = auto()
    normal = auto()


@unique
class ModifierType(Enum):
    repeat_more_than_once = '+'
    repeat_what_ever = '*'
    repeat_once_or_nothing_happened = '?'
    none = None


ModifierMap = {
    '*': ModifierType.repeat_what_ever,
    '+': ModifierType.repeat_more_than_once,
    '?': ModifierType.repeat_once_or_nothing_happened
}
BNFBaseRule = NamedTuple('BaseRule', [('type', RuleType), ('content', str), ('modifier', ModifierType)])
BNFRule = NamedTuple('BNFRule', [('type', RuleType), ('name', str), ('sub_rules', List[List[Union[BNFBaseRule, str]]])])

# BNFSubRule = NamedTuple('BNFGroupRule',
#                         [('rules_sequence', List[Union[str, 'BNFRule', 'BNFGroupRule']])])