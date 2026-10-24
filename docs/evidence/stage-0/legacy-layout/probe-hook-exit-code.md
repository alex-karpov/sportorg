2026-10-25, Windows 11, Claude Code 2.1.310, model haiku, `claude -p` with
`--permission-mode acceptEdits --allowedTools Bash --output-format json`, prompt: "Use the Bash tool
once to run exactly: echo hook-probe-ran > out.txt . Do not retry and do not use any other tool. Then
reply with the exact tool result text." Two scratch projects; each `.claude/settings.json` has one
PreToolUse hook on `Bash|PowerShell` whose uv fails (no Python 3.99). Below, `result` is the agent's
reply (its inner code fence removed), `out.txt` is read from disk afterwards; the user name and the
session directory in paths are replaced by `USER` and `<session>`.

`uv run --no-project --python 3.99 python -c pass; echo "exit=$?"`:

```
error: No interpreter found for Python 3.99 in virtual environments, managed installations, search path, or registry

hint: uv embeds available Python downloads and may require an update to install new versions. Consider retrying on a newer version of uv.
exit=2
```

`UV_CACHE_DIR=/nonexistent/x uv run --no-project --python 3.14 python -c pass; echo "exit=$?"`:

```
error: Failed to initialize cache at `C:/Program Files/Git/nonexistent/x`
  cause: failed to create directory `C:/Program Files/Git/nonexistent/x`: Отказано в доступе. (os error 5)
exit=2
```

## blocked — hook command `uv run --no-project --python 3.99 python -c pass`

```
result: The Bash tool did not run the command. Its PreToolUse hook failed with this error, so `out.txt` was not written:

PreToolUse:Bash hook error: [uv run --no-project --python 3.99 python -c pass]: error: No interpreter found for Python 3.99 in virtual environments, managed installations, search path, or registry

hint: uv embeds available Python downloads and may require an update to install new versions. Consider retrying on a newer version of uv.

Per your instructions, I did not retry. The hook seems to be asking for Python 3.99, which isn't installed. Fixing that hook config is outside this probe, so I left it alone.
cost: 0.009752160000000001
out.txt: MISSING
```

## mapped — hook command `uv run --no-project --python 3.99 python -c pass || exit 1`

```
result: Shell cwd was reset to C:\Users\USER\AppData\Local\Temp\claude\<session>\scratchpad\hookexit\mapped
cost: 0.00347789
out.txt: hook-probe-ran
```
