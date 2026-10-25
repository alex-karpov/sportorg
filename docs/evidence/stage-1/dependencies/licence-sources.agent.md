# Licences from primary sources: `sportident`, PySide6, `Unicode-3.0` (agent judgement)

This file is agent judgement, not script output; no human reviewed it. It answers report question 4
after the maintainer's decision `[мейнтейнер: 2026-10-25]`: Р2 is a package-metadata error, the licence
is GPL-3.0-or-later.

Sources of the facts:
- **"re-verified"**: the main session's agent (Claude Code, Opus 5.5, 2026-10-25) checked the fact
  against the Stage 1 cache `~/.cache/sportorg-stage1/` (SHA-256 in its `MANIFEST.json`) or against the
  legacy pin.
- **"review session"**: another agent session downloaded and read the files on 2026-10-25
  (`/tmp/claude-1000/si/`, `/tmp/claude-1000/u/`; temporary, may be gone). The hashes below let anyone
  download the files again and compare.

Person names are limited to the copyright holders named in licence notices, because attribution is
the question. Commit authors are not listed (Stage 1 rule 4).

## `sportident` 1.2.8 (runtime dependency of legacy)

| Fact | Source | Checked |
|---|---|---|
| PyPI JSON: `license` = `GPLv3+`, no `license_expression`, classifier `License :: Other/Proprietary License`, home page `https://github.com/sportorg/sireader` | `https://pypi.org/pypi/sportident/1.2.8/json`, cache `pypi/sportident==1.2.8.json` | re-verified |
| sdist `sportident-1.2.8.tar.gz` SHA-256 `be1afe931a6986e9acd847274ba72e805e114e3cf0014738b5c342fc0a52938b` | the same JSON, `urls[].digests` | re-verified (digest in JSON); download compared in the review session |
| wheel `sportident-1.2.8-py3-none-any.whl` SHA-256 `ad66dd66d67aa0bbabea0069868e70e0c426c14db5187f7015aa120b82a9761d` | the same JSON | re-verified (digest in JSON); download compared in the review session |
| sdist `pyproject.toml`: `[tool.poetry] license = "GPLv3+"`; wheel `WHEEL`: `Generator: poetry-core 1.9.0` | the sdist and the wheel | review session |
| `sportident.py` header: GPL "version 3 of the License, or (at your option) any later version" | the sdist | review session |
| `LICENSE` in sdist and wheel is the GPL-3.0 text. Against `https://www.gnu.org/licenses/gpl-3.0.txt` it differs only in whitespace and four links: `http://` instead of `https://`, and in one of them the older path `philosophy/why-not-lgpl.html` instead of `licenses/why-not-lgpl.html` (the path difference was added on 2026-10-25 after the independent check; `diff -w` over the review session's files) | the sdist, the wheel, gnu.org (the local copy of the gnu.org file from the review session has SHA-256 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`; its download was not repeated) | review session; the diff re-run by the agent |
| Why the classifier says "Proprietary": poetry-core turns an unknown licence id such as `GPLv3+` into a licence that is not OSI-approved, and its `classifier_name` for such a licence returns `Other/Proprietary License`. The author did not choose the classifier | poetry-core 1.9.0 `src/poetry/core/spdx/helpers.py:33-35`, `src/poetry/core/spdx/license.py:153-158` (sdist SHA-256 `fa7a4001eae8aa572ee84f35feb510b321bd652e5cf9293249d62853e1f935a2`) | review session |
| `sportorg/sireader` is a GitHub fork of `gaudenz/sireader`; the GitHub API reports `GPL-3.0` for both; tag `v1.2.8` = `c21fec5`; git blob of `sportident.py` at the tag and in the sdist is `dc11df24b52084c1497e42be01845afd784b7e78` | `gh api repos/sportorg/sireader`, clone of the repository | review session |
| The original `sireader.py` begins with the copyright notices of Gaudenz Steinlin (2008–2014) and Simon Harston (2014). Commit `d209fef` (2019-11-23) removed both lines; in v1.2.8 only a thank-you comment remains (`sportident.py:214`). The README does not say it is a fork | clone of `sportorg/sireader`: `git log -S"Gaudenz Steinlin"` | review session |

**Conclusion** `[допущение]` (no lawyer):
- the licence of `sportident` 1.2.8 is GPL-3.0-or-later, compatible with the project licence;
- the PyPI classifier is a build-tool artefact.

The project's `scripts/check_licenses.py` puts classifiers above the free `License` field (ADR-0004 row 7). So it would report `sportident` as a runtime problem. ADR-0004 records a single-package exception, tied to the hashes above.

**Removed attribution** (report discrepancy Р7, a licence question):
- whether removing the notices breaks GPLv3 §4/§5 is not claimed;
- the new project keeps the attribution of both copyright holders if it uses this code;
- the question to the `sportorg/sireader` maintainer is in TASK-10.

## PySide6

| Fact | Source | Checked |
|---|---|---|
| Verdict "unknown" only for 6.6.3.1, which the legacy lock needs only under Python 3.8 (Windows 7) | `python-packages.md` (script output) | re-verified |
| 6.10.0 declares `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, verdict `ok` | `python-packages.md` | re-verified |

"Proprietary" in the classifiers is Qt's commercial alternative under dual licensing `[допущение]`. On Python 3.14 the project has no question. LGPL duties for a frozen build (the user can replace Qt) belong to the installer stage.

## `Unicode-3.0` (crate `unicode-ident` 1.0.24)

| Fact | Source | Checked |
|---|---|---|
| crates.io: licence `(MIT OR Apache-2.0) AND Unicode-3.0`, checksum `e6e4313cd5fcd3dad5cafa179702e2b244f760991f45397d14d4ebf38247da75` | crates.io API, cache `crates/unicode-ident==1.0.24.json` | re-verified |
| The same checksum in the legacy `Cargo.lock` | `[код: pysport@b548c35 Cargo.lock]` | re-verified |
| SPDX License List 3.29.0: `Unicode-3.0`, "Unicode License v3", OSI-approved, not deprecated | `https://spdx.org/licenses/Unicode-3.0.json` | review session |
| FSF: "a lax, permissive, free software license, compatible with all versions of the GNU GPL"; the condition is to keep the copyright and permission notice | `https://www.gnu.org/licenses/license-list.html#Unicodev3` | review session |
| `Unicode-3.0` covers only the tables generated from UCD 17.0.0 (`src/tables.rs`); `LICENSE-UNICODE` matches the SPDX text | the `.crate` file | review session |
| In legacy the crate is a direct dependency of `proc-macro2` and `syn` only, and enters through them → `pyo3-macros`/`quote` → `pyo3`, i.e. at compile time for procedural macros (`syn` was added on 2026-10-25 after the independent check) | `[код: pysport@b548c35 Cargo.lock]` | re-verified (dependency lists in `Cargo.lock`); that it is absent from the built `cdylib` is `[допущение]` |

**Conclusion:** compatible with GPL-3.0.
- Nothing changes while the project has no Rust.
- When Rust appears, `Unicode-3.0` goes into the allowlist of `scripts/check_licenses.py` with a line in ADR-0004.
