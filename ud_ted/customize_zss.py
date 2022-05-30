from zss import Node


class UDNodeLabel:
    """
    A label class that contains all parts of a UD node label.
    """

    def __init__(self, form: str = None, deprel: str = None):
        self.form: str = form
        self.deprel: str = deprel.split(":")[0]  # Only universal tag

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, UDNodeLabel):
            return False
        return self.form == other.form and self.deprel == other.deprel

    def __str__(self):
        return f"({self.deprel}){self.form}"


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


class CostModel:
    """
    A representation of the command line options that influence the cost operations.
    """

    def __init__(self, deprel: bool = False):
        self.deprel = deprel

    @staticmethod
    def insert_cost(node: Node) -> int:
        """
        A function to compute the cost of an insert operation.

        :param node: The node to insert
        :return: The cost of inserting the node
        """
        return 1

    @staticmethod
    def remove_cost(node: Node) -> int:
        """
        A function to compute the cost of a delete operation.

        :param node: The node to delete
        :return: The cost of deleting the node
        """
        return 1

    def update_cost(self, node_a: Node, node_b: Node) -> int:
        """
        A function to compute the cost of changing node A into node B.

        :param node_a: The source node
        :param node_b: The target node
        :return: The cost of updating the node
        """
        if self.deprel and node_a.label.deprel != node_b.label.deprel:
            return 1
        else:
            return 0
