# Polyson

![Polyson's logo](assets/logo.png)

Offline Windows CLI tool to simulate Codeforces Polygon workflow.

> **Note:** Windows-only tool. Requires `g++` (MinGW) and `latexmk` (MiKTeX / TeX Live) available in system `PATH`.

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


* **Create contest:** `son contest <dir_name> [prob1 prob2 ...] [-n "Display Name"]`
  * *Initializes a contest folder with multiple problem subfolders and a `contest.json` configuration file.*
  * *Example:* `son contest fc_01 prob_a prob_b prob_c -n "Free Contest #01 <2026>"`


* **Check status:** `son status`
  * *Displays current problem or contest metadata, configurations, and test counts.*


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
  * *Runs recursively across all problems when executed inside a contest folder.*


* **Validate existing tests:** `son validate`
  * *Runs `validator.cpp` against all current custom and generated test inputs.*
  * *Runs recursively across all problems when executed inside a contest folder.*


* **Shuffle test cases:** `son shuffle`
  * *Randomly shuffles input/output test file contents while maintaining test file index order.*
  * *Runs recursively across all problems when executed inside a contest folder.*


* **Compile LaTeX PDF & Images:** `son pdf [*paths_or_contest.json] [options]`
  * *Compiles `statement.tex` from specified problem folder(s) or an entire contest into a unified PDF via `latexmk`.*
  * *Examples:*
  * `son pdf`
  * `son pdf prob_a prob_b --open`
  * `son pdf fc_01/contest.json --img`
  * `son pdf --title "Free Contest 2026" --watermark "INTERNAL USE"`


* *Options:*
  * `--img`, `--image`: Render PDF pages as PNG images (150 DPI) and automatically bundle them into a `statements.zip` file.
  * `--open`, `--view`: Automatically open the generated PDF or ZIP file upon completion.
  * `--title "<text>"`: Set a custom title for the compiled document.
  * `--subtitle "<text>"`: Set a custom subtitle for the compiled document.
  * `--open`, `--view`: Automatically open the generated PDF or ZIP file upon completion.
  * `--no-title`: Hide the title page.
  * `--no-toc`: Hide the Table of Contents.
  * `--watermark "<text>"`: Set custom watermark text.
  * `--no-watermark`: Disable watermark.
  * `--header-left "<text>"`: Custom top-left page header.
  * `--header-right "<text>"`: Custom top-right page header.




* **Stress test (Infinite loop):** `son stress "<cmd>" <sol1> <sol2>`
  * *Generates test cases on the fly to compare two solutions until a mismatch or crash occurs.*
  * *Example:* `son stress "gen ${seed} 1 100" solutions/sol.cpp solutions/brute.cpp`
  * *Stop:* Press `Ctrl + C`


* **Open in Explorer:** `son open <path>`
  * *Opens the specified file or folder directly in Windows Explorer.*


* **Clean binaries:** `son clean`
  * *Removes compiled executables (`*.exe`) and LaTeX build auxiliary files.*
  * *Cleans all sub-problem folders when executed inside a contest folder.*