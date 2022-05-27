from zss import Node


class UDNodeLabel:
    """
    A label class that contains all parts of a UD node label.
    """

    def __init__(self, form: str = None):
        self.form: str = form

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, UDNodeLabel):
            return False
        return self.form == other.form

    def __str__(self):
        return self.form


class UDNode(Node):
    """
    A custom node class that holds all relevant information from a UD dependency graph in its label.
    """

    def __init__(self, label: UDNodeLabel, children=None):
        super().__init__(label, children)

    def __str__(self):
        string = f"[{self.label} "
        for child in self.children:
            string += str(child)
        string += " ]"
        return string


def insert_cost(node: Node) -> int:
    """
    A function to compute the cost of an insert operation.

    :param node: The node to insert
    :return: The cost of inserting the node
    """
    return 1


def remove_cost(node: Node) -> int:
    """
    A function to compute the cost of a delete operation.

    :param node: The node to delete
    :return: The cost of deleting the node
    """
    return 1


def update_cost(node_a: Node, node_b: Node) -> int:
    """
    A function to compute the cost of changing node A into node B.

    :param node_a: The source node
    :param node_b: The target node
    :return: The cost of updating the node
    """
    return 0
