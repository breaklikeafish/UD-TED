import sys

import pyconll
import zss

from argparse import Namespace
from typing import Optional
from ud_ted.customize_zss import UDNode, UDNodeLabel, insert_cost, remove_cost, update_cost


def ud_ted(args: Namespace) -> int:
    """
    Computes the tree edit distance between two CoNLL-U sentences.

    :param args: Contains command line arguments, including paths to the CoNLL-U files
    :return: The tree edit distance
    """
    sent1 = load_sentence(args.file1, args.ids[0] if args.ids else None)
    sent2 = load_sentence(args.file2, args.ids[1] if args.ids else None)
    return zss.distance(sent1, sent2,
                        get_children=UDNode.get_children,
                        insert_cost=insert_cost,
                        remove_cost=remove_cost,
                        update_cost=update_cost)


def load_sentence(path: str, sent_id: Optional[str]) -> UDNode:
    """
    Load the sentence from the CoNNL-U file and transform it into the correct format.

    :param path: The path to the CoNNL-U file
    :param sent_id: The sentence ID; if None, the first sentence in the file is processed
    :return: A tree representation of the sentence
    """
    for sentence in pyconll.load_from_file(path):
        if not sent_id or sent_id == sentence.id:
            pyconll_tree = sentence.to_tree()
            tree = UDNode(UDNodeLabel(form=pyconll_tree.data.form))
            for token in pyconll_tree:
                _add_child(token, tree)
            return tree


def _add_child(pyconll_tree: pyconll.tree.Tree, tree: UDNode):
    node = UDNode(UDNodeLabel(form=pyconll_tree.data.form))
    for token in pyconll_tree:
        _add_child(token, node)
    tree.addkid(node)
