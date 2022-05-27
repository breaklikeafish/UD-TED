import argparse

from ud_ted.distance import ud_ted


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
    parser.add_argument("--ids",
                        nargs=2,
                        type=str,
                        required=False,
                        help="the ids of the sentences to compare",
                        metavar=("id1", "id2"))

    # Parse arguments
    args = parser.parse_args()

    # Execute program
    dist = ud_ted(args)
    print(f"Tree edit distance: {dist}")


if __name__ == "__main__":
    main()
