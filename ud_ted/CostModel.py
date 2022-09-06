# A tree edit-distance tool for Universal Dependencies.
# Copyright (C) 2022 Klara Lennermann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Label:
    """
    A label class that contains all parts of a UD node label.
    """

    def __init__(self, form: str = None, deprel: str = None, upos: str = None):
        self.form: str = form
        self.deprel: str = deprel.split(":")[0] if deprel else None  # Only universal tag
        self.upos: str = upos

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Label):
            return False
        return self.form == other.form and self.deprel == other.deprel and self.upos == other.upos

    def __str__(self):
        return f"({self.deprel}){self.form}.{self.upos}"


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

    # Substitution
    else:
        return _deprel_cost(node_a, node_b)


def upos_cost_func(node_a: Label, node_b: Label) -> float:
    """
    A cost function that assumes unit costs for insertion and deletion and substitution of a universal dependency tag.

    :param node_a: The source node
    :param node_b: The target node
    :return: The cost of substituting the source node with the target node
    """
    # Insertion and deletion
    if node_a is None or node_b is None:
        return 1.0

    # Substitution
    else:
        return _upos_cost(node_a, node_b)


def deprel_upos_cost_func(node_a: Label, node_b: Label) -> float:
    """
    A cost function that assumes unit costs for insertion and deletion and substitution of a dependency relation a
    universal dependency tag.

    :param node_a: The source node
    :param node_b: The target node
    :return: The cost of substituting the source node with the target node
    """
    # Insertion and deletion
    if node_a is None or node_b is None:
        return 1.0

    # Substitution
    else:
        cost = _deprel_cost(node_a, node_b) + _upos_cost(node_a, node_b)
        return cost


def _deprel_cost(node_a: Label, node_b: Label) -> float:
    if node_a.deprel == node_b.deprel:
        return 0.0
    else:
        return 1.0


def _upos_cost(node_a: Label, node_b: Label) -> float:
    if node_a.upos == node_b.upos:
        return 0.0
    else:
        return 1.0
