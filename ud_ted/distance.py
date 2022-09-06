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

import pyconll
import requests
import time

from edist import ted
from typing import List, Optional, Tuple, Generator
from ud_ted import CostModel
from ud_ted.CostModel import Label
from uted import uted_astar


def ud_ted(file1: str, file2: str,
           timeout: Optional[float] = None,
           ordered: bool = False,
           id1: Optional[str] = None, id2: Optional[str] = None,
           deprel: Optional[bool] = False,
           upos: Optional[bool] = False
           ) -> float:
    """
    Computes the tree edit distance between two CoNLL-U sentences.

    :param file1: The path to the CoNLL-U file containing the first sentence
    :param file2: The path to the CoNLL-U file containing the second sentence
    :param timeout: Optional. The number of seconds after which to stop the search
    :param ordered: Whether to compute the ordered or unordered tree edit distance
    :param id1: Optional. The ID of the first sentence
    :param id2: Optional. The ID of the second sentence
    :param deprel: Optional. Whether to compare the dependency relationship label
    :param upos: Optional. Whether to compare the universal dependency tag
    :return: The tree edit distance
    """
    # Load input
    x_nodes, x_adj = load_sentence(file1, id1)
    y_nodes, y_adj = load_sentence(file2, id2)

    # Choose cost function
    cost_func = _choose_cost_func(deprel, upos)

    # Compute distance
    if ordered:
        distance = ted.ted(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func)
    else:
        distance, _, _ = uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func, heuristic=1,
                                    timeout=timeout)

    return distance


def doc_ud_ted(file1: str, file2: str,
               timeout: Optional[float] = None,
               ordered: bool = False,
               deprel: Optional[bool] = False,
               upos: Optional[bool] = False
               ) -> float:
    """
    Computes the tree edit distance between every pair of sentences in two CoNLL-U files.

    :param file1: The path to the CoNLL-U file containing the first treebank
    :param file2: The path to the CoNLL-U file containing the second treebank
    :param timeout: Optional. The number of seconds after which to stop the search
    :param ordered: Whether to compute the ordered or unordered tree edit distance
    :param deprel: Optional. Whether to compare the dependency relationship label
    :param upos: Optional. Whether to compare the universal dependency tag
    :return: The tree edit distance
    """
    i = 0
    distances = []

    # Choose cost function
    cost_func = _choose_cost_func(deprel, upos)

    print(f"ID\tDistance\tTime\tNodes1\tNodes2")

    for sent1, sent2 in zip(load_all_sentences(file1), load_all_sentences(file2)):

        if sent1 is None or sent2 is None:
            break

        x_nodes, x_adj, sent_id = sent1
        y_nodes, y_adj, _ = sent2

        # Compute distance
        start = time.time()
        if ordered:
            distance = ted.ted(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func)
        else:
            x = uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=cost_func, timeout=timeout)
            distance, _, _ = x if x else (None, None, None)
        end = time.time()

        print(f"{sent_id}\t{distance}\t{end - start}sec\t{len(x_nodes)}\t{len(y_nodes)}")

        if distance is not None:
            distances.append(distance)

        i += 1

    if len(distances) > 0:
        return sum(distances) / len(distances)


def load_all_sentences(path: str) -> Generator[Tuple[List[Label], List[List[int]], Optional[str]], None, None]:
    """
    Yields all CoNLL-U sentences as an adjacency representation of the tree

    :param path: The path to the CoNLL-U file
    :return: A generator over all sentences in the file
    """
    if path.startswith("https://"):
        path = requests.get(path).text
        load_func = pyconll.load_from_string
    else:
        load_func = pyconll.load_from_file
    for sentence in load_func(path):
        pyconll_tree = sentence.to_tree()
        nodes = [Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel, upos=pyconll_tree.data.upos)]
        adj = [[]]
        for token in pyconll_tree:
            _add_child(token, nodes, adj, 0)
        while len(nodes) > len(adj):
            adj.append([])
        yield nodes, adj, sentence.id


def load_sentence(path: str, sent_id: Optional[str] = None, return_id: bool = False) \
        -> Tuple[List[Label], List[List[int]]] | Tuple[List[Label], List[List[int]], str]:
    """
    Loads the CoNLL-U sentence into an adjacency representation of the tree

    :param path: The path to the CoNLL-U file containing the sentence
    :param sent_id: Optional. The ID of the sentence
    :param return_id: Whether to return the sentence ID if given
    :return: A tuple of a label list and an adjacency list (and the sentence ID if return_id is True)
    """
    if path.startswith("https://"):
        path = requests.get(path).text
        load_func = pyconll.load_from_string
    else:
        load_func = pyconll.load_from_file
    for sentence in load_func(path):
        pyconll_tree = sentence.to_tree()
        if sent_id == sentence.id:
            nodes = [Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel, upos=pyconll_tree.data.upos)]
            adj = [[]]
            for token in pyconll_tree:
                _add_child(token, nodes, adj, 0)
            while len(nodes) > len(adj):
                adj.append([])
            if return_id:
                return nodes, adj, sentence.id
            else:
                return nodes, adj


def _add_child(pyconll_tree: pyconll.tree.Tree, tree: List[Label], adj: List[List[int]], parent: int):
    tree.append(Label(form=pyconll_tree.data.form, deprel=pyconll_tree.data.deprel, upos=pyconll_tree.data.upos))
    while parent >= len(adj):
        adj.append([])
    adj[parent].append(len(tree)-1)
    parent = len(tree)-1
    for token in pyconll_tree:
        _add_child(token, tree, adj, parent)


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
