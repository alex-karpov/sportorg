# README clean-install probe for Windows. Runs inside Windows Sandbox under Windows PowerShell 5.1.
# Every README step runs in a child process; the log records command, directory, output and exit code.
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
$Share = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log = Join-Path $Share 'clean-install-windows.log'
$Done = Join-Path $Share 'done.txt'
$Tmp = Join-Path $env:TEMP 'probe'
$Repo = 'https://github.com/alex-karpov/sportorg.git'
New-Item -ItemType Directory -Force $Tmp | Out-Null
Set-Content -Path $Log -Value "Clean-install probe $(Get-Date -Format o)" -Encoding UTF8

function Write-Log([string]$text) { Add-Content -Path $Log -Value $text -Encoding UTF8 }

function Update-PathFromRegistry {
  # What a newly opened shell sees after installers changed the Machine/User PATH.
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}

$script:n = 0
function Invoke-Step([string]$title, [string]$shell, [string]$command, [string]$dir) {
  $script:n++
  $out = Join-Path $Tmp "out$($script:n).txt"
  if ($shell -eq 'cmd') {
    $file = Join-Path $Tmp "step$($script:n).cmd"
    Set-Content -Path $file -Value "@echo off`r`n$command" -Encoding ASCII
    $runner = "`"$file`""
  } else {
    $file = Join-Path $Tmp "step$($script:n).ps1"
    Set-Content -Path $file -Value $command -Encoding ASCII
    $runner = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$file`""
  }
  Write-Log ''
  Write-Log "######## [$($script:n)] $title"
  Write-Log "shell: $shell | dir: $dir"
  Write-Log "> $command"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  Push-Location $dir
  cmd /d /c "chcp 65001 >nul & $runner > `"$out`" 2>&1"
  $code = $LASTEXITCODE
  Pop-Location
  $sw.Stop()
  if (Test-Path $out) { Add-Content -Path $Log -Value (Get-Content -Path $out -Encoding UTF8) -Encoding UTF8 }
  Write-Log ('[exit {0}] [{1:N1} s]' -f $code, $sw.Elapsed.TotalSeconds)
}

try {
  $os = Get-CimInstance Win32_OperatingSystem
  Write-Log ('OS: {0} {1} build {2} | PowerShell {3} | user {4} | home {5}' -f $os.Caption, $os.OSArchitecture, $os.BuildNumber, $PSVersionTable.PSVersion, $env:USERNAME, $HOME)
  Write-Log 'Preinstalled tools (Get-Command):'
  foreach ($t in 'git', 'uv', 'python', 'python3', 'py', 'winget', 'curl.exe', 'pwsh') {
    $c = Get-Command $t -ErrorAction SilentlyContinue
    Write-Log ('  {0,-9} {1}' -f $t, $(if ($c) { $c.Source } else { 'not found' }))
  }

  Invoke-Step 'README step 1 verbatim (Windows PowerShell)' 'ps' 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' $HOME
  Invoke-Step 'README step 2 verbatim, same window (Windows PowerShell 5.1)' 'ps' "git clone $Repo && cd sportorg" $HOME
  Invoke-Step 'README step 2 verbatim, same window (cmd)' 'cmd' "git clone $Repo && cd sportorg" $HOME
  Invoke-Step 'README step 3 verbatim, same window' 'ps' 'uv sync' $HOME

  Write-Log ''
  Write-Log '######## DEVIATION: README does not name Git; install Git for Windows (latest GitHub release, silent)'
  try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/git-for-windows/git/releases/latest' -Headers @{ 'User-Agent' = 'clean-install-probe' }
    $asset = $rel.assets | Where-Object { $_.name -match '^Git-.*-64-bit\.exe$' } | Select-Object -First 1
    $inst = Join-Path $Tmp $asset.name
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $inst -UseBasicParsing
    Write-Log ('installer: {0} sha256 {1}' -f $asset.browser_download_url, (Get-FileHash $inst -Algorithm SHA256).Hash)
    $p = Start-Process -FilePath $inst -ArgumentList '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', '/SUPPRESSMSGBOXES' -Wait -PassThru
    Write-Log "[installer exit $($p.ExitCode)]"
  } catch { Write-Log "Git install failed: $_" }

  Write-Log ''
  Write-Log '######## NEW WINDOW: PATH reloaded from the registry (what a newly opened shell sees)'
  Update-PathFromRegistry
  Invoke-Step 'tool versions in a new window' 'ps' 'uv --version; git --version' $HOME

  New-Item -ItemType Directory -Force "$HOME\verbatim" | Out-Null
  Invoke-Step 'README step 2 verbatim, new window (cmd; default branch)' 'cmd' "git clone $Repo && cd sportorg" "$HOME\verbatim"
  Invoke-Step 'contents of the default-branch clone' 'cmd' 'dir /b /a' "$HOME\verbatim\sportorg"
  Invoke-Step 'README step 3 verbatim in the default-branch clone' 'ps' 'uv sync' "$HOME\verbatim\sportorg"

  Invoke-Step 'README step 2 with --branch stage-0, new window (cmd)' 'cmd' "git clone --branch stage-0 $Repo && cd sportorg" $HOME
  $Proj = "$HOME\sportorg"
  Invoke-Step 'clone HEAD' 'cmd' 'git rev-parse HEAD' $Proj
  Invoke-Step 'README step 3 verbatim' 'ps' 'uv sync' $Proj
  Invoke-Step 'README step 4 verbatim' 'ps' 'uv run python scripts/check.py' $Proj
  Invoke-Step 'README step 5 verbatim (optional)' 'ps' 'uvx pre-commit install' $Proj

  Invoke-Step 'extra: interpreters uv installed' 'ps' 'uv python list --only-installed' $Proj
  Invoke-Step 'extra: pre-commit on all files' 'ps' 'uvx pre-commit run --all-files' $Proj
  Invoke-Step 'extra: vulnerabilities' 'ps' 'uv audit' $Proj
  Invoke-Step 'extra: licences' 'ps' 'uv run python -m scripts.check_licenses' $Proj
} catch {
  Write-Log "PROBE ERROR: $_"
} finally {
  Write-Log ''
  Write-Log "DONE $(Get-Date -Format o)"
  Set-Content -Path $Done -Value 'done' -Encoding ASCII
}
