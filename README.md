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

```sh
solution_zipper --help
usage: solution_zipper [-h] [--password PASSWORD] [--max_file_size MAX_FILE_SIZE] [--remove_stored_files] solution_dir

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
