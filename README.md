# solution-zipper
Simple python tool to zip solutions to CTF, HTB, or coding solutions with a password. Just intended for personal use

Just point the script towards the directory that contains the solution and all notes/details that you had and zip them up.

```sh
# Example here is just for a random leet code solution
ls 1_two_sum/
main.go

# Want to store this but not have a spoiler
zip_solution 1_two_sum
Creating 1_two_sum.zip
Adding main.go to zip
Solution data zipped
```

This just creates the simple zip for a leetcode solution I don't want to spoil for others.

For HTB or CTF related ones, I would recommend just using the flag in order for the password

```sh
# This would also have notes, scans etc. but this is just an exmaple
ls HTB_Chemistry
user.txt
root.txt

zip_solution HTB_Chemistry --password <root flag>
Creating HTB_Chemistry.zip
Adding user.txt to zip
Adding root.txt to zip
Solution data zipped
```

There are other options to help not store super large blobs that shouldn't be pushed to github or even just exlude certain names.

## Simple zipper

```sh
zip_solution --help
usage: zip_solution zipper [-h] [--password PASSWORD] [--max_file_size MAX_FILE_SIZE] [--remove_stored_files] solution_dir

positional arguments:
  solution_dir          Path to directory containing solution to challenge

options:
  -h, --help            show this help message and exit
  --password PASSWORD   Password to encrypt the solution with, for CTF/HTB like challenges the flag is recommended
  --max_file_size MAX_FILE_SIZE
                        Number of bytes a file can be to be added to solution zip file, default is 1GB
  --remove_stored_files
                        If we should remove the files after they have been stored in solution zipfile
```

## Managing Solutions with git

To do this, you need to configure zip_solution to your private solution info repo, and then add challenge repos for where solutions that are being zipped and pushed into git will be.

All will need to be repos, and the solution-info one containing info to unzip solution zips is stored in a private repo.

To Configure
```sh
zip_solution manage_solution configure -h
usage: solution_zipper manage_solution configure [-h] [--config_path CONFIG_PATH] solution_info_repo

positional arguments:
  solution_info_repo    Path to the solution info repo, does a check to make sure it's private

options:
  -h, --help            show this help message and exit
  --config_path CONFIG_PATH
                        Path to configuration file for solution_zipper for handling gits fully
```

To Add a Challenge Repo
```sh
zip_solution manage_solution add_challenge_repo -h
usage: solution_zipper manage_solution add_challenge_repo [-h] [--repo_name REPO_NAME] [--config_path CONFIG_PATH] challenge_repo

positional arguments:
  challenge_repo        Path to challenge repo to add for configuration

options:
  -h, --help            show this help message and exit
  --repo_name REPO_NAME
                        Name of the challenge repo for config file, defaults to dir name
  --config_path CONFIG_PATH
                        Path to configuration file for solution_zipper for handling gits fully
```

After configuration, to have zip created and the zip pushed along with it's unzip info to your repos
```sh
zip_solution manage_solution zip_and_store -h
usage: solution_zipper manage_solution zip_and_store [-h] [--config_path CONFIG_PATH] [--password PASSWORD] [--max_file_size MAX_FILE_SIZE]
                                                     [--exclude_files EXCLUDE_FILES [EXCLUDE_FILES ...]]
                                                     solution_dir

positional arguments:
  solution_dir          Path to directory containing solution to challenge

options:
  -h, --help            show this help message and exit
  --config_path CONFIG_PATH
                        Path to configuration file for solution_zipper for handling gits fully
  --password PASSWORD   Password to encrypt the solution with, for CTF/HTB like challenges the flag is recommended
  --max_file_size MAX_FILE_SIZE
                        Number of bytes a file can be to be added to solution zip file, default is 1GB
  --exclude_files EXCLUDE_FILES [EXCLUDE_FILES ...]
                        List of filenames to ignore/not store in zip
```
