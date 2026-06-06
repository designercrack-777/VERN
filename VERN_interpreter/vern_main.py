#!/usr/bin/env python3
"""VERN interpreter entry point — invoked as: vern <file.vern>"""

import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: vern <file.vern>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    # executor.py is the sole entry into the interpreter stack
    from executor import execute_file
    execute_file(path)

if __name__ == '__main__':
    main()
