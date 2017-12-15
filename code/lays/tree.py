class Tree:
    def __init__(self, name: str, children: 'Tree' = None) -> None:
        super().__init__()
        if children is None:
            children = []
        self.children = children
        self.name = name

    def append(self, child_tree):
        self.children.append(child_tree)
        return self

    def dump(self, depth=0):
        print(' ' * depth + 'node:{}'.format(self.name))
        for node in self.children:
            if isinstance(node, Tree):
                node.dump(depth + 1)
            else:
                print(' ' * depth, node)
