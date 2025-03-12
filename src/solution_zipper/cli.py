#!/usr/bin/python3
"""cli.py

Contains main functions for using solution zipper as a cli tool
"""

import argparse
from pathlib import Path

from solution_zipper import create_zip_file


def main():
    """Main method"""
    parser = argparse.ArgumentParser(prog='solution_zipper')
    parser.add_argument('solution_dir', help="Path to directory containing solution to challenge")
    parser.add_argument('--password', default=None,
        help="Password to encrypt the solution with, for CTF/HTB like challenges the flag "\
            + "is recommended")
    parser.add_argument('--max_file_size', type=int, default=None,
        help="Number of bytes a file can be to be added to solution zip file, default is 1GB")
    parser.add_argument('--exclude_files', nargs='+', default=None)
    options = parser.parse_args()
    ret_pass = create_zip_file(Path(options.solution_dir), options.password,
        options.exclude_files, options.max_file_size)
    print(f"Password to decrypt zip: {ret_pass}")

if __name__ == "__main__":
    main()
