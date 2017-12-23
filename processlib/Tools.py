from typing import Generator, Union, Tuple, Dict

from processlib.BNF import RuleType, ModifierType, BNFRule
from processlib.Token import ScannerToken, SemanticToken
from processlib.Tree import Tree

DUMPED_TREE = ''


class TreeTools:
    @staticmethod
    def dfs_dump(tree):
        global DUMPED_TREE
        DUMPED_TREE = ''
        TreeTools.dump_str(tree)
        return DUMPED_TREE

    @staticmethod
    def dump_str(dfs_tree: Tree):
        global DUMPED_TREE
        DUMPED_TREE = ''
        for node, depth, parent, child_index in TreeTools.flatten(dfs_tree):
            if isinstance(node, Tree):
                DUMPED_TREE += ' ' * depth + 'node: ' + node.name + '\n'
            else:
                DUMPED_TREE += ' ' * depth + str(node) + '\n'
        return DUMPED_TREE

    @staticmethod
    def dump_html_code(dfs_tree):
        return dump_to_html(TreeTools.dump_str(dfs_tree))

    @staticmethod
    def dump_to_console(dfs_tree: Tree):
        print(TreeTools.dump_str(dfs_tree))

    @staticmethod
    def flatten(dfs_tree: Tree) -> Generator[
        Tuple[Union[Tree, ScannerToken, SemanticToken, any], int, Tree, int], None, None]:
        def each_nodes(tree, depth=0, parent=None, child_index=0):
            yield (tree, depth, parent, child_index)
            for index, node in enumerate(tree.children):
                if isinstance(node, Tree):
                    yield from each_nodes(node, depth + 1, tree, index)
                else:
                    yield (node, depth + 1, tree, index)

        return each_nodes(dfs_tree)


class BNFTools:
    @staticmethod
    def dump_rules_str(rules: Dict[str, BNFRule]):
        for rule in rules.values():
            if rule.type is RuleType.internal:
                continue
            print(rule.name + ' = ' + BNFTools.dump_rule_str(rules, rule))

    @staticmethod
    def dump_rule_str(all_rules, rule):
        result = []
        for sub in rule.sub_rules:
            result_sub = []
            for token in sub:
                if token.type is RuleType.string:
                    result_sub.append("'" + token.content + "'")
                elif token.type is RuleType.regex:
                    result_sub.append(token.content)

                elif token.type is RuleType.link:
                    if all_rules[token.content].type == RuleType.internal:
                        result_sub.append('(' + BNFTools.dump_rule_str(all_rules, all_rules[token.content]) + ')')
                    else:
                        result_sub.append(token.content)

                if token.modifier is not ModifierType.none:
                    result_sub[-1] += token.modifier.value
            result.append(' '.join(result_sub))
        return ' | '.join(result)


def dump_to_html(content):
    return content.replace('\n', '<br>').replace(' ', '&nbsp;')
