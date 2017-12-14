from processlib.treer import Tree

DUMPED_TREE=''

def dfs_dump(tree):
    global DUMPED_TREE
    DUMPED_TREE=''
    dump_str(tree)
    return DUMPED_TREE

def dump_str(dfstree, depth=0):
    global DUMPED_TREE
    DUMPED_TREE+= ' ' * depth + 'node: '+dfstree.name+'\n'
    for node in dfstree.children:
        if isinstance(node, Tree):
            dump_str(node,depth + 1)
        else:
            DUMPED_TREE+=' ' * depth + str(node)+'\n'
