from processlib.Tree import Tree

DUMPED_TREE = ''


def dfs_dump(tree):
    global DUMPED_TREE
    DUMPED_TREE = ''
    dump_str(tree)
    return DUMPED_TREE


def dump_str(dfs_tree: Tree, depth=0):
    global DUMPED_TREE
    DUMPED_TREE += ' ' * depth + 'node: ' + dfs_tree.name + '\n'
    for node in dfs_tree.children:
        if isinstance(node, Tree):
            dump_str(node, depth + 1)
        else:
            DUMPED_TREE += ' ' * depth + str(node) + '\n'
    return DUMPED_TREE


def dump_html_code(dfs_tree):
    return dump_str(dfs_tree).replace('\n', '<br>').replace(' ', '&nbsp;')


def dump_to_console(dfs_tree: Tree):
    print(dump_str(dfs_tree))
