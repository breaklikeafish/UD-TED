# UD-TED
A tree edit-distance tool for Universal Dependencies developed as part of my Bachelor's thesis.

## Input
The `ud-ted` command takes two positional arguments, both of them paths to CoNLL-U files containing the input sentences.
If no other option is given, the unordered tree edit distance between the first sentences in the files is computed following the implementation by Paaßen (2021).

### Options
#### `--timeout`
In the worst case, unordered tree edit distance requires exponential time.
With big trees (more than 20 nodes), this may take a long time.
By providing a timeout, the program simply stops computing after the time is over, or skips the pair in the `doc` option.
#### `--ordered`
Computes the ordered tree edit distance following the implementation of the Zhang-Shasha algorithm in the ``edist`` package (Paaßen et al., 2015) instead.
#### `--ids`
Allows for the user to specify the sentence IDs of the sentence to be processed.
The sentence ID of a sentence must appear in a comment above the respective sentence, in the following format:
```
# sent_id = <id>
```
#### `--doc`
Compute the tree edit distance between every pair of trees in two files.
#### `--deprel`
Adds the edit operation to relabel the edge label (dependency relation).
Only the basic type of the dependency relation (i.e., the part before the colon) is compared.
#### `--upos`
Adds the edit operation to relabel the universal dependency tag (UPOS).

## Output
The tree edit distance between the input trees. 
By default, all labels are ignored and the cost of both delete and insert operations is 1.

## References
- Benjamin Paaßen. 2021. [An A*-algorithm for the unordered tree edit distance with custom costs](https://doi.org/10.1007%2F978-3-030-89657-7_27). In Nora Reyes, Richard Connor, Nils Kriege, Daniyal Kazempour, Ilaria Bartolini, Erich Schubert, and Jian-Jia Chen, editors, _Similarity Search and Applications_, pages 364–371. Springer International Publishing.
- Benjamin Paaßen, Bassam Mokbel, and Barbara Hammer. 2015. [A toolbox for adaptive sequence dissimilarity measures for intelligent tutoring systems](http://www.educationaldatamining.org/EDM2015/uploads/papers/paper_257.pdf). In _Proceedings of the 8th International Conference on Educational Data Mining (EDM 2015)_, pages 632–632. International Educational Datamining Society.
