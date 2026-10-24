fsmode on Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.43 | python 3.14.4 | /usr/bin/bash

files 0o444, directories 0o555

| case | exit | effect on .legacy | message |
|---|---|---|---|
| append with >> | 1 | unchanged | /usr/bin/bash: line 1: .legacy/pysport/probe.txt: Permission denied |
| sed -i | 4 | unchanged | sed: couldn't open temporary file .legacy/pysport/sed6m46iX: Permission denied |
| cp a new file into the tree | 1 | unchanged | cp: cannot create regular file '.legacy/pysport/new.txt': Permission denied |
| mv a file | 1 | unchanged | mv: cannot move '.legacy/pysport/probe.txt' to '.legacy/pysport/moved.txt': Permission denied |
| rm -f a file | 1 | unchanged | rm: cannot remove '.legacy/pysport/sub/deep.txt': Permission denied |
| rm -rf the tree | 1 | unchanged | rm: cannot remove '.legacy/pysport/probe.txt': Permission denied rm: cannot remove '.legacy/pysport/.git/logs/refs/heads/master': Permission denied rm: cannot r |
| git rm inside the clone | 128 | unchanged | fatal: Unable to create '/home/USER/probe-fs-linux/.legacy/pysport/.git/index.lock': Permission denied |
| chmod u+w, then append | 0 | .legacy/pysport/probe.txt: MODIFIED |  |
| python open(..., 'a') | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     open('.legacy/pysport/probe.txt', 'a').write('x')     ~~~~^^^^^^^^^^^^^^^^^^^^^^^^ |
| python os.remove | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     import os; os.remove('.legacy/pysport/sub/deep.txt')                ~~~~~~~~~^^^^^ |
