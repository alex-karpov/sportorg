# Stubs of the legacy API used by the oracle driver

Hand-written `.pyi` files for the part of `sportorg` (pysport@b548c35) and `orjson` that
`scripts/oracle_driver/driver.py` calls, so basedpyright checks the driver (Python 3.8 environment in
`pyproject.toml`) without the legacy checkout, also in CI (ADR-0009 T3). They declare only what the
driver uses. They are a contract, not a copy: the integration tests in
`tests/scripts/oracle/test_oracle_cli.py` run the driver against the real legacy code.
