# Python vulnerabilities: pysport@b548c35

Produced by `scripts/archaeology/dependencies.py` (command in `commands.txt`). Sources:
- `uv.lock`, `pyproject.toml`, `Cargo.lock` of pysport@b548c35, read through git.
- PyPI JSON cache `pypi/`: 123 files, combined SHA-256 `e9b1748f101858e955c478cbca6dfaa0a2c539fe9b0c3a502817c7993d60df5e` (per-file values in `summary.json`).
- OSV query cache `osv/`: 137 files, combined SHA-256 `bcb3e2bb59deee80aba743695999f08c84f14d977553d74287c68cfcc074690c` (per-file values in `summary.json`).
- crates.io JSON cache `crates/`: 14 files, combined SHA-256 `7e2071bea42e7e76a4a8c7eb75c08b04013065a548fc8b99598ed4d5234446a7` (per-file values in `summary.json`).
- `tools/uv-audit-legacy.json`: SHA-256 `838867634555d674066ca1fd387317fc84cbf3e0c0ea6dbbe346ee44e6d13c48`.
- `tools/osv-scanner-legacy.json`: SHA-256 `af422970dc30e04aa2c84f8654cff385d9a3062dd9fdeb4d964b1621f7cb26dd`.

| package | version | class | py3.8-only | id | aliases | label | CVSS | fixed |
|---|---|---|---|---|---|---|---|---|
| aiohttp | 3.10.11 | runtime | yes | GHSA-2fqr-mr3j-6wp8 | CVE-2026-54279, PYSEC-2026-2112 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-2g87-pp6c-29x5 | - | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-2vrm-gr82-f7m5 | CVE-2026-34514, PYSEC-2026-2096 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-3wq7-rqq7-wx6j | CVE-2026-34517, PYSEC-2026-2099 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-494j-54xm-rwp3 | CVE-2026-111063 | LOW | - | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-4fvr-rgm6-gqmc | CVE-2026-54273, PYSEC-2026-2107 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-4m7w-qmgq-4wj5 | CVE-2026-54275, PYSEC-2026-237 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-54jq-c3m8-4m76 | CVE-2025-69226, PYSEC-2026-1097 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-5wr8-gcqf-gqf3 | CVE-2026-111064 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-63hf-3vf5-4wqf | CVE-2026-34520, PYSEC-2026-2102 | LOW | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-63hw-fmq6-xxg2 | CVE-2026-54277, PYSEC-2026-2110 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-69f9-5gxw-wvc2 | CVE-2025-69224, PYSEC-2026-1099 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-6cjc-53gc-5rqm | CVE-2026-111065 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-6jhg-hg63-jvvf | CVE-2025-69228, PYSEC-2026-1100 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-6mq8-rvhq-8wgg | CVE-2025-69223, PYSEC-2026-1101 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-9548-qrrj-x5pj | CVE-2025-53643, PYSEC-2026-1104 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.12.14 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-966j-vmvw-g2g9 | CVE-2026-34518, PYSEC-2026-2100 | LOW | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-9x8q-7h8h-wcw9 | CVE-2026-54280, PYSEC-2026-2113 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-9xw5-w5jj-pvcg | CVE-2026-111066 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-c427-h43c-vf67 | CVE-2026-34525, PYSEC-2026-2103 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-cq5v-8q36-5273 | CVE-2026-69244, PYSEC-2026-3545 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-f9xw-jh8m-3mwq | CVE-2026-111748 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-fh55-r93g-j68g | CVE-2025-69230, PYSEC-2026-1105 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-g3cq-j2xw-wf74 | CVE-2026-54278, PYSEC-2026-2111 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-g84x-mcqj-x9qq | CVE-2025-69229, PYSEC-2026-1106 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-gx76-c99x-2c96 | CVE-2026-111749 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-hcc4-c3v8-rx92 | CVE-2026-34513, PYSEC-2026-2095 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-hg6j-4rv6-33pg | CVE-2026-47265, PYSEC-2026-2105 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-hpj7-wq8m-9hgp | CVE-2026-54276, PYSEC-2026-2109 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-jg22-mg44-37j8 | CVE-2026-34993, PYSEC-2026-2104 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:H/A:L | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-jj3x-wxrx-4x23 | CVE-2025-69227, PYSEC-2026-1107 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-m5qp-6w8w-w647 | CVE-2026-34516, PYSEC-2026-2098 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-m6qw-4cw2-hm4m | CVE-2026-50269, PYSEC-2026-2106 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-mfx4-hv73-q22v | CVE-2026-69243, PYSEC-2026-3546 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-mq44-7p77-q5h7 | CVE-2026-59881, PYSEC-2026-3547 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-mqqc-3gqh-h2x8 | CVE-2025-69225, PYSEC-2026-1109 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-mwh4-6h8g-pg8w | CVE-2026-34519, PYSEC-2026-2101 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-p998-jp59-783m | CVE-2026-34515, PYSEC-2026-2097 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-pqxq-w44r-73xw | CVE-2026-111750 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L | 3.14.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-w2fm-2cpv-w7v5 | CVE-2026-22815, PYSEC-2026-2094 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | GHSA-xcgm-r5h9-7989 | CVE-2026-54274, PYSEC-2026-2108 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1097 | CVE-2025-69226, GHSA-54jq-c3m8-4m76 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1099 | CVE-2025-69224, GHSA-69f9-5gxw-wvc2 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1100 | CVE-2025-69228, GHSA-6jhg-hg63-jvvf | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1101 | CVE-2025-69223, GHSA-6mq8-rvhq-8wgg | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1104 | CVE-2025-53643, GHSA-9548-qrrj-x5pj | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.12.14 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1105 | CVE-2025-69230, GHSA-fh55-r93g-j68g | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1106 | CVE-2025-69229, GHSA-g84x-mcqj-x9qq | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1107 | CVE-2025-69227, GHSA-jj3x-wxrx-4x23 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-1109 | CVE-2025-69225, GHSA-mqqc-3gqh-h2x8 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2094 | CVE-2026-22815, GHSA-w2fm-2cpv-w7v5 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2095 | CVE-2026-34513, GHSA-hcc4-c3v8-rx92 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2096 | CVE-2026-34514, GHSA-2vrm-gr82-f7m5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2097 | CVE-2026-34515, GHSA-p998-jp59-783m | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2098 | CVE-2026-34516, GHSA-m5qp-6w8w-w647 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2099 | CVE-2026-34517, GHSA-3wq7-rqq7-wx6j | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2100 | CVE-2026-34518, GHSA-966j-vmvw-g2g9 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2101 | CVE-2026-34519, GHSA-mwh4-6h8g-pg8w | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2102 | CVE-2026-34520, GHSA-63hf-3vf5-4wqf | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2103 | CVE-2026-34525, GHSA-c427-h43c-vf67 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2104 | CVE-2026-34993, GHSA-jg22-mg44-37j8 | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2105 | CVE-2026-47265, GHSA-hg6j-4rv6-33pg | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2106 | CVE-2026-50269, GHSA-m6qw-4cw2-hm4m | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.0 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2107 | CVE-2026-54273, GHSA-4fvr-rgm6-gqmc | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2108 | CVE-2026-54274, GHSA-xcgm-r5h9-7989 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2109 | CVE-2026-54276, GHSA-hpj7-wq8m-9hgp | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2110 | CVE-2026-54277, GHSA-63hw-fmq6-xxg2 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2111 | CVE-2026-54278, GHSA-g3cq-j2xw-wf74 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2112 | CVE-2026-54279, GHSA-2fqr-mr3j-6wp8 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-2113 | CVE-2026-54280, GHSA-9x8q-7h8h-wcw9 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-237 | CVE-2026-54275, GHSA-4m7w-qmgq-4wj5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-3545 | CVE-2026-69244, GHSA-cq5v-8q36-5273 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.3 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-3546 | CVE-2026-69243, GHSA-mfx4-hv73-q22v | - | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.10.11 | runtime | yes | PYSEC-2026-3547 | CVE-2026-59881, GHSA-mq44-7p77-q5h7 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.13.1 | runtime | no | GHSA-2fqr-mr3j-6wp8 | CVE-2026-54279, PYSEC-2026-2112 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-2g87-pp6c-29x5 | - | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-2vrm-gr82-f7m5 | CVE-2026-34514, PYSEC-2026-2096 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-3wq7-rqq7-wx6j | CVE-2026-34517, PYSEC-2026-2099 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-494j-54xm-rwp3 | CVE-2026-111063 | LOW | - | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-4fvr-rgm6-gqmc | CVE-2026-54273, PYSEC-2026-2107 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-4m7w-qmgq-4wj5 | CVE-2026-54275, PYSEC-2026-237 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-54jq-c3m8-4m76 | CVE-2025-69226, PYSEC-2026-1097 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-5wr8-gcqf-gqf3 | CVE-2026-111064 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-63hf-3vf5-4wqf | CVE-2026-34520, PYSEC-2026-2102 | LOW | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-63hw-fmq6-xxg2 | CVE-2026-54277, PYSEC-2026-2110 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-69f9-5gxw-wvc2 | CVE-2025-69224, PYSEC-2026-1099 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-6cjc-53gc-5rqm | CVE-2026-111065 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-6jhg-hg63-jvvf | CVE-2025-69228, PYSEC-2026-1100 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-6mq8-rvhq-8wgg | CVE-2025-69223, PYSEC-2026-1101 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-966j-vmvw-g2g9 | CVE-2026-34518, PYSEC-2026-2100 | LOW | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-9x8q-7h8h-wcw9 | CVE-2026-54280, PYSEC-2026-2113 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-9xw5-w5jj-pvcg | CVE-2026-111066 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-c427-h43c-vf67 | CVE-2026-34525, PYSEC-2026-2103 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-cq5v-8q36-5273 | CVE-2026-69244, PYSEC-2026-3545 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-f9xw-jh8m-3mwq | CVE-2026-111748 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-fh55-r93g-j68g | CVE-2025-69230, PYSEC-2026-1105 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-g3cq-j2xw-wf74 | CVE-2026-54278, PYSEC-2026-2111 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-g84x-mcqj-x9qq | CVE-2025-69229, PYSEC-2026-1106 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-gx76-c99x-2c96 | CVE-2026-111749 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-hcc4-c3v8-rx92 | CVE-2026-34513, PYSEC-2026-2095 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-hg6j-4rv6-33pg | CVE-2026-47265, PYSEC-2026-2105 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | GHSA-hpj7-wq8m-9hgp | CVE-2026-54276, PYSEC-2026-2109 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | GHSA-jg22-mg44-37j8 | CVE-2026-34993, PYSEC-2026-2104 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:H/A:L | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | GHSA-jj3x-wxrx-4x23 | CVE-2025-69227, PYSEC-2026-1107 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-m5qp-6w8w-w647 | CVE-2026-34516, PYSEC-2026-2098 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-m6qw-4cw2-hm4m | CVE-2026-50269, PYSEC-2026-2106 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | GHSA-mfx4-hv73-q22v | CVE-2026-69243, PYSEC-2026-3546 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.13.1 | runtime | no | GHSA-mq44-7p77-q5h7 | CVE-2026-59881, PYSEC-2026-3547 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.13.1 | runtime | no | GHSA-mqqc-3gqh-h2x8 | CVE-2025-69225, PYSEC-2026-1109 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | GHSA-mwh4-6h8g-pg8w | CVE-2026-34519, PYSEC-2026-2101 | LOW | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-p998-jp59-783m | CVE-2026-34515, PYSEC-2026-2097 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-pqxq-w44r-73xw | CVE-2026-111750 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L | 3.14.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-w2fm-2cpv-w7v5 | CVE-2026-22815, PYSEC-2026-2094 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | GHSA-xcgm-r5h9-7989 | CVE-2026-54274, PYSEC-2026-2108 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1097 | CVE-2025-69226, GHSA-54jq-c3m8-4m76 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1099 | CVE-2025-69224, GHSA-69f9-5gxw-wvc2 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1100 | CVE-2025-69228, GHSA-6jhg-hg63-jvvf | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1101 | CVE-2025-69223, GHSA-6mq8-rvhq-8wgg | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1105 | CVE-2025-69230, GHSA-fh55-r93g-j68g | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1106 | CVE-2025-69229, GHSA-g84x-mcqj-x9qq | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1107 | CVE-2025-69227, GHSA-jj3x-wxrx-4x23 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-1109 | CVE-2025-69225, GHSA-mqqc-3gqh-h2x8 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U | 3.13.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2094 | CVE-2026-22815, GHSA-w2fm-2cpv-w7v5 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2095 | CVE-2026-34513, GHSA-hcc4-c3v8-rx92 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2096 | CVE-2026-34514, GHSA-2vrm-gr82-f7m5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2097 | CVE-2026-34515, GHSA-p998-jp59-783m | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2098 | CVE-2026-34516, GHSA-m5qp-6w8w-w647 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2099 | CVE-2026-34517, GHSA-3wq7-rqq7-wx6j | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2100 | CVE-2026-34518, GHSA-966j-vmvw-g2g9 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2101 | CVE-2026-34519, GHSA-mwh4-6h8g-pg8w | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2102 | CVE-2026-34520, GHSA-63hf-3vf5-4wqf | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2103 | CVE-2026-34525, GHSA-c427-h43c-vf67 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N | 3.13.4 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2104 | CVE-2026-34993, GHSA-jg22-mg44-37j8 | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2105 | CVE-2026-47265, GHSA-hg6j-4rv6-33pg | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2106 | CVE-2026-50269, GHSA-m6qw-4cw2-hm4m | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.0 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2107 | CVE-2026-54273, GHSA-4fvr-rgm6-gqmc | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2108 | CVE-2026-54274, GHSA-xcgm-r5h9-7989 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2109 | CVE-2026-54276, GHSA-hpj7-wq8m-9hgp | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2110 | CVE-2026-54277, GHSA-63hw-fmq6-xxg2 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2111 | CVE-2026-54278, GHSA-g3cq-j2xw-wf74 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2112 | CVE-2026-54279, GHSA-2fqr-mr3j-6wp8 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-2113 | CVE-2026-54280, GHSA-9x8q-7h8h-wcw9 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-237 | CVE-2026-54275, GHSA-4m7w-qmgq-4wj5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.14.1 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-3545 | CVE-2026-69244, GHSA-cq5v-8q36-5273 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 3.14.3 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-3546 | CVE-2026-69243, GHSA-mfx4-hv73-q22v | - | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N | 3.14.2 |
| aiohttp | 3.13.1 | runtime | no | PYSEC-2026-3547 | CVE-2026-59881, GHSA-mq44-7p77-q5h7 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.14.2 |
| certifi | 2025.10.5 | runtime | no | GHSA-6q48-6c7w-9gw2 | PYSEC-2026-4320 | CRITICAL | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2026.10.19 |
| certifi | 2025.10.5 | runtime | no | PYSEC-2026-4320 | GHSA-6q48-6c7w-9gw2 | - | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2026.10.19 |
| cryptography | 46.0.6 | runtime | no | GHSA-537c-gmf6-5ccf | - | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 48.0.1 |
| cryptography | 46.0.6 | runtime | no | GHSA-g6cj-pr64-35w5 | CVE-2026-69247, PYSEC-2026-3552 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N | 50.0.0 |
| cryptography | 46.0.6 | runtime | no | GHSA-jwv3-5hgf-82ww | CVE-2026-69249, PYSEC-2026-3553 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 49.0.0 |
| cryptography | 46.0.6 | runtime | no | GHSA-m2h6-j472-rp4c | CVE-2026-69248, PYSEC-2026-3554 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:P | 49.0.0 |
| cryptography | 46.0.6 | runtime | no | GHSA-p423-j2cm-9vmq | CVE-2026-39892, PYSEC-2026-36 | MODERATE | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 46.0.7 |
| cryptography | 46.0.6 | runtime | no | PYSEC-2026-3552 | CVE-2026-69247, GHSA-g6cj-pr64-35w5 | - | CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N | 50.0.0 |
| cryptography | 46.0.6 | runtime | no | PYSEC-2026-3553 | CVE-2026-69249, GHSA-jwv3-5hgf-82ww | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N | 49.0.0 |
| cryptography | 46.0.6 | runtime | no | PYSEC-2026-3554 | CVE-2026-69248, GHSA-m2h6-j472-rp4c | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:P | 49.0.0 |
| cryptography | 46.0.6 | runtime | no | PYSEC-2026-36 | CVE-2026-39892, GHSA-p423-j2cm-9vmq | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H | 46.0.7 |
| filelock | 3.20.0 | dev | no | GHSA-qmgc-5h2g-mvrw | CVE-2026-22701, PYSEC-2026-1374 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H | 3.20.3 |
| filelock | 3.20.0 | dev | no | GHSA-w853-jp5j-5j7f | CVE-2025-68146, PYSEC-2026-1375 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H | 3.20.1 |
| filelock | 3.20.0 | dev | no | PYSEC-2026-1374 | CVE-2026-22701, GHSA-qmgc-5h2g-mvrw | - | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H | 3.20.3 |
| filelock | 3.20.0 | dev | no | PYSEC-2026-1375 | CVE-2025-68146, GHSA-w853-jp5j-5j7f | - | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H | 3.20.1 |
| idna | 3.11 | runtime | no | GHSA-65pc-fj4g-8rjx | CVE-2026-45409, PYSEC-2026-215 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N | 3.15 |
| idna | 3.11 | runtime | no | PYSEC-2026-215 | CVE-2026-45409, GHSA-65pc-fj4g-8rjx | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 3.15 |
| lief | 0.14.1 | dev | yes | GHSA-377p-g8gr-5wpg | CVE-2024-31636, PYSEC-2024-280 | LOW | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N | 0.15.0 |
| lief | 0.14.1 | dev | yes | GHSA-mjjp-xjfg-97wg | CVE-2025-15504, PYSEC-2026-1538 | LOW | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 0.17.2 |
| lief | 0.14.1 | dev | yes | PYSEC-2024-280 | CVE-2024-31636, GHSA-377p-g8gr-5wpg | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N | - |
| lief | 0.14.1 | dev | yes | PYSEC-2026-1538 | CVE-2025-15504, GHSA-mjjp-xjfg-97wg | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 0.17.2 |
| lief | 0.17.0 | dev | no | GHSA-mjjp-xjfg-97wg | CVE-2025-15504, PYSEC-2026-1538 | LOW | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 0.17.2 |
| lief | 0.17.0 | dev | no | PYSEC-2026-1538 | CVE-2025-15504, GHSA-mjjp-xjfg-97wg | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 0.17.2 |
| lxml | 6.0.2 | runtime | no | GHSA-vfmq-68hx-4jfw | CVE-2026-41066, PYSEC-2026-87 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 6.1.0 |
| lxml | 6.0.2 | runtime | no | PYSEC-2026-87 | CVE-2026-41066, GHSA-vfmq-68hx-4jfw | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 6.1.0 |
| multidict | 6.7.0 | runtime | no | GHSA-54p9-h82j-f925 | CVE-2026-104874, PYSEC-2026-4244 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 6.9.1 |
| multidict | 6.7.0 | runtime | no | PYSEC-2026-4244 | CVE-2026-104874, GHSA-54p9-h82j-f925 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 6.9.1 |
| orjson | 3.10.15 | runtime | yes | GHSA-hx9q-6w63-j58v | CVE-2025-67221, PYSEC-2026-107 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P | 3.11.6 |
| orjson | 3.10.15 | runtime | yes | PYSEC-2026-107 | CVE-2025-67221, GHSA-hx9q-6w63-j58v | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.11.5 |
| orjson | 3.11.3 | runtime | no | GHSA-hx9q-6w63-j58v | CVE-2025-67221, PYSEC-2026-107 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P | 3.11.6 |
| orjson | 3.11.3 | runtime | no | PYSEC-2026-107 | CVE-2025-67221, GHSA-hx9q-6w63-j58v | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.11.5 |
| pygments | 2.19.2 | dev | no | GHSA-5239-wwwm-4pmq | CVE-2026-4539, PYSEC-2026-2987 | LOW | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 2.20.0 |
| pygments | 2.19.2 | dev | no | PYSEC-2026-2987 | CVE-2026-4539, GHSA-5239-wwwm-4pmq | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L; CVSS_V4: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P | 2.20.0 |
| pytest | 8.3.5 | dev | yes | GHSA-6w46-j5rx-g56g | CVE-2025-71176, PYSEC-2026-1845 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L | 9.0.3 |
| pytest | 8.3.5 | dev | yes | PYSEC-2026-1845 | CVE-2025-71176, GHSA-6w46-j5rx-g56g | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L | 9.0.3 |
| pytest | 8.4.2 | dev | no | GHSA-6w46-j5rx-g56g | CVE-2025-71176, PYSEC-2026-1845 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L | 9.0.3 |
| pytest | 8.4.2 | dev | no | PYSEC-2026-1845 | CVE-2025-71176, GHSA-6w46-j5rx-g56g | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L | 9.0.3 |
| requests | 2.32.4 | runtime | yes | GHSA-gc5v-m9x4-r6x2 | CVE-2026-25645, PYSEC-2026-2275 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N | 2.33.0 |
| requests | 2.32.4 | runtime | yes | PYSEC-2026-2275 | CVE-2026-25645, GHSA-gc5v-m9x4-r6x2 | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N | 2.33.0 |
| requests | 2.32.5 | runtime | no | GHSA-gc5v-m9x4-r6x2 | CVE-2026-25645, PYSEC-2026-2275 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N | 2.33.0 |
| requests | 2.32.5 | runtime | no | PYSEC-2026-2275 | CVE-2026-25645, GHSA-gc5v-m9x4-r6x2 | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N | 2.33.0 |
| setuptools | 69.5.1 | runtime | yes | GHSA-5rjg-fvgr-3xxf | BIT-setuptools-2025-47273, CVE-2025-47273, PYSEC-2025-49 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P | 78.1.1 |
| setuptools | 69.5.1 | runtime | yes | GHSA-cx63-2mw6-8hw5 | BIT-setuptools-2024-6345, CVE-2024-6345, PYSEC-2026-1918 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N | 70.0.0 |
| setuptools | 69.5.1 | runtime | yes | GHSA-h35f-9h28-mq5c | BIT-setuptools-2026-59890, CVE-2026-59890, PYSEC-2026-3447 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N | 83.0.0 |
| setuptools | 69.5.1 | runtime | yes | GHSA-xmj3-9gf7-h52w | - | LOW | CVSS_V4: CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:A/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N | 84.1.0 |
| setuptools | 69.5.1 | runtime | yes | PYSEC-2025-49 | BIT-setuptools-2025-47273, CVE-2025-47273, GHSA-5rjg-fvgr-3xxf | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H | 250a6d17978f9f6ac3ac887091f2d32886fbbb0b, 78.1.1 |
| setuptools | 69.5.1 | runtime | yes | PYSEC-2026-1918 | BIT-setuptools-2024-6345, CVE-2024-6345, GHSA-cx63-2mw6-8hw5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N | 70.0.0 |
| setuptools | 69.5.1 | runtime | yes | PYSEC-2026-3447 | BIT-setuptools-2026-59890, CVE-2026-59890, GHSA-h35f-9h28-mq5c | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N | 83.0.0 |
| setuptools | 80.9.0 | runtime | no | GHSA-h35f-9h28-mq5c | BIT-setuptools-2026-59890, CVE-2026-59890, PYSEC-2026-3447 | MODERATE | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N | 83.0.0 |
| setuptools | 80.9.0 | runtime | no | GHSA-xmj3-9gf7-h52w | - | LOW | CVSS_V4: CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:A/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N | 84.1.0 |
| setuptools | 80.9.0 | runtime | no | PYSEC-2026-3447 | BIT-setuptools-2026-59890, CVE-2026-59890, GHSA-h35f-9h28-mq5c | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N | 83.0.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-2xpw-w6gg-jr37 | CVE-2025-66471, PYSEC-2026-1994 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-38jv-5279-wg99 | CVE-2026-21441, PYSEC-2026-1996 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.3 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-48p4-8xcf-vxj5 | CVE-2025-50182, PYSEC-2026-1997 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 2.5.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-8988-9cw3-xx77 | CVE-2026-97687, PYSEC-2026-4175 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2.8.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-gm62-xv2j-4w53 | CVE-2025-66418, PYSEC-2026-1998 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-pq67-6m6q-mj2v | CVE-2025-50181, PYSEC-2026-1999 | MODERATE | CVSS_V3: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 2.5.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-qccp-gfcp-xxvc | CVE-2026-44431, PYSEC-2026-141 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N; CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N | 2.7.0 |
| urllib3 | 2.2.3 | runtime | yes | GHSA-vxq7-64xx-v4gw | CVE-2026-97689, PYSEC-2026-4177 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.8.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-141 | CVE-2026-44431, GHSA-qccp-gfcp-xxvc | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N | 2.7.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-1994 | CVE-2025-66471, GHSA-2xpw-w6gg-jr37 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-1996 | CVE-2026-21441, GHSA-38jv-5279-wg99 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.3 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-1997 | CVE-2025-50182, GHSA-48p4-8xcf-vxj5 | - | CVSS_V3: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 2.5.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-1998 | CVE-2025-66418, GHSA-gm62-xv2j-4w53 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-1999 | CVE-2025-50181, GHSA-pq67-6m6q-mj2v | - | CVSS_V3: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 2.5.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-4175 | CVE-2026-97687, GHSA-8988-9cw3-xx77 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2.8.0 |
| urllib3 | 2.2.3 | runtime | yes | PYSEC-2026-4177 | CVE-2026-97689, GHSA-vxq7-64xx-v4gw | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.8.0 |
| urllib3 | 2.5.0 | runtime | no | GHSA-2xpw-w6gg-jr37 | CVE-2025-66471, PYSEC-2026-1994 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.5.0 | runtime | no | GHSA-38jv-5279-wg99 | CVE-2026-21441, PYSEC-2026-1996 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.3 |
| urllib3 | 2.5.0 | runtime | no | GHSA-8988-9cw3-xx77 | CVE-2026-97687, PYSEC-2026-4175 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2.8.0 |
| urllib3 | 2.5.0 | runtime | no | GHSA-gm62-xv2j-4w53 | CVE-2025-66418, PYSEC-2026-1998 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.5.0 | runtime | no | GHSA-qccp-gfcp-xxvc | CVE-2026-44431, PYSEC-2026-141 | HIGH | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N; CVSS_V4: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N | 2.7.0 |
| urllib3 | 2.5.0 | runtime | no | GHSA-vxq7-64xx-v4gw | CVE-2026-97689, PYSEC-2026-4177 | HIGH | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.8.0 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-141 | CVE-2026-44431, GHSA-qccp-gfcp-xxvc | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N | 2.7.0 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-1994 | CVE-2025-66471, GHSA-2xpw-w6gg-jr37 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-1996 | CVE-2026-21441, GHSA-38jv-5279-wg99 | - | CVSS_V3: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H; CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.3 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-1998 | CVE-2025-66418, GHSA-gm62-xv2j-4w53 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.6.0 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-4175 | CVE-2026-97687, GHSA-8988-9cw3-xx77 | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 2.8.0 |
| urllib3 | 2.5.0 | runtime | no | PYSEC-2026-4177 | CVE-2026-97689, GHSA-vxq7-64xx-v4gw | - | CVSS_V4: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H | 2.8.0 |
| wheel | 0.43.0 | dev | yes | GHSA-8rrh-rw8j-w5fx | CVE-2026-24049, PYSEC-2026-2047 | HIGH | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H | 0.46.2 |
| wheel | 0.43.0 | dev | yes | PYSEC-2026-2047 | CVE-2026-24049, GHSA-8rrh-rw8j-w5fx | - | CVSS_V3: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H | 0.46.2 |
