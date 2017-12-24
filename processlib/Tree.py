class Tree:

    def __init__(self, name: str, children: 'Tree' = None) -> None:
        super().__init__()
        if children is None:
            children = []
        self.children = children
        self.name = name

    def append(self, child_tree, concat=False):
        if concat is True:
            if isinstance(child_tree, Tree):
                self.children.extend(child_tree.children)
            else:
                self.children.extend(iter(child_tree))
        else:
            self.children.append(child_tree)
        return self
