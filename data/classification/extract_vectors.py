#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""extract_vectors.py extracts values for classificators from XML files from reports.
   Their paths are passed in `checked_vectors` file and the values are written to `vectors` file.
"""

import sys

import readers

def print_report_data(path):
    for vector, flag, operation, benchmark, uuid in readers.read_report(path):
        print(uuid, operation, str(flag), " ".join(vector))

def main():
    filename = "checked_vectors"
    if len(sys.argv) >= 2:
        filename = sys.argv[1]

    paths = readers.read_checked_vectors(filename)
    for p in paths:
        print_report_data(p)

if __name__ == "__main__":
    main()
