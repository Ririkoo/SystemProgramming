from typing import Generator, Union, Tuple

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


def dump_to_html(content):
    return content.replace('\n', '<br>').replace(' ', '&nbsp;')
