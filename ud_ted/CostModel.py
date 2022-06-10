class Label:
    """
    A label class that contains all parts of a UD node label.
    """

    def __init__(self, form: str = None, deprel: str = None):
        self.form: str = form
        self.deprel: str = deprel.split(":")[0] if deprel else None  # Only universal tag

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Label):
            return False
        return self.form == other.form and self.deprel == other.deprel

    def __str__(self):
        return f"{self.form}"


def simple_cost_func(node_a: Label, node_b: Label) -> float:
    """
    A simple cost function that assumes unit costs for insertion and deletion and zero cost for substitution.

    :param node_a: The source node
    :param node_b: The target node
    :return: The cost of substituting the source node with the target node
    """

    # Insertion and deletion
    if node_a is None or node_b is None:
        return 1.0

    # Substitution (content of the nodes doesn't matter)
    else:
        return 0.0


def deprel_cost_func(node_a: Label, node_b: Label) -> float:
    """
    A cost function that assumes unit costs for insertion and deletion and substitution of a dependency relation.

    :param node_a: The source node
    :param node_b: The target node
    :return: The cost of substituting the source node with the target node
    """
    # Insertion and deletion
    if node_a is None or node_b is None or node_a.deprel != node_b.deprel:
        return 1.0

    # Substitution with identical dependency relation
    else:
        return 0.0
