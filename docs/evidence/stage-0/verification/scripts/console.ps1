# README step 4 in a real console window (no redirection of the tools' output); only exit codes go to the share.
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
Set-Location "$HOME\sportorg"
$r = @("console $(Get-Date -Format o) | code page: $((chcp) -join ' ') | OutputEncoding: $([Console]::OutputEncoding.WebName)")
uv run python scripts/check.py
$r += "[exit $LASTEXITCODE] uv run python scripts/check.py"
uv run lint-imports
$r += "[exit $LASTEXITCODE] uv run lint-imports"
uv run python -c "import sys, locale; print(sys.stdout.encoding, locale.getpreferredencoding(), sys.stdout.isatty())" | Out-Null
$r += "[exit $LASTEXITCODE] python encoding probe"
$enc = uv run python -c "import sys, locale; print(sys.stdout.encoding, locale.getpreferredencoding())"
$r += "redirected python stdout encoding / preferred: $enc"
$r | Set-Content -Path 'C:\share\console-exit.txt' -Encoding ASCII
