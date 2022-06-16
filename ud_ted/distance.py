import time

import pyconll

from typing import List, Optional, Tuple
from ud_ted import CostModel
from ud_ted.CostModel import Label
from uted import uted_astar


def ud_ted(file1: str, file2: str,
           id1: Optional[str] = None, id2: Optional[str] = None,
           deprel: Optional[bool] = False,
           upos: Optional[bool] = False
           ) -> float:
    """
    Computes the tree edit distance between two CoNLL-U sentences.

    :param file1: The path to the CoNLL-U file containing the first sentence
    :param file2: The path to the CoNLL-U file containing the second sentence
    :param id1: Optional. The ID of the first sentence
    :param id2: Optional. The ID of the second sentence
    :param deprel: Optional. Whether to compare the dependency relationship label
    :param upos: Optional. Whether to compare the universal dependency tag
    :return: The tree edit distance
    """
    # Load input
    x_nodes, x_adj = load_sentence(file1, id1)
    y_nodes, y_adj = load_sentence(file2, id2)

    if len(x_nodes) > 27 or len(y_nodes) > 27:
        print(f"WARNING: Tree has {max(len(x_nodes), len(y_nodes))} nodes.")

    # Choose cost function
    cost_func = _choose_cost_func(deprel, upos)

    # Compute distance
    distance, alignment, n = uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func)

    return distance


def avg_ud_ted(file1: str, file2: str,
               deprel: Optional[bool] = False,
               upos: Optional[bool] = False
               ) -> float:
    """
    Computes the tree edit distance between every pair of sentences in two CoNLL-U files.

    :param file1: The path to the CoNLL-U file containing the first treebank
    :param file2: The path to the CoNLL-U file containing the second treebank
    :param deprel: Optional. Whether to compare the dependency relationship label
    :param upos: Optional. Whether to compare the universal dependency tag
    :return: The tree edit distance
    """
    i = 0
    distances = []

    # Choose cost function
    cost_func = _choose_cost_func(deprel, upos)

    print(f"ID\tDistance\tTime\tNum of Nodes")

    while True:

        # Load input
        sent1 = load_sentence(file1, sent_num=i, return_id=True)
        sent2 = load_sentence(file2, sent_num=i)

        if sent1 is None or sent2 is None:
            break

        x_nodes, x_adj, sent_id = sent1
        y_nodes, y_adj = sent2

        # Compute distance
        start = time.time()
        x = uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func)
        distance, alignment, n = x if x else (None, None, None)
        end = time.time()

        print(f"{sent_id}\t{distance}\t{end - start}sec\t{max(len(x_nodes), len(y_nodes))}")

        if distance:
            distances.append(distance)

        i += 1

    if len(distances) > 0:
        return sum(distances)/len(distances)


def load_sentence(path: str, sent_id: Optional[str] = None, sent_num: int = 0, return_id: bool = False) \
        -> Tuple[List[Label], List[List[int]]] | Tuple[List[Label], List[List[int]], str]:
    """
    Loads the CoNLL-U sentence into an adjacency representation of the tree

    :param path: The path to the CoNLL-U file containing the sentence
    :param sent_id: Optional. The ID of the second sentence
    :param sent_num: The position of the sentence in the file (only if sent_id is None)
    :param return_id: Whether to return the sentence ID if given
    :return: A tuple of a label list and an adjacency list (and the sentence ID if return_id is True)
    """
    for i, sentence in enumerate(pyconll.load_from_file(path)):
        pyconll_tree = sentence.to_tree()
        if sent_id == sentence.id or (sent_id is None and sent_num == i):
            nodes = [Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel, upos=pyconll_tree.data.upos)]
            child_index = 1
            adj = [[]]
            for token in pyconll_tree:
                adj[0].append(child_index)
                child_index = _add_child(token, nodes, adj, child_index)
            while len(nodes) > len(adj):
                adj.append([])
            if return_id:
                return nodes, adj, sentence.id
            else:
                return nodes, adj


def _add_child(pyconll_tree: pyconll.tree.Tree, tree: List[Label], adj: List[List[int]], index: int) -> int:
    tree.append(Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel, upos=pyconll_tree.data.upos))
    while index >= len(adj):
        adj.append([])
    new_index = index
    for token in pyconll_tree:
        new_index = _add_child(token, tree, adj, new_index)
        adj[index].append(new_index)
    return new_index + 1


def _choose_cost_func(deprel: bool, upos: bool):
    if deprel:
        if upos:
            return CostModel.deprel_upos_cost_func
        else:
            return CostModel.deprel_cost_func
    else:
        if upos:
            return CostModel.upos_cost_func
        else:
            return CostModel.simple_cost_func
