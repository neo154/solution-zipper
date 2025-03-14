"""solution_zipper.py

Contains the variables and functions for creating zips for solution files
"""

__author__ = "neo154"
__version__ = '0.1.0'
__all__ = ['create_zip_file']

import os
import secrets
from pathlib import Path

import pyzipper

DEFAULT_MAX_SIZE = 1073741824 # 1GB

def _add_file(zip_ref: pyzipper.AESZipFile, f_path: Path, max_file_size: int,
        exclude_files: list[str], parents: Path=None):
    """
    _add_file Handler for adding file or directory and all subfiles to `AESZipFile` object

    Args:
        zip_ref (pyzipper.AESZipFile): Encrypted zip file reference
        f_path (Path): Path of file to add
        max_file_size (int): Max file size that will be compressed in bytes
        exclude_files (list[str]): List of file names, can be dir name, to not add/ignore
        parents (Path, optional): Parent path, just for recursive call. Defaults to None.

    Raises:
        ValueError: If file found isn't a directory or normal file
    """
    if parents is None:
        parents = Path()
    file_stat = f_path.stat()
    if f_path.name in exclude_files:
        print(f"{f_path.name} is in exclude file names list, ignoring for zip")
        return
    if f_path.is_file():
        if file_stat.st_size < DEFAULT_MAX_SIZE:
            tmp_ref = parents.joinpath(f_path.name)
            print(f"Adding {tmp_ref} to zip")
            zip_ref.write(tmp_ref)
        else:
            print(f"{f_path} was larger than {max_file_size} bytes, not adding to zip")
    elif f_path.is_dir():
        for sub_path in f_path.iterdir():
            _add_file(zip_ref, sub_path, max_file_size, exclude_files,
                parents.joinpath(f_path.name))
    else:
        raise ValueError(f'{f_path} not a file or directory')

def create_zip_file(solution_dir: Path, password: str=None, exclude_files: list[str]=None,
        max_file_size: int=DEFAULT_MAX_SIZE) -> str:
    """
    create_zip_file Provided some directory containing a solultion, will create an encrypted zip
    file containing all components in solution, and returning password for storage

    Not intended for any high end security, just trying to make sure that the GitHub zips that
    contain spoilers are protected but can be opened by intended people/groups

    Args:
        solution_dir (Path): Path to solution directory
        password (str, optional): Password to encrypt, either flag for CTF/HTB.
            Default is None, creates it's own version used for things like leetCode.
        exclude_files (list[Path], optional): List of file names to exclude. Defaults to None.
        max_file_size (int, optional): Max size of a file to be added to compressed file, in bytes.
            Defaults to 1GB.

    Raises:
        FileExistsError: If solution related zipfile already exists
        FileNotFoundError: If solution directory provided doesn't exist or can't be found
        NotADirectoryError: If path for solution isn't a directory

    Returns:
        str: Password for decrypting zipfile
    """
    zip_path = solution_dir.parent.joinpath(f'{solution_dir.name}.zip')
    if zip_path.exists():
        raise FileExistsError(f"Cannot create another zip file in the same location {zip_path}")
    if not solution_dir.exists():
        raise FileNotFoundError(f"Solution directory is not found {solution_dir}")
    if not solution_dir.is_dir():
        raise NotADirectoryError(f"Solution paths needs to be a directory to zip everything")
    if password is None:
        # Safe enough here
        password = secrets.token_urlsafe(20)
    if exclude_files is None:
        exclude_files = []
    orig_dir = Path.cwd()
    os.chdir(solution_dir.parent)
    print(f"Creating {zip_path.name}")
    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip_ref:
        zip_ref.setpassword(password.encode('ascii'))
        _add_file(zip_ref, solution_dir, max_file_size, exclude_files)
    os.chdir(orig_dir)
    return password
