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

__version__ = "0.1.0"

import argparse
import time

from ud_ted.distance import ud_ted, doc_ud_ted


def main():
    """
    The main script that reads the command line arguments and computes the tree edit distance of the input.
    """
    # Create parser
    parser = argparse.ArgumentParser(description="Compute the tree edit distance between two Universal Dependencies "
                                                 "dependency trees")

    # Add arguments
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument("file1",
                        type=str,
                        help="the path to the file containing the first sentence",
                        metavar="file1")
    parser.add_argument("file2",
                        type=str,
                        help="the path to the file containing the second sentence",
                        metavar="file2")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--timeout",
                       nargs=1,
                       type=float,
                       required=False,
                       help="timeout in seconds",
                       metavar="n")
    group.add_argument("--ordered",
                       action="store_true",
                       help="compute the ordered tree edit distance")

    group = parser.add_mutually_exclusive_group(required=True)
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
        dist = doc_ud_ted(file1=args.file1,
                          file2=args.file2,
                          timeout=args.timeout[0] if args.timeout else None,
                          ordered=args.ordered,
                          deprel=args.deprel,
                          upos=args.upos)
        end = time.time()
    else:
        start = time.time()
        dist = ud_ted(file1=args.file1,
                      file2=args.file2,
                      timeout=args.timeout[0] if args.timeout else None,
                      ordered=args.ordered,
                      id1=args.ids[0] if args.ids else None,
                      id2=args.ids[1] if args.ids else None,
                      deprel=args.deprel,
                      upos=args.upos)
        end = time.time()
    print(f"Tree edit distance: {dist}")
    print(f"Time: {end - start}")


if __name__ == "__main__":
    main()
