import argparse
import time

from ud_ted.distance import ud_ted, avg_ud_ted


def main():
    """
    The main script that reads the command line arguments and computes the tree edit distance of the input.
    """
    # Create parser
    parser = argparse.ArgumentParser(description="Compute the tree edit distance between two Universal Dependencies "
                                                 "dependency trees")

    # Add arguments
    parser.add_argument("file1",
                        type=str,
                        help="the path to the file containing the first sentence",
                        metavar="file1")
    parser.add_argument("file2",
                        type=str,
                        help="the path to the file containing the second sentence",
                        metavar="file2")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ids",
                       nargs=2,
                       type=str,
                       required=False,
                       help="the ids of the sentences to compare",
                       metavar=("id1", "id2"))
    group.add_argument("--doc",
                       action="store_true",
                       help="compute the tree edit distance for every pair of parallel sentences in a treebank")

    parser.add_argument("--deprel",
                        action="store_true",
                        help="compare dependency relation")
    parser.add_argument("--upos",
                        action="store_true",
                        help="compare universal dependency tags")

    # Parse arguments
    args = parser.parse_args()

    # Execute program
    if args.doc:
        start = time.time()
        dist = avg_ud_ted(file1=args.file1,
                          file2=args.file2,
                          deprel=args.deprel,
                          upos=args.upos)
        end = time.time()
    else:
        start = time.time()
        dist = ud_ted(file1=args.file1,
                      file2=args.file2,
                      id1=args.ids[0] if args.ids else None,
                      id2=args.ids[1] if args.ids else None,
                      deprel=args.deprel,
                      upos=args.upos)
        end = time.time()
    print(f"Tree edit distance: {dist}")
    print(f"Time: {end - start}")


if __name__ == "__main__":
    main()
