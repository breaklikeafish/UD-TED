import pyconll

from typing import List, Optional, Tuple
from ud_ted import CostModel
from ud_ted.CostModel import Label
from uted import uted_astar


def ud_ted(file1: str, file2: str,
           id1: Optional[str] = None, id2: Optional[str] = None,
           deprel: Optional[bool] = False
           ) -> float:
    """
    Computes the tree edit distance between two CoNLL-U sentences.

    :param file1: The path to the CoNLL-U file containing the first sentence
    :param file2: The path to the CoNLL-U file containing the second sentence
    :param id1: Optional. The ID of the first sentence
    :param id2: Optional. The ID of the second sentence
    :param deprel: Optional. Whether to compare the dependency relationship label
    :return: The tree edit distance
    """
    # Load input
    x_nodes, x_adj = load_sentence(file1, id1)
    y_nodes, y_adj = load_sentence(file2, id2)

    # Choose cost function
    if deprel:
        cost_func = CostModel.deprel_cost_func
    else:
        cost_func = CostModel.simple_cost_func

    # Compute distance
    distance, alignment, n = uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func)

    return distance


def load_sentence(path: str, sent_id: Optional[str] = None) -> Tuple[List[Label], List[List[int]]]:
    """
    Loads the CoNLL-U sentence into an adjacency representation of the tree

    :param path: The path to the CoNLL-U file containing the sentence
    :param sent_id: Optional. The ID of the second sentence
    :return: A tuple of a label list and an adjacency list
    """
    for sentence in pyconll.load_from_file(path):
        pyconll_tree = sentence.to_tree()
        if not sent_id or sent_id == sentence.id:
            nodes = [Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel)]
            child_index = 1
            adj = [[]]
            for token in pyconll_tree:
                adj[0].append(child_index)
                child_index = _add_child(token, nodes, adj, child_index)
            return nodes, adj


def _add_child(pyconll_tree: pyconll.tree.Tree, tree: List[Label], adj: List[List[int]], index: int) -> int:
    tree.append(Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel))
    while index >= len(adj):
        adj.append([])
    new_index = index
    for token in pyconll_tree:
        new_index = _add_child(token, tree, adj, new_index)
        adj[index].append(new_index)
    return new_index + 1
