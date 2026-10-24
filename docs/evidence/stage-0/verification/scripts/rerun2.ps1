# check.py exit code with output kept: once to a file, once to NUL.
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
Set-Location "$HOME\sportorg"
cmd /d /c "uv run python scripts/check.py --keep-going > C:\share\check-to-file.txt 2>&1"
[IO.File]::AppendAllText('C:\share\check-to-file.txt', "[exit $LASTEXITCODE] output to file`r`n")
cmd /d /c "uv run python scripts/check.py --keep-going > nul 2> C:\share\check-to-nul-stderr.txt"
[IO.File]::AppendAllText('C:\share\check-to-nul-stderr.txt', "[exit $LASTEXITCODE] stdout to NUL`r`n")
git status --porcelain --untracked-files=all > C:\share\git-status.txt 2>&1
[IO.File]::AppendAllText('C:\share\git-status.txt', "[exit $LASTEXITCODE] git status`r`n")
