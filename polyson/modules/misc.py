import json
import os
import random
import shutil
import subprocess


def open_folder(target):
    target_path = os.path.abspath(target)
    if not os.path.exists(target_path):
        print(f"[ERROR] Target location does not exist: '{target}'")
        return
    
    if os.path.isdir(target_path):
        os.startfile(target_path)
    else:
        subprocess.run(["explorer", "/select,", target_path])
    print(f"[INFO] Opened location: '{target}'")


def shuffle_tests():
    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        print(f"==================================================")
        print(f"   SHUFFLING CONTEST TESTS: {contest_data.get('contest_name', 'Unknown')}")
        print(f"==================================================")
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                print(f"\n>>> [PROBLEM: {p}]")
                os.chdir(p)
                shuffle_tests()
                os.chdir(cwd)
        return

    if not os.path.exists("problem.json") or not os.path.exists("tests"):
        print("[ERROR] problem.json or tests directory missing.")
        return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    in_ext = config.get("input_extension", ".in")
    out_ext = config.get("output_extension", ".out")

    test_pairs = []
    for f in os.listdir("tests"):
        full_path = os.path.join("tests", f)
        if os.path.isfile(full_path) and (f.endswith(in_ext) if in_ext else True):
            base_name = f[:-len(in_ext)] if in_ext else f
            if base_name.isdigit():
                out_file = f"{base_name}{out_ext}"
                out_path = os.path.join("tests", out_file)
                if os.path.exists(out_path):
                    test_pairs.append((full_path, out_path))

    if len(test_pairs) < 2:
        print("[INFO] Not enough tests to shuffle.")
        return

    contents = []
    for in_p, out_p in test_pairs:
        with open(in_p, "r", encoding="utf-8", errors="ignore") as fi, open(out_p, "r", encoding="utf-8", errors="ignore") as fo:
            contents.append((fi.read(), fo.read()))

    shuffled_contents = contents.copy()
    random.shuffle(shuffled_contents)

    for (in_p, out_p), (in_data, out_data) in zip(test_pairs, shuffled_contents):
        with open(in_p, "w", encoding="utf-8", newline='\n') as fi, open(out_p, "w", encoding="utf-8", newline='\n') as fo:
            fi.write(in_data)
            fo.write(out_data)

    print(f"[SUCCESS] Shuffled contents of {len(test_pairs)} test pairs successfully.")

def clean_workspace():
    targets = []

    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                os.chdir(p)
                clean_workspace()
                os.chdir(cwd)

    binary_targets = ["generator.exe", "solution.exe", "validator.exe", "checker.exe", "stress_sol1.exe", "stress_sol2.exe"]
    latex_extensions = [".aux", ".fdb_latexmk", ".fls", ".log", ".toc", ".synctex.gz"]
    temp_prefixes = ["stress_", "temp_"]

    for f in binary_targets:
        if os.path.exists(f):
            targets.append(f)

    if os.path.exists("problem.json"):
        try:
            with open("problem.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            checker_type = config.get("checker", "ncmp")
            builtin_checkers = ["ncmp", "wcmp", "lcmp", "rcmp", "fcmp", "uncmp", "yesno", "acmp", "case1", "casen", "lines", "nums"]
            if checker_type in builtin_checkers and os.path.exists("checker.cpp"):
                targets.append("checker.cpp")
        except Exception:
            pass

    for f in os.listdir("."):
        if os.path.isfile(f):
            if any(f.endswith(ext) for ext in latex_extensions) or any(f.startswith(pref) for pref in temp_prefixes):
                if f not in targets:
                    targets.append(f)

    if not targets:
        print("[INFO] Nothing to clean. Workspace is already clean.")
        return

    print("========================================")
    print("          FILES TO BE REMOVED           ")
    print("========================================")
    for item in targets:
        print(f" - {item}")
    print("========================================")

    confirm = input("Are you sure you want to delete these items? [y/N]: ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("[*] Clean operation cancelled.")
        return

    for item in targets:
        try:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)
            print(f"[+] Removed: {item}")
        except Exception as e:
            print(f"[!] Failed to remove {item}: {e}")


def show_status():
    orig_cwd = os.getcwd()

    if os.path.exists("contest.json"):
        try:
            with open("contest.json", "r", encoding="utf-8") as f:
                contest_data = json.load(f)
            problems = contest_data.get("problems", [])
            print("========================================")
            print("          POLYSON CONTEST STATUS        ")
            print("========================================")
            print(f" Contest Name : {contest_data.get('contest_name', 'Unknown')}")
            print(f" Problems     : {', '.join(problems)}")
            print("----------------------------------------")
            for p in problems:
                p_path = os.path.join(orig_cwd, p)
                if os.path.exists(p_path) and os.path.isdir(p_path):
                    print(f"\n[Sub-Problem: {p}]")
                    os.chdir(p_path)
                    show_status()
                    os.chdir(orig_cwd)
            print("========================================")
        finally:
            os.chdir(orig_cwd)
        return

    if not os.path.exists("problem.json"):
        print(f"[ERROR] problem.json not found in {orig_cwd}")
        return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    pkg_dir = os.path.dirname(os.path.realpath(__file__))
    possible_tpl_dirs = [
        os.path.join(pkg_dir, "templates", "sample"),
        os.path.join(pkg_dir, "polyson", "templates", "sample"),
        os.path.join(os.path.dirname(pkg_dir), "templates", "sample"),
        os.path.join(os.path.dirname(pkg_dir), "polyson", "templates", "sample")
    ]
    
    defaults_dir = None
    for chk_dir in possible_tpl_dirs:
        if os.path.exists(chk_dir) and os.path.isdir(chk_dir):
            defaults_dir = chk_dir
            break

    def normalize_code(text):
        lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        return "\n".join([line for line in lines if line])

    def check_file_status(file_path, possible_tpl_names):
        full_file_path = os.path.join(orig_cwd, file_path)
        if not os.path.exists(full_file_path):
            return "[MISSING]"
        
        if not defaults_dir:
            return "[UNKNOWN]"

        if isinstance(possible_tpl_names, str):
            possible_tpl_names = [possible_tpl_names]

        found_template = False
        for tpl_name in possible_tpl_names:
            tpl_path = os.path.join(defaults_dir, tpl_name)
            if os.path.exists(tpl_path):
                found_template = True
                try:
                    with open(full_file_path, "r", encoding="utf-8", errors="ignore") as f1, \
                         open(tpl_path, "r", encoding="utf-8", errors="ignore") as f2:
                        c1 = normalize_code(f1.read())
                        c2 = normalize_code(f2.read())
                        if c1 == c2:
                            return "[DEFAULT]"
                except Exception:
                    pass
        
        if not found_template:
            return "[UNKNOWN]"

        return "[MODIFIED]"

    in_ext = config.get("input_extension", ".in")

    custom_count = 0
    if os.path.exists("tests/custom"):
        for f in os.listdir("tests/custom"):
            if os.path.isfile(os.path.join("tests/custom", f)):
                if in_ext:
                    if f.endswith(in_ext):
                        custom_count += 1
                else:
                    if "." not in f:
                        custom_count += 1

    script_count = 0
    if os.path.exists("tests"):
        for f in os.listdir("tests"):
            if os.path.isfile(os.path.join("tests", f)):
                if in_ext:
                    if f.endswith(in_ext):
                        base_name = f[:-len(in_ext)]
                        if base_name.isdigit():
                            script_count += 1
                else:
                    if f.isdigit():
                        script_count += 1

    sol_file = config.get("solution_file", "solutions/ma_solution.cpp")
    checker_type = config.get("checker", None)
    builtin_checkers = ["ncmp", "wcmp", "lcmp", "rcmp", "fcmp", "uncmp", "yesno", "acmp", "case1", "casen", "lines", "nums"]

    print("========================================")
    print("          POLYSON PROBLEM STATUS        ")
    print("========================================")
    print(f" Problem Name : {config.get('problem_name', 'unspecified')}")
    print(f" Source       : {config.get('source', 'unspecified')}")
    print(f" Rating       : {config.get('rating', 0)}")
    print(f" Time Limit   : {config.get('time_limit_ms', 1000)} ms")
    print(f" Memory Limit : {config.get('memory_limit_mb', 256)} MB")
    print(f" Solution File: {sol_file}")
    print(f" Input Ext    : '{in_ext}'")
    print(f" Output Ext   : '{config.get('output_extension', '.out')}'")
    print(f" Checker      : {checker_type if checker_type else 'default (ncmp)'}")
    print(f" Tags         : {', '.join(config.get('tags', ['unspecified']))}")
    print("----------------------------------------")
    print(" FILE CHECKLIST:")
    print(f"  - Solution   : {check_file_status(sol_file, ['solutions/ma_solution.cpp', 'ma_solution.cpp', 'sol.cpp'])}")
    print(f"  - Generator  : {check_file_status('gen.cpp', ['gen.cpp', 'generator.cpp'])}")
    print(f"  - Validator  : {check_file_status('validator.cpp', ['validator.cpp', 'val.cpp'])}")

    if checker_type and checker_type in builtin_checkers:
        print(f"  - Checker    : [BUILT-IN] ({checker_type})")
    elif os.path.exists("checker.cpp"):
        st = check_file_status("checker.cpp", ["checker.cpp", "chk.cpp"])
        print(f"  - Checker    : {st}")
    elif checker_type and (checker_type.endswith(".cpp") or checker_type not in builtin_checkers):
        chk_file = checker_type if checker_type.endswith(".cpp") else f"{checker_type}.cpp"
        if os.path.exists(chk_file):
            st = check_file_status(chk_file, ["checker.cpp", "chk.cpp"])
            print(f"  - Checker    : {st}")
        else:
            print("  - Checker    : [MISSING]")
    else:
        print("  - Checker    : [BUILT-IN] (ncmp)")

    print("----------------------------------------")
    print(f" Custom Tests : {custom_count}")
    print(f" Script Tests : {script_count}")
    print("========================================")
