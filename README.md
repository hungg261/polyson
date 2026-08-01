# Polyson

![Polyson's logo](assets/logo.png)

Minimalist, offline Windows CLI tool to simulate Codeforces Polygon.
**Note:** This tool is Windows-only.

## Installation

```bash
pip install -e .
```
*Note: Use either `polyson` or the short alias `son`.*

## Commands

* **Create problem:** `son init <name>`
* **Configure keys:** `son config <alias> <value>`
  * *Aliases:* `name`, `sol`, `in`, `out`, `src`, `tl`, `ml`, `rt`, `tg`
  * *Load checker:* `son config chk <template>`
  * *Load validator:* `son config val <template>`
* **Generate tests:** `son run`
* **Validate tests:** `son validate`
* **Stress test (Infinite):** `son stress "<cmd>" <sol1> <sol2>`
  * *Example:* `son stress "gen ${seed} 1 100" solutions/sol.cpp solutions/brute.cpp`
  * *Stop:* Press `Ctrl + C`
* **Check status:** `son status`
* **Reset problem:** `son reset`
* **Open explorer:** `son open <path>`
* **Clean workspace:** `son clean`
