# UD-TED
A tree edit-distance tool for Universal Dependencies developed as part of my Bachelor's thesis.

## Input
The `ud-ted` command takes two positional arguments, both of them paths to CoNLL-U files containing the input sentences.
If no other option is given, the tree edit distance between the first sentences in the files is computed.

### Options
#### `--ids`
Allows for the user to specify the sentence IDs of the sentence to be processed.
The sentence ID of a sentence must appear in a comment above the respective sentence, in the following format:
```
# sent_id = <id>
```
#### `--deprel`
Adds the edit operation to relabel the edge label (dependency relation).
Only the basic type of the dependency relation (i.e., the part before the colon) is compared.

## Output
The tree edit distance between the input trees. 
By default, all labels are ignored and the cost of both delete and insert operations is 1.
