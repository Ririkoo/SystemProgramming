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

