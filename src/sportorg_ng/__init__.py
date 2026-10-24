"""sportorg_ng: timing and results software for orienteering and related sports.

Package layout (placeholder until the Stage 4 architecture ADR):

- ``core``     domain model and rules; imports nothing from the other packages
- ``adapters`` I/O: files, devices, network, printing
- ``ui``       user interface
- ``national`` optional national packages (``national.ru`` is the Russian one)

The boundaries are enforced by import-linter (see ``pyproject.toml``).
"""

__version__ = "0.0.1"
