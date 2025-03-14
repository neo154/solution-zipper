#!/usr/bin/python3
"""cli.py

Contains main functions for using solution zipper as a cli tool
"""

import argparse
from pathlib import Path

from .git_solutions import (add_new_challenges_repo,
                           configure_solution_info_repo, zip_and_store)
from .solution_zipper import create_zip_file


def main():
    """Main method"""
    parser = argparse.ArgumentParser(prog='solution_zipper')
    sub_parser = parser.add_subparsers(required= True, dest='sub_command',
        description="Valid zipper actions")
    # Simple zipping and output passwords
    zipper_parser = sub_parser.add_parser('zipper',
        help="Just for base parser for zipping a solution and printing out zip password")
    zipper_parser.add_argument('solution_dir',
        help="Path to directory containing solution to challenge")
    zipper_parser.add_argument('--password', default=None,
        help="Password to encrypt the solution with, for CTF/HTB like challenges the flag "\
            + "is recommended")
    zipper_parser.add_argument('--max_file_size', type=int, default=None,
        help="Number of bytes a file can be to be added to solution zip file, default is 1GB")
    zipper_parser.add_argument('--exclude_files', nargs='+', default=None,
        help="List of filenames to ignore/not store in zip")
    # For zipping and git actions
    git_zipper_parser = sub_parser.add_parser('manage_solution',
        help="For having the solutions fully managed and pushed to repo, just create PRs")
    git_zip_subparser = git_zipper_parser.add_subparsers(required=True,
        description='Valid management actions', dest='management_action')
    ## Git zip configuring
    git_configure_parser = git_zip_subparser.add_parser('configure',
        help="Configures the solution-info repo location and config file for managing files")
    git_configure_parser.add_argument('solution_info_repo',
        help="Path to the solution info repo, does a check to make sure it's private")
    git_configure_parser.add_argument('--config_path', default=None,
        help="Path to configuration file for solution_zipper for handling gits fully")
    ## Git zip adding challenge repos
    git_add_ch_repo_parser = git_zip_subparser.add_parser('add_challenge_repo',
        help="Add repo for challenges such as leetcode, HTB, etc.")
    git_add_ch_repo_parser.add_argument('challenge_repo',
        help="Path to challenge repo to add for configuration")
    git_add_ch_repo_parser.add_argument('--repo_name', default=None,
        help='Name of the challenge repo for config file, defaults to dir name')
    git_add_ch_repo_parser.add_argument('--config_path', default=None,
        help="Path to configuration file for solution_zipper for handling gits fully")
    ## Git zip and store action
    git_manage_solution = git_zip_subparser.add_parser('zip_and_store',
        help="Zips the solution and stores it's password in private repo and pushes " \
            + "zip to challenge repo")
    git_manage_solution.add_argument('solution_dir',
        help="Path to directory containing solution to challenge")
    git_manage_solution.add_argument('--config_path', default=None,
        help="Path to configuration file for solution_zipper for handling gits fully")
    git_manage_solution.add_argument('--password', default=None,
        help="Password to encrypt the solution with, for CTF/HTB like challenges the flag "\
            + "is recommended")
    git_manage_solution.add_argument('--max_file_size', type=int, default=None,
        help="Number of bytes a file can be to be added to solution zip file, default is 1GB")
    git_manage_solution.add_argument('--exclude_files', nargs='+', default=None,
        help="List of filenames to ignore/not store in zip")
    options = parser.parse_args()
    print(options)
    sub_command: str = options.sub_command
    if sub_command=='zipper':
        ret_pass = create_zip_file(Path(options.solution_dir), options.password,
            options.exclude_files, options.max_file_size)
        print(f"Password to decrypt zip: {ret_pass}")
    elif sub_command=='manage_solution':
        manage_action: str = options.management_action
        config_option: str|None = options.config_path
        if isinstance(config_option, str):
            config_option = Path(config_option)
        if manage_action=='configure':
            configure_solution_info_repo(Path(options.solution_info_repo), config_option)
        elif manage_action=='add_challenge_repo':
            add_new_challenges_repo(Path(options.challenge_repo), options.repo_name, config_option)
        elif manage_action=='zip_and_store':
            zip_and_store(Path(options.solution_dir), config_option, options.password,
                options.exclude_files, options.max_file_size)
        else:
            # How did we get here?
            raise ValueError(f"Uknown management action {manage_action} provided")
    else:
        raise ValueError(f"Uknown command {sub_command} provided")

if __name__ == "__main__":
    main()
