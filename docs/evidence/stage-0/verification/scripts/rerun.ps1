# Exit codes of steps 6-17 (the first run lost them when writes to the shared log failed).
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
$Out = 'C:\share\rerun-exit-codes.txt'
[IO.File]::WriteAllText($Out, "rerun $(Get-Date -Format o) (same sandbox, warm state)`r`n")
$Repo = 'https://github.com/alex-karpov/sportorg.git'
$Proj = "$HOME\sportorg"
New-Item -ItemType Directory -Force "$env:TEMP\clones" | Out-Null
$steps = @(
  @("$env:TEMP\clones", "git clone $Repo default-branch"),
  @("$env:TEMP\clones", "git clone --branch stage-0 $Repo stage-0"),
  @("$HOME\verbatim\sportorg", 'uv sync'),
  @($Proj, 'uv sync'),
  @($Proj, 'uv run python scripts/check.py'),
  @($Proj, 'uvx pre-commit install'),
  @($Proj, 'uvx pre-commit run --all-files'),
  @($Proj, 'uv audit'),
  @($Proj, 'uv run python -m scripts.check_licenses')
)
foreach ($s in $steps) {
  Push-Location $s[0]
  cmd /d /c "$($s[1]) >nul 2>&1"
  $code = $LASTEXITCODE
  Pop-Location
  [IO.File]::AppendAllText($Out, ('[exit {0}] {1} | {2}' -f $code, $s[1], $s[0]) + "`r`n")
}
[IO.File]::AppendAllText($Out, "done`r`n")
