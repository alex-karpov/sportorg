# Claude Code configuration facts (collected 2026-10-24, Claude Code 2.1.310)

Collected by a documentation-reading subagent from https://code.claude.com/docs/en/ (permissions.md,
hooks.md, memory.md, settings.md, settings-reference.md, sandboxing.md, plugins/install.md,
plugins/loading.md, plugin-evals) and verified in this session where marked **[verified here]**.

## Permission rules
- Path forms: `//path` absolute from filesystem root (Windows paths are normalised, `C:\Users\x` → `//c/Users/x`),
  `~/path` home, `/path` relative to the settings file's project, `path`/`./path` relative to cwd. No `../` form
  is documented. **[verified here]**: `Edit(../_deny_probe/**)` did not block an Edit; `Edit(//c/Users/USER/Prog/Orient/_deny_probe/**)`
  blocked it with "File is in a directory that is denied by your permission settings".
- `Write(...)` rules never match; use `Edit(...)` for Write/NotebookEdit/MultiEdit. A Read deny also covers Edit/Write
  and recognised Bash file commands; Glob/Grep coverage is best-effort. Bash rules match command text only and are not a
  security boundary.
- `permissions.deny` lists merge across settings files; a deny at any level wins; `settings.local.json` cannot remove a
  committed deny. `permissions.blockReadsOutsideWorkingDirectories` (2.1.257+) exists as a blunter alternative.
- No OS sandbox on native Windows (macOS, Linux, WSL2 only).

## Hooks
- `PostToolUse` matcher `Edit|Write` (exact list; other characters make it a regex); stdin JSON carries
  `tool_input.file_path` (absolute). `timeout` in seconds (default 600). `${CLAUDE_PROJECT_DIR}` is exported.
  Default shell on Windows is Git Bash, or PowerShell when Git Bash is absent (`"shell": "powershell"` to force).
- `Stop` input has `stop_hook_active`; block with exit 2 (stderr to Claude) or `{"decision":"block","reason":...}`;
  8 consecutive stop-hook continuations are capped.
- `PreToolUse` may return `hookSpecificOutput.permissionDecision` = `allow|deny|ask|defer` with
  `permissionDecisionReason`; deny > defer > ask > allow; hooks cannot override deny/ask rules.
- **[verified here]**: a hook that fails (exit 1, e.g. `uv run` erroring on a broken `.venv`) blocks the tool call;
  a PreToolUse hook that depends on the project venv therefore locks every tool when the venv breaks. Guard hooks must
  not depend on the project environment (`uv run --no-project`).
- Hooks from committed `.claude/settings.json` were picked up by the running session without restart **[verified here]**.

## CLAUDE.md imports
- `@AGENTS.md` on its own line inlines the file; relative to the importing file; nesting up to 4 hops; imports in code
  spans are ignored; symlinks discouraged on Windows. Claude Code 2.1.277+ reads AGENTS.md directly only when no
  CLAUDE.md exists.

## Plugins
- Project scope: `enabledPlugins` in `.claude/settings.json` (committed); collaborators still run
  `claude plugin install <name>@<marketplace> --scope project` once. Official marketplace: `claude-plugins-official`.
- `claude plugin eval` (≥ 2.1.269): cases under the plugin's eval directory (`evals/` or `--eval-dir`); case =
  `prompt.md` (frontmatter `name, tags, plugins, runs, max_turns, timeout_seconds, …`) + `graders/*.md`
  (`regex`, `tool_used`, `tool_order`, `file_exists` free; `llm`, `baseline` judge calls) + optional `case.yaml`
  (`schema_version "1.1"`, `context.scaffold_script|history_file|add_dirs`). `plugins: ["../.."]` names the plugin
  directory relative to the case. `--ablation with-without` adds a no-plugin arm; `tool_used: Skill` graders are
  plugin-fired indicators, not score. `--max-cost-usd` is a list-price ceiling checked before each run (exit 2 on
  partial). Shell-granting suites need a sandbox backend: WSL2 on Windows. **[verified here]**: with an installed
  plugin as target, cases are read from the plugin's own directory, not from the current repo.
