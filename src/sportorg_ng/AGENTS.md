# src/sportorg_ng — layer rules

Placeholder layout until the Stage 4 architecture ADR; enforced now by import-linter (`pyproject.toml`).

- `core/` — domain model and rules. Imports only the standard library (never `os`, `sys`, `subprocess`,
  `socket`) and pure third-party libraries approved by an ADR. Never imports `adapters`, `ui`,
  `national`, device, GUI or platform libraries.
- `adapters/` — files, devices, network, printing, OS. Implements ports defined in `core`.
- `ui/` — user interface. Nothing imports `ui`.
- `national/<cc>/` — optional national packages (`ru` first). `core` and `adapters` never import them;
  the test suite must stay green with every national package removed.

Every public function is fully typed. Rules are data (decision tables with a clause citation), not
`if sport == ...` branches in the core.
