# A modified implementation of the unordered tree edit distance by Benjamin Paaßen.
# The original implementation can be found at https://gitlab.com/bpaassen/uted.
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

import numpy as np
import time
from queue import PriorityQueue


def outermost_right_leaves(adj):
    """ Computes the outermost right leaves of a tree based on its adjacency
    list. The outermost right leaf of a tree is defined as recursively
    accessing the right-most child of a node until we hit a leaf.

    Note that we assume a proper depth-first-search order of adj, i.e. for
    every node i, the following indices are all part of the subtree rooted at
    i until we hit the parent of i's right sibling or the end of the tree.

    Parameters
    ----------
    adj: list
        An adjacency list representation of the tree, i.e. an array such that
        for every i, adj[i] is the list of child indices for node i.

    Returns
    -------
    orl: int array
        An array containing the outermost right leaf parent for every node
        in the tree.

    """
    # the number of nodes in the tree
    m = len(adj)
    # the array into which we will write the outermost right leaves for each
    # node
    orl = np.full(m, -1, dtype=int)
    for i in range(m):
        # keep searching until we hit a node for which the outermost right
        # leaf is already defined or until we hit a leaf
        r = i
        while True:
            # if r has no children, r is the outermost right leaf for i
            if not adj[r]:
                orl[i] = r
                break
            # if the outermost right leaf for r is defined, that is also the
            # outermost right leaf for i
            if orl[r] >= 0:
                orl[i] = orl[r]
                break
            # otherwise, continue searching
            r = adj[r][-1]
    return orl


def parents(adj):
    """ Returns the parent representation of the tree with the given
    adjacency list.

    Parameters
    ----------
    adj: list
        The adjacency list of the tree.

    Returns
    -------
    par: int array
        a numpy integer array with len(adj) elements, where the ith
        element contains the parent of the parent of the ith node.
        Nodes without children contain the entry -1.

    """
    par = np.full(len(adj), -1, dtype=int)
    for i in range(len(adj)):
        for j in adj[i]:
            par[j] = i
    return par


class LinearHeuristic:
    """ A linear-time heuristic which lower-bounds the unordered
    tree edit distance between two forests by the minimal cost of deletions
    and insertions we have to apply, ignoring all replacement costs.

    Attributes
    ----------
    dels: ndarray
        An m-element vector of deletion costs.
    inss: ndarray
        An n-element vector of insertion costs.
    reps: ndarray
        An m x n matrix of replacement costs (will be ignored)

    """

    def __init__(self, dels, inss, reps):
        self.dels = dels
        self.inss = inss

    def apply(self, i, k, remaining):
        """ Applies the heuristic to compare two subforests of the input tree,
        namely the subforest x[i:k+1] and the subforest y[remaining].

        Parameters
        ----------
        i: int
            The start parent of the subforest in x.
        k: int
            The end parent of the subforest in x.
        remaining: set
            The set of indices for the suborest in y.

        Returns
        -------
        d: float
            A lower bound for the unordered tree edit distance between
            the subforest x[i:k+1] and the subforest y[remaining].

        """
        m = k - i
        remaining = list(remaining)
        n = len(remaining)
        # if m or n is zero, compute the value quickly
        if m == 0:
            if n == 0:
                return 0.
            return self.inss[remaining].sum()
        if n == 0:
            return self.dels[i:k].sum()
        # check which input is smaller
        if m == n:
            return 0.
        elif m < n:
            # use the numpy partition function to find the n - m smallest
            # insertion costs without having to do an nlogn sorting
            l = n - m
            sorted_inss = np.partition(self.inss[remaining], l)
            return np.sum(sorted_inss[:l])
        else:
            # use the numpy partition function to find the n - m smallest
            # deletion costs without having to do an nlogn sorting
            l = m - n
            sorted_dels = np.partition(self.dels[i:k], l)
            return np.sum(sorted_dels[:l])


def uted_astar(x_nodes, x_adj, y_nodes, y_adj, delta=None, heuristic=1, verbose=False, timeout=None):
    """ Computes the unordered tree edit distance between two trees via an
    A* algorithm. This implementation is inspired by Yoshino, Higuchi, and
    Hirata (2013). In contrast to this prior work, however, we are not
    restricted to unit edit costs but can deal with arbitrary cost functions.
    For this purpose, this implementation contains three novel lower bound
    functions, one in linear, one in quadratic, and one in cubic time, which
    provide tighter and tighter lower bounds on the actual edit distance.

    Note that this function is guaranteed to compute the correct unordered edit
    distance, but this means that it - in general - runs in exponential time.
    This function is particularly slow if there are many co-optimal or close to
    co-optimal mappings, because A* will try all of them.

    Parameters
    ----------
    x_nodes: list
        Nodes of the first tree.
    x_adj: list
        Adjacency list of the first tree. Note that the tree must be
        in depth first search order.
    y_nodes: list
        Nodes of the second tree.
    y_adj: list
        Adjacency list of the second tree. Note that the tree must be
        in depth first search order.
    delta: function (default = None)
        a function that takes two nodes as inputs and returns their pairwise
        distance, where delta(x, None) should be the cost of deleting x and
        delta(None, y) should be the cost of inserting y. If undefined, we use
        unit costs.
    heuristic: int (default = 1)
        Level of the heuristic, either 1, 2, 3, or 'yoshino'. Heuristics 1,
        2, and 3 can handle generic delta functions, whereas the yoshino
        heuristic is limited to unit distances. Note that the runtime is
        different between heuristics: Yoshino and 1 are linear-time,
        2 is quadratic, and 3 is cubic time. However, 2 provides a tighter
        lower bound than 1, and 3 a tighter bound than 2.
    timeout: int (default = None)
        Number of seconds after which to stop searching or None if no timeout
        is desired.

    Returns
    -------
    d: float
        The unordered tree edit distance
    alignment: list
        The alignment corresponding to the distance. x[i] is aligned with
        y[alignment[i]]. If alignment[i] = -1, this means that node i is
        deleted.
    search_size: int
        The number of nodes in the edit distance search tree.

    """

    # pre-compute deletion, insertion, and replacement costs
    m = len(x_nodes)
    n = len(y_nodes)

    if delta is None:
        dels = np.ones(m)
        inss = np.ones(n)
        reps = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                if x_nodes[i] != y_nodes[j]:
                    reps[i, j] = 1.
    else:
        dels = np.zeros(m)
        for i in range(m):
            dels[i] = delta(x_nodes[i], None)
        inss = np.zeros(n)
        for j in range(n):
            inss[j] = delta(None, y_nodes[j])
        reps = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                reps[i, j] = delta(x_nodes[i], y_nodes[j])

    # set heuristic
    h = LinearHeuristic(dels, inss, reps)

    # pre-compute outermost right leaves for x
    x_orl = outermost_right_leaves(x_adj)
    # pre-compute outermist right leaves for y
    y_orl = outermost_right_leaves(y_adj)
    # pre-compute parents for x
    x_pi = parents(x_adj)
    # pre-compute parents for y
    y_pi = parents(y_adj)

    # set up a list of nodes in the edit distance search tree
    # note: in the edit distance search tree, depth codes the
    # parent i in the left tree and the label codes the parent j
    # in the right tree. The path from the root to a node
    # constitutes a partial alignment of both trees.
    edist_nodes = [0]
    # set up the parent reference in the edit distance search tree
    edist_parents = [-1]
    # set up a storage for heuristic sibling alingment costs
    edist_h_sibs = [0]
    # set up a priority queue which stores the currently best
    # node
    Q = PriorityQueue()
    g = reps[0, 0]
    h_child = h.apply(1, m, list(range(1, n)))
    Q.put((g + h_child, g, 0))

    # keep track of the best solution until now
    best_distance = np.inf
    best_solution = None

    # keep track of the current highest lower bound
    highest_lower_bound = 0

    # keep searching
    start = time.time()
    while not Q.empty():

        # stop if search takes too long
        if timeout and time.time() - start > timeout:
            return None

        # pop the edit path with the currently best lower
        # bound
        f_lo_parent, g_parent, v_parent = Q.get()

        if verbose:
            print('remaining best lower bound: %g; current best solution: %g' % (f_lo_parent, best_distance))

        # if the lower bound is already higher than the currently best
        # solution, stop the search here
        if f_lo_parent >= best_distance:
            break

        # extract which nodes are already aligned in the current branch
        # of the search
        partial_alignment = []
        u = v_parent
        while u >= 0:
            partial_alignment.append(edist_nodes[u])
            u = edist_parents[u]
        partial_alignment.reverse()
        i = len(partial_alignment)

        if verbose:
            print('trying to align node %d from partial alignment %s' % (i, str(partial_alignment)))

        # This is a technical check. During an A* computation, the
        # lower bound on the final value is only permitted to
        # increase. If it does not, there is a bug.
        if f_lo_parent > highest_lower_bound:
            highest_lower_bound = f_lo_parent
        elif f_lo_parent < highest_lower_bound - 1E-3:
            print('current partial alignment')
            print(partial_alignment)
            raise ValueError(
                'Internal error: Lower bound shrank during computation, indicating that it is not a true lower bound!')

        # extract which nodes in the right-hand-side tree are still
        # available for alignment.
        # For this purpose, we start with the nodes that are
        # explicitly mentioned in the partial alignment and fill in
        # all nodes on ancestor paths towards the root
        taken = set(partial_alignment)
        # we have to remove nodes on the path from the root
        # to aligned nodes, though, because these are already
        # counted in g_parent
        for j in partial_alignment:
            if j < 1:
                continue
            l = y_pi[j]
            while l > 0 and l not in taken:
                taken.add(l)
                l = y_pi[l]
        # next, we check if there are any nodes left to align in x
        if i == len(x_nodes):
            # if this is not the case, we can construct a complete
            # solution by inserting all remaining nodes from y
            remaining = set(range(n)) - taken
            dist = g_parent
            for j in remaining:
                dist += inss[j]
            # if the solution is better than the current best, store it
            if dist < best_distance:
                best_distance = dist
                best_solution = partial_alignment
            continue

        # next, we search upwards in x until we find 
        # an aligned ancestor (at worst: the root of x).
        # Let x[k] be this ancestor and let y[l] be its partner in y.
        # Then, we can only align descendants of x[k] to descendants of
        # y[l] (which are not yet taken).
        k = x_pi[i]
        while partial_alignment[k] < 0:
            k = x_pi[k]
        l = partial_alignment[k]
        # compute all descendants of y[l] and remove all nodes which are
        # already aligned
        remaining = set(range(l, y_orl[l] + 1)) - taken

        # recover the heuristic cost for aligning all right siblings
        # of x[k], which we have already computed before.
        # for that purpose, we first have to retrieve the node in
        # the edit distance search tree
        u = v_parent
        for r in range(k + 1, i):
            u = edist_parents[u]
        # and then get its h_sib_value
        h_sib_parent = edist_h_sibs[u]

        # now, construct all children in the edit distance search tree.

        # The first child represents the deletion of i.
        v = len(edist_nodes)
        edist_nodes.append(-1)
        edist_parents.append(v_parent)
        # Accordingly, our new g value is the previous g value plus
        # the deletion costs for i
        g = g_parent + dels[i]
        # the heuristic value for aligning children is zero because by
        # deleting x[i] we raise all its children to the sibling level
        h_child = 0.
        # the heuristic value for aligning siblings concerns all
        # descendants of k which are after i in depth first search
        # and all remaining nodes in y which we computed before.
        # To this, we add the sibling alignment cost for k.
        h_sib = h.apply(i + 1, x_orl[k] + 1, remaining) + h_sib_parent
        edist_h_sibs.append(h_sib)
        # compute objective function lower bound. If our bound is lower,
        # we take the bound from the parent node
        f_lo = g + h_child + h_sib
        f_lo = max(f_lo_parent, f_lo)
        # put node onto the priority queue
        Q.put((f_lo, g, v))

        if verbose:
            print('deletion: g = %g, h_sib = %g, h_sib_parent = %g -> f_lo = %g' % (g, h_sib, h_sib_parent, f_lo))

        # The remaining children in the edit distance search tree concern
        # the alignment of i with a node that is in remaining
        for j in remaining:
            # add the alignment of i with j to the edit distance search tree
            v = len(edist_nodes)
            edist_nodes.append(j)
            edist_parents.append(v_parent)
            # our new g value if the parent g value plus the replacement cost
            # of i with j plus the insertion of all nodes on a path from l to j
            taken_j = taken.copy()
            taken_j.add(j)
            g = g_parent + reps[i, j]
            l2 = y_pi[j]
            while l2 != l:
                g += inss[l2]
                taken_j.add(l2)
                l2 = y_pi[l2]
            # the heuristic value for aligning children concerns the
            # descendants of i and the descendants of j
            remaining_child = set(range(j + 1, y_orl[j] + 1)) - taken_j
            h_child = h.apply(i + 1, x_orl[i] + 1, remaining_child)
            # the heuristic value for aligning siblings concerns the
            # remaining descendants of k and l after removing the
            # descendants of i and j
            remaining_j = remaining - set(range(j + 1, y_orl[j] + 1)).union(taken_j)
            # and we add the heuristic sibling value for the parent
            h_sib = h.apply(x_orl[i] + 1, x_orl[k] + 1, remaining_j) + h_sib_parent

            edist_h_sibs.append(h_sib)
            # compute objective function lower bound. If our bound is lower,
            # we take the bound from the parent node
            f_lo = g + h_child + h_sib
            f_lo = max(f_lo_parent, f_lo)
            # put node onto the priority queue
            Q.put((f_lo, g, v))

            if verbose:
                print('replacement with %d: g = %g, h_child = %g, h_sib = %g, h_sib_parent = %g -> f_lo = %g' % (
                    j, g, h_child, h_sib, h_sib_parent, f_lo))

    return best_distance, best_solution, len(edist_nodes)
