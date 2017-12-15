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
    def dump_str(dfs_tree: Tree, depth=0):
        global DUMPED_TREE
        DUMPED_TREE += ' ' * depth + 'node: ' + dfs_tree.name + '\n'
        for node in dfs_tree.children:
            if isinstance(node, Tree):
                TreeTools.dump_str(node, depth + 1)
            else:
                DUMPED_TREE += ' ' * depth + str(node) + '\n'
        return DUMPED_TREE

    @staticmethod
    def dump_html_code(dfs_tree):
        return dump_to_html(TreeTools.dump_str(dfs_tree))

    @staticmethod
    def dump_to_console(dfs_tree: Tree):
        print(TreeTools.dump_str(dfs_tree))


def dump_to_html(content):
    return content.replace('\n', '<br>').replace(' ', '&nbsp;')
