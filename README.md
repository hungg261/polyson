# Polyson

![Polyson's logo](assets/logo.png)

Offline Windows CLI tool to simulate Codeforces Polygon workflow.

> **Note:** Windows-only tool. Requires `g++` (MinGW) available in system `PATH`.

---

## Installation

Run in the root directory:

```bash
pip install -e .
```

*You can use either `polyson` or the short alias `son` for all commands.*

---

## Commands Reference

* **Create problem:** `son init <name>`
  * *Initializes a new problem folder populated with default template files.*
* **Check status:** `son status`
  * *Displays current problem metadata, configurations, and test counts.*
* **Reset problem:** `son reset`
  * *Restores all problem configuration and source template files to factory defaults.*
* **Configure properties:** `son config <alias> <value>`
  * *Aliases:* `name`, `sol`, `in`, `out`, `src`, `tl`, `ml`, `rt`, `tg`
  * *Example:* `son config tl 2000` | `son config sol solutions/my_sol.cpp`
* **Load preset checker:** `son config chk <template>`
  * *Loads standard testlib checkers (e.g., `wcmp`, `ncmp`, `yesno`, `fcmp`).*
* **Load preset validator:** `son config val <template>`
  * *Loads standard testlib validators (e.g., `ival`, `nval`, `sval`).*
* **Generate tests:** `son run`
  * *Compiles `gen.cpp`, runs `script.ftl` commands, validates inputs, and generates outputs via `solution.cpp`.*
* **Validate existing tests:** `son validate`
  * *Runs `validator.cpp` against all current custom and generated test inputs.*
* **Shuffle test cases:** `son shuffle`
  * *Randomly shuffles input/output test file contents while maintaining test file index order.*
* **Stress test (Infinite loop):** `son stress "<cmd>" <sol1> <sol2>`
  * *Generates test cases on the fly to compare two solutions until a mismatch or crash occurs.*
  * *Example:* `son stress "gen ${seed} 1 100" solutions/sol.cpp solutions/brute.cpp`
  * *Stop:* Press `Ctrl + C`
* **Open in Explorer:** `son open <path>`
  * *Opens the specified file or folder directly in Windows Explorer.*
* **Clean binaries:** `son clean`
  * *Removes compiled executables (`*.exe`) and auxiliary build files.*
