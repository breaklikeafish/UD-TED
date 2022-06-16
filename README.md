# UD-TED
A tree edit-distance tool for Universal Dependencies developed as part of my Bachelor's thesis.

## Input
The `ud-ted` command takes two positional arguments, both of them paths to CoNLL-U files containing the input sentences.
If no other option is given, the unordered tree edit distance between the first sentences in the files is computed.

### Options
#### `--timeout`
In the worst case, unordered tree edit distance requires exponential time.
With big trees (more than 20 nodes), this may take a long time.
By providing a timeout, the program simply stops computing after the time is over, or skips the pair in the `doc` option.
#### `--ordered`
Computes the ordered tree edit distance instead.
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
