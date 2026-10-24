fsmode on Windows-11-10.0.26300-SP0 | python 3.14.8 | C:\Program Files\Git\usr\bin\bash.EXE

files 0o444, directories 0o555 (Windows: only the file read-only attribute applies)

| case | exit | effect on .legacy | message |
|---|---|---|---|
| append with >> | 1 | unchanged | /usr/bin/bash: line 1: .legacy/pysport/probe.txt: Permission denied |
| sed -i | 0 | .legacy/pysport/probe.txt: MODIFIED |  |
| cp a new file into the tree | 0 | .legacy/pysport/new.txt: CREATED |  |
| mv a file | 0 | .legacy/pysport/moved.txt: CREATED; .legacy/pysport/probe.txt: DELETED |  |
| rm -f a file | 0 | .legacy/pysport/sub/deep.txt: DELETED |  |
| rm -rf the tree | 0 | .legacy/pysport/probe.txt: DELETED; .legacy/pysport/sub/deep.txt: DELETED |  |
| git rm inside the clone | 0 | .legacy/pysport/probe.txt: DELETED |  |
| chmod u+w, then append | 0 | .legacy/pysport/probe.txt: MODIFIED |  |
| python open(..., 'a') | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     open('.legacy/pysport/probe.txt', 'a').write('x')     ~~~~^^^^^^^^^^^^^^^^^^^^^^^^ |
| python os.remove | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     import os; os.remove('.legacy/pysport/sub/deep.txt')                ~~~~~~~~~^^^^^ |
| PowerShell Set-Content | 1 | unchanged | Set-Content : Отказано в доступе по пути "C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba 943f-a1a1-4392-906f-fe77b312b7f2\scratch |
| PowerShell Remove-Item | 1 | unchanged | Remove-Item : Cannot remove item C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba943f-a1a1 -4392-906f-fe77b312b7f2\scratchpad\probe |
| PowerShell Remove-Item -Force | 0 | .legacy/pysport/sub/deep.txt: DELETED |  |
| PowerShell Remove-Item -Recurse -Force | 0 | .legacy/pysport/probe.txt: DELETED; .legacy/pysport/sub/deep.txt: DELETED |  |

files 0o444, directories 0o555 (Windows: only the file read-only attribute applies) + inherited deny ACE for USER on .legacy: WriteData, AppendData, WriteExtendedAttributes, WriteAttributes, Delete, DeleteSubdirectoriesAndFiles

| case | exit | effect on .legacy | message |
|---|---|---|---|
| append with >> | 1 | unchanged | /usr/bin/bash: line 1: .legacy/pysport/probe.txt: Permission denied |
| sed -i | 4 | unchanged | sed: couldn't open temporary file .legacy/pysport/sed4RSWSg: Permission denied |
| cp a new file into the tree | 1 | unchanged | cp: cannot create regular file '.legacy/pysport/new.txt': Permission denied |
| mv a file | 1 | unchanged | mv: cannot move '.legacy/pysport/probe.txt' to '.legacy/pysport/moved.txt': Permission denied |
| rm -f a file | 1 | unchanged | rm: cannot remove '.legacy/pysport/sub/deep.txt': Permission denied |
| rm -rf the tree | 1 | unchanged | rm: cannot remove '.legacy/pysport/.git/COMMIT_EDITMSG': Permission denied rm: cannot remove '.legacy/pysport/.git/config': Permission denied rm: cannot remove  |
| git rm inside the clone | 128 | unchanged | fatal: Unable to create 'C:/Users/USER/AppData/Local/Temp/claude/C--Users-USER-Prog-Orient-sportorg/dcba943f-a1a1-4392-906f-fe77b312b7f2/scratchpad/probe-fs-win/. |
| chmod u+w, then append | 1 | unchanged | chmod: changing permissions of '.legacy/pysport/probe.txt': Permission denied |
| python open(..., 'a') | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     open('.legacy/pysport/probe.txt', 'a').write('x')     ~~~~^^^^^^^^^^^^^^^^^^^^^^^^ |
| python os.remove | 1 | unchanged | Traceback (most recent call last):   File "<string>", line 1, in <module>     import os; os.remove('.legacy/pysport/sub/deep.txt')                ~~~~~~~~~^^^^^ |
| PowerShell Set-Content | 1 | unchanged | Set-Content : Access to the path 'C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba943f-a1a 1-4392-906f-fe77b312b7f2\scratchpad\prob |
| PowerShell Remove-Item | 1 | unchanged | Remove-Item : Cannot remove item C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba943f-a1a1 -4392-906f-fe77b312b7f2\scratchpad\probe |
| PowerShell Remove-Item -Force | 1 | unchanged | Remove-Item : Cannot remove item C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba943f-a1a1 -4392-906f-fe77b312b7f2\scratchpad\probe |
| PowerShell Remove-Item -Recurse -Force | 1 | unchanged | Remove-Item : Cannot remove item C:\Users\USER\AppData\Local\Temp\claude\C--Users-USER-Prog-Orient-sportorg\dcba943f-a1a1 -4392-906f-fe77b312b7f2\scratchpad\probe |
