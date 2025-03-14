"""git_solutions.py

This is the git solutions functions to setup repos that would contain solutions
and a private repository with those keys
"""

__author__ = "neo154"
__version__ = '0.1.0'
__all__ = ['configure_solution_info_repo', 'add_new_challenges_repo', 'zip_and_store']

import json
import os
import tempfile
from pathlib import Path

import git
from git.exc import GitError, InvalidGitRepositoryError
from .solution_zipper import create_zip_file

RESERVED_NAME = 'solution_info_repo'

def _get_repo_url(repo: git.Repo) -> str:
    """
    _get_repo_url Little helper to get git url

    Args:
        repo (git.Repo): Repo object being used

    Raises:
        ValueError: If number of remote URLS for repo is not 1

    Returns:
        str: Returns single url for the git repo
    """
    urls = list(repo.remote().urls)
    if len(urls) < 1:
        raise ValueError("Provided doesn't have a remote URL")
    if len(urls) > 1:
        raise ValueError("Provided has more than 1 remote URL, not supported")
    return urls[0]

def _check_private_repo(test_repo: git.Repo) -> bool:
    """
    _check_private_repo Check repo, identifies if is likely private or not

    Args:
        test_repo (git.Repo): Repo object for a supposedly private repo

    Raises:
        ValueError: If https base git or not in github, all I need for now

    Returns:
        bool: Whether or not repo is able to be anonymously accessed
    """
    orig_dir = Path.cwd()
    url = _get_repo_url(test_repo)
    if not url.startswith('https://') and not "github.com" not in url:
        raise ValueError(f"Only support https:// urls, got{url}")
    url = url.replace('https://github.com', 'https://null:null@github.com')
    print(f"Checking if {url.split('/')[-1]} repo is private")
    likely_private = False
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        print("Attempting  unauthed pull of repo")
        try:
            git.Repo.clone_from(url, to_path='./')
            print("Could pull repo, somethign wrong?")
        except GitError:
            print("Couldn't pull repo, hopefully private")
            likely_private = True
        os.chdir(orig_dir)
    return likely_private

def configure_solution_info_repo(solution_info_proj_path: Path, config_path: Path=None) -> None:
    """
    configure_solution_info_repo Configures solution info repo that will contain the solutions
    collection of repos, challenge name, and password for the zip

    Args:
        solution_info_proj_path (Path): Path to solution info git project
        config_path (Path, optional): Path to the config for this tool. Defaults to None.

    Raises:
        NotADirectoryError: Configi parent isn't a directory
        FileNotFoundError: If the config path exists but isn't a file
        FileExistsError: If config already exisits, only need to do initial config once
        ValueError: Solutions repo isn't a git project or confirmed to anonymously pulled
    """
    print("Identifying configuration paths")
    if config_path is None:
        config_path = Path.home().joinpath('.solution_info/config.json')
    if not config_path.parent.exists():
        config_path.parent.mkdir(511, True, False)
    if not config_path.parent.is_dir():
        raise NotADirectoryError(f"Config parent isn't a directory: {config_path.parent}")
    if config_path.exists() and not config_path.is_file():
        raise FileNotFoundError(f"Config file path isn't a file obj {config_path}")
    if config_path.exists():
        raise FileExistsError('Config file already exists, solution info proj should be there')
    try:
        solution_info_repo = git.Repo(solution_info_proj_path)
    except InvalidGitRepositoryError as invalid_git_err:
        raise ValueError("solution info project path not a git") from invalid_git_err
    if not _check_private_repo(solution_info_repo):
        raise ValueError("Solutions info repo may not be private, check and try again")
    config = {
        RESERVED_NAME: str(solution_info_proj_path.absolute().resolve())
    }
    with config_path.open('w', encoding='utf-8') as config_ref:
        json.dump(config, config_ref, indent=2)
    print("Configuration complete")

def add_new_challenges_repo(challenges_repo_path: Path, repo_name: str=None,
        config_path: Path=None) -> None:
    """
    add_new_challenges_repo Adds a challenges repo such as a git for leetcode, HTB, etc. to
    management config for full zip and push to github

    Args:
        challenges_repo_path (Path): Path object for a challenge repo,  must be configured git
        repo_name (str, optional): Name of the repo for config and print messages.
            Defaults to dir_name.
        config_path (Path, optional): Configuration path. Defaults to None.

    Raises:
        FileNotFoundError: If Config isn't found
        NotADirectoryError: If challenge repo isn't found or isn't a dir
        ValueError: Challenge repo isn't configured git repo or can't use the name for config
    """
    print("Checking configuration file")
    if config_path is None:
        config_path = Path.home().joinpath('.solution_info/config.json')
    if not config_path.exists():
        raise FileNotFoundError(f"Cannot find configuration file at {config_path}")
    if not challenges_repo_path.is_dir():
        raise NotADirectoryError(f"Cannot find provided challenges repo")
    print("Checking repo path")
    try:
        challenge_repo = git.Repo(challenges_repo_path)
    except InvalidGitRepositoryError as invalid_git_err:
        raise ValueError("solution info project path not a git") from invalid_git_err
    with config_path.open('r', encoding='utf-8') as config_ref:
        tmp_config = json.load(config_ref)
    url = _get_repo_url(challenge_repo)
    if repo_name is None:
        repo_name = url.split('/')[-1]
    if repo_name == RESERVED_NAME:
        raise ValueError(f"Cannot use {repo_name}, reserved name")
    if repo_name in tmp_config:
        raise ValueError(f"Repo with name {repo_name} alread is found in config")
    tmp_config[repo_name] = str(challenges_repo_path.absolute().resolve())
    with config_path.open('w', encoding='utf-8') as config_ref:
        json.dump(tmp_config, config_ref, indent=2)
    print(f"Added {repo_name} to challenges manager")

def zip_and_store(solution_dir: Path, config_path: Path=None, password: str=None,
        exclude_files: list[str]=None, max_file_size: int=None) -> None:
    """
    zip_and_store Zips solution, stores the password in private solutions repo and then publishes
    a new branch for both using the name of the challenge and solution for both repos

    Args:
        solution_dir (Path): Path to solution work directory
        config_path (Path, optional): Configuration file path for solution zipper.
            Defaults to None.
        password (str, optional): Password to use for encrypting zip, recommended to use
            flag.txt or root.txt for security challenges. Defaut is to genreate a new one.
        exclude_files (list[str], optional): List of names of files to exlude from zip.
            Defaults to None.
        max_file_size (int, optional): Max file size in bytes to exlucde if they exceed this size.
            Defaults to None.

    Raises:
        FileNotFoundError: If configuration file isn't found
        ValueError: Solution's parent directory system can't be found in challenge repos
        NotADirectoryError: Directory path for solution in the solution-info repo is taken
        FileExistsError: Zipped solution password is already stored for this solution
    """
    print("Checking configuration file")
    if config_path is None:
        config_path = Path.home().joinpath('.solution_info/config.json')
    if not config_path.exists():
        raise FileNotFoundError(f"Cannot find configuration file at {config_path}")
    with config_path.open('r', encoding='utf-8') as config_ref:
        tmp_config: dict[str, str] = json.load(config_ref)
    # Try to identify this thing based on solution dir
    repo_name = None
    solution_dir = solution_dir.absolute().resolve()
    solution_name = solution_dir.name
    solution_parent = solution_dir.parent
    for key, value in tmp_config.items():
        if key!=RESERVED_NAME and str(solution_parent) in value:
            repo_name = key
            print(f"Located solution in project {repo_name}")
            solution_git_path = value
            break
    if repo_name is None:
        raise ValueError(
            f"Not able to locate solution in config file: {solution_dir}. Add and try again")
    solution_info_path = Path(tmp_config[RESERVED_NAME])
    zip_pass = create_zip_file(solution_dir, password, exclude_files, max_file_size)
    solution_zip_file = solution_dir.parent.joinpath(f'{solution_dir.name}.zip')
    solution_info_repo = git.Repo(solution_info_path)
    print("Attempting to get solution zip info into repo")
    if solution_info_repo.active_branch.name!='main':
        solution_info_repo.git.checkout('main')
    print("Checking for solution-info repo updates")
    solution_info_repo.remote('origin').pull('main')
    solution_info_repo.create_head(f'{repo_name}_{solution_name}').checkout()
    # Adding files
    print("Attempting to add solution zip info")
    if solution_info_path.joinpath(repo_name).exists() \
            and not solution_info_path.joinpath(repo_name).is_dir():
        raise NotADirectoryError(
            f"This name is already taken as a file in solution repo: {repo_name}")
    if not solution_info_path.joinpath(repo_name).exists():
        solution_info_path.joinpath(repo_name).mkdir()
    if solution_info_path.joinpath(repo_name).joinpath(solution_name).exists():
        raise FileExistsError(
            f"Solution {solution_name} already found in challenge section {repo_name}")
    with solution_info_path.joinpath(repo_name).joinpath(solution_name)\
            .open('w', encoding='utf-8') as file_ref:
        _ = file_ref.write(zip_pass)
    solution_info_repo.index.add(str(
        solution_info_path.joinpath(repo_name).joinpath(solution_name)))
    solution_info_repo.index.commit(f'Adding zip info in {repo_name} for solution {solution_name}')
    print("Local commit created")
    solution_info_repo.remote('origin').push(
        f'{repo_name}_{solution_name}:{repo_name}_{solution_name}').raise_if_error()
    print("Solution info for new zip created")
    solution_info_repo.git.checkout('main')
    print("Attempting to push file into solution repo")
    solution_repo = git.Repo(solution_git_path)
    if solution_repo.active_branch.name!='main':
        solution_repo.git.checkout('main')
    solution_repo.remote('origin').pull('main')
    solution_repo.create_head(solution_name).checkout()
    solution_repo.index.add(str(solution_zip_file))
    print(f"Adding zip for {solution_name}")
    solution_repo.index.commit(f'Adding solution zip for {solution_name}')
    solution_repo.remote('origin').push(f'{solution_name}:{solution_name}').raise_if_error()
    print(f"Pushed solution zip to repo")
    solution_repo.git.checkout('main')
    print("Solution successfully added, both branches are ready for PR")
