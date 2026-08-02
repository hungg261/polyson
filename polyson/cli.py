import os
import shutil
import subprocess
import json
from polyson.compiler import compile_cpp
from polyson.engine import parse_freemarker_polygon
import random

def create_problem(name):
    if os.path.exists(name):
        print(f"[ERROR] Directory '{name}' already exists!")
        return
    
    base_dir = os.path.dirname(__file__)
    template_src = os.path.join(base_dir, "templates", "sample")
    shutil.copytree(template_src, name, copy_function=shutil.copy)
    
    shared_testlib = os.path.join(base_dir, "defaults", "testlib.h")
    if os.path.exists(shared_testlib):
        shutil.copy(shared_testlib, os.path.join(name, "testlib.h"))
        
    print(f"[INFO] Successfully initialized a new problem at: '{name}'")

def create_contest(args):
    if not args:
        print("[ERROR] Missing folder name. Usage: polyson contest <dir_name> [prob1 prob2 ...] [-n \"Contest Name\"]")
        return

    dir_name = args[0]
    display_name = dir_name
    problem_names = []

    i = 1
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--name"):
            if i + 1 < len(args):
                display_name = args[i + 1]
                i += 2
                continue
            else:
                print("[ERROR] Missing value for -n/--name flag.")
                return
        else:
            problem_names.append(arg)
            i += 1

    if os.path.exists(dir_name):
        print(f"[ERROR] Directory '{dir_name}' already exists!")
        return

    os.makedirs(dir_name)
    cwd = os.getcwd()
    os.chdir(dir_name)

    print(f"[*] Initializing contest folder '{dir_name}' (Name: '{display_name}') with {len(problem_names)} problem(s)...")

    created_problems = []
    for p_name in problem_names:
        create_problem(p_name)
        created_problems.append(p_name)

    contest_config = {
        "contest_name": display_name,
        "problems": created_problems
    }

    with open("contest.json", "w", encoding="utf-8") as f:
        json.dump(contest_config, f, indent=4)

    os.chdir(cwd)
    print(f"[SUCCESS] Contest folder '{dir_name}' initialized successfully with contest.json!")

def reset_problem():
    if not os.path.exists("problem.json") or not os.path.exists("script.ftl") or not os.path.exists("gen.cpp"):
        print("[ERROR] Execution error: You must be inside a valid problem directory to reset it.")
        return

    choice = input("Are you sure you want to reset all files to factory defaults? (y/N): ").strip().lower()
    if choice != 'y':
        print("[INFO] Reset operation cancelled.")
        return

    base_dir = os.path.dirname(__file__)
    template_src = os.path.join(base_dir, "templates", "sample")

    for item in os.listdir(template_src):
        s = os.path.join(template_src, item)
        d = os.path.join(os.getcwd(), item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d, copy_function=shutil.copy)
        else:
            shutil.copy(s, d)

    shared_testlib = os.path.join(base_dir, "defaults", "testlib.h")
    if os.path.exists(shared_testlib):
        shutil.copy(shared_testlib, os.path.join(os.getcwd(), "testlib.h"))

    print("[SUCCESS] Problem files and configuration have been reset to factory defaults.")

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

def update_config(key, value):
    if not os.path.exists("problem.json"):
        print("[ERROR] problem.json not found in the current directory.")
        return

    aliases = {
        "name": "problem_name",
        "sol": "solution_file",
        "in": "input_extension",
        "out": "output_extension",
        "src": "source",
        "tl": "time_limit_ms",
        "ml": "memory_limit_mb",
        "rt": "rating",
        "tg": "tags",
        "chk": "checker_template",
        "val": "validator_template"
    }

    target_key = aliases.get(key.lower(), key)
    base_dir = os.path.dirname(__file__)

    if target_key == "checker_template":
        filename = value if value.endswith(".cpp") else f"{value}.cpp"
        src_path = os.path.join(base_dir, "defaults", "checkers", filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, "checker.cpp")
            print(f"[SUCCESS] Applied shared checker template: '{filename}' -> checker.cpp")
            return
        else:
            print(f"[ERROR] Checker template '{filename}' not found in defaults/checkers/")
            return

    if target_key == "validator_template":
        filename = value if value.endswith(".cpp") else f"{value}.cpp"
        src_path = os.path.join(base_dir, "defaults", "validators", filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, "validator.cpp")
            print(f"[SUCCESS] Applied shared validator template: '{filename}' -> validator.cpp")
            return
        else:
            print(f"[ERROR] Validator template '{filename}' not found in defaults/validators/")
            return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    if target_key in ["time_limit_ms", "memory_limit_mb", "rating"]:
        try:
            value = int(value)
        except ValueError:
            print(f"[ERROR] Value for '{target_key}' must be an integer.")
            return
    elif target_key == "tags":
        value = [tag.strip() for tag in value.split(",")]

    config[target_key] = value

    with open("problem.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    print(f"[SUCCESS] Updated '{target_key}' to {value} in problem.json")

def generate_and_validate():
    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        print(f"==================================================")
        print(f"   RUNNING CONTEST: {contest_data.get('contest_name', 'Unknown')}")
        print(f"==================================================")
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                print(f"\n>>> [PROBLEM: {p}]")
                os.chdir(p)
                generate_and_validate()
                os.chdir(cwd)
            else:
                print(f"\n[WARNING] Skipping non-existent problem folder: {p}")
        print(f"\n==================================================")
        print(f"[SUCCESS] Finished running all contest problems!")
        print(f"==================================================")
        return

    if not os.path.exists("problem.json") or not os.path.exists("script.ftl") or not os.path.exists("gen.cpp"):
        print("[ERROR] Execution error: Missing core files (problem.json, script.ftl, or gen.cpp).")
        return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    sol_src = config.get("solution_file", "solutions/solution.cpp")
    in_ext = config.get("input_extension", ".in")
    out_ext = config.get("output_extension", ".out")

    if not os.path.exists(sol_src):
        print(f"[ERROR] Solution file not found at: {sol_src}")
        return

    if not os.path.exists("tests"):
        os.makedirs("tests")
    if not os.path.exists("tests/custom"):
        os.makedirs("tests/custom")

    for f in os.listdir("tests"):
        full_path = os.path.join("tests", f)
        if os.path.isfile(full_path):
            os.remove(full_path)

    custom_inputs = []
    if os.path.exists("tests/custom"):
        for f in os.listdir("tests/custom"):
            full_path = os.path.join("tests/custom", f)
            if os.path.isfile(full_path) and (f.endswith(in_ext) if in_ext else "." not in f):
                custom_inputs.append(f)

    gen_exe = "generator.exe"
    sol_exe = "solution.exe"
    val_exe = "validator.exe"

    compile_cpp("gen.cpp", gen_exe)
    compile_cpp(sol_src, sol_exe)
    
    has_validator = os.path.exists("validator.cpp")
    if has_validator:
        compile_cpp("validator.cpp", val_exe)

    with open("script.ftl", "r", encoding="utf-8") as f:
        ftl_content = f.read()
    
    lines = parse_freemarker_polygon(ftl_content)
    total_script_tests = len(lines)
    print(f"[*] Found {total_script_tests} script-generated test command(s).")
    
    pad_length = max(2, len(str(total_script_tests)))

    for f_name in custom_inputs:
        base_name = f_name[:-len(in_ext)] if in_ext else f_name
        input_path = os.path.join("tests/custom", f_name)
        output_path = os.path.join("tests/custom", f"{base_name}{out_ext}")
        
        print(f" -> Processing custom test case: {f_name}...")
        
        if has_validator:
            with open(input_path, "r") as infile:
                v_res = subprocess.run([val_exe], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if v_res.returncode != 0:
                    print(f"    [INVALID] Custom test {f_name}: Rejected by Validator!")
                    continue
                else:
                    print(f"    [OK] Custom test {f_name} passed validation.")
                    
        with open(input_path, "r") as infile, open(output_path, "w", newline='\n') as outfile:
            subprocess.run([sol_exe], stdin=infile, stdout=outfile)

    test_idx = 1
    for line in lines:
        tokens = line.split()
        if not tokens:
            continue
        
        args = [t for t in tokens[1:] if t not in ('>', '$')]
        test_name = str(test_idx).zfill(pad_length)
        input_path = os.path.join("tests", f"{test_name}{in_ext}")
        output_path = os.path.join("tests", f"{test_name}{out_ext}")
        
        print(f" -> Processing script test case {test_name}{in_ext}...")
        
        with open(input_path, "w", newline='\n') as infile:
            subprocess.run([gen_exe] + args, stdout=infile)
            
        if has_validator:
            with open(input_path, "r") as infile:
                v_res = subprocess.run([val_exe], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if v_res.returncode != 0:
                    print(f"    [INVALID] Test {test_name}{in_ext}: Rejected by Validator!")
                    continue
                else:
                    print(f"    [OK] Test {test_name}{in_ext} passed validation.")
            
        with open(input_path, "r") as infile, open(output_path, "w", newline='\n') as outfile:
            subprocess.run([sol_exe], stdin=infile, stdout=outfile)
            
        test_idx += 1

    print("\n[SUCCESS] The 'tests/' directory has been formatted and is ready for Polygon upload.")

def validate_existing_tests():
    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        print(f"==================================================")
        print(f"   VALIDATING CONTEST: {contest_data.get('contest_name', 'Unknown')}")
        print(f"==================================================")
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                print(f"\n>>> [PROBLEM: {p}]")
                os.chdir(p)
                validate_existing_tests()
                os.chdir(cwd)
        return

    if not os.path.exists("problem.json") or not os.path.exists("tests"):
        print("[ERROR] problem.json or tests directory missing.")
        return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    in_ext = config.get("input_extension", ".in")
    val_exe = "validator.exe"

    has_validator = os.path.exists("validator.cpp")
    if not has_validator:
        print("[ERROR] validator.cpp not found in the current directory.")
        return

    compile_cpp("validator.cpp", val_exe)

    custom_inputs = []
    if os.path.exists("tests/custom"):
        for f in os.listdir("tests/custom"):
            full_path = os.path.join("tests/custom", f)
            if os.path.isfile(full_path) and (f.endswith(in_ext) if in_ext else "." not in f):
                custom_inputs.append(f)

    script_inputs = []
    for f in os.listdir("tests"):
        full_path = os.path.join("tests", f)
        if os.path.isfile(full_path) and (f.endswith(in_ext) if in_ext else True):
            base_name = f[:-len(in_ext)] if in_ext else f
            if base_name.isdigit():
                script_inputs.append(f)

    print(f"[*] Validating {len(custom_inputs)} custom test(s) and {len(script_inputs)} script test(s)...")

    for f_name in custom_inputs:
        input_path = os.path.join("tests/custom", f_name)
        with open(input_path, "r") as infile:
            v_res = subprocess.run([val_exe], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if v_res.returncode != 0:
                print(f"    [INVALID] Custom test {f_name}: Rejected by Validator!")
            else:
                print(f"    [OK] Custom test {f_name} passed validation.")

    for f_name in script_inputs:
        input_path = os.path.join("tests", f_name)
        with open(input_path, "r") as infile:
            v_res = subprocess.run([val_exe], stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if v_res.returncode != 0:
                print(f"    [INVALID] Script test {f_name}: Rejected by Validator!")
            else:
                print(f"    [OK] Script test {f_name} passed validation.")

    print("[SUCCESS] Validation process completed.")

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

def clean_binaries():
    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                os.chdir(p)
                clean_binaries()
                os.chdir(cwd)

    binary_targets = ["generator.exe", "solution.exe", "validator.exe", "checker.exe", "stress_sol1.exe", "stress_sol2.exe"]
    latex_extensions = [".aux", ".fdb_latexmk", ".fls", ".log", ".toc", ".synctex.gz"]
    cleaned_any = False
    
    for f in binary_targets:
        if os.path.exists(f):
            os.remove(f)
            print(f"[INFO] Removed binary: {f}")
            cleaned_any = True

    for f in os.listdir("."):
        if os.path.isfile(f):
            if any(f.endswith(ext) for ext in latex_extensions):
                os.remove(f)
                print(f"[INFO] Removed auxiliary file: {f}")
                cleaned_any = True
            
    if cleaned_any:
        print("[SUCCESS] Workspace cleaned successfully.")
    else:

        print("[INFO] Nothing to clean. Workspace is already clean.")

def show_status():
    if os.path.exists("contest.json"):
        with open("contest.json", "r", encoding="utf-8") as f:
            contest_data = json.load(f)
        problems = contest_data.get("problems", [])
        print("========================================")
        print("          POLYSON CONTEST STATUS        ")
        print("========================================")
        print(f" Contest Name : {contest_data.get('contest_name', 'Unknown')}")
        print(f" Problems     : {', '.join(problems)}")
        print("----------------------------------------")
        cwd = os.getcwd()
        for p in problems:
            if os.path.exists(p) and os.path.isdir(p):
                print(f"\n[Sub-Problem: {p}]")
                os.chdir(p)
                show_status()
                os.chdir(cwd)
        print("========================================")
        return

    if not os.path.exists("problem.json"):
        print("[ERROR] problem.json not found in the current directory.")
        return

    with open("problem.json", "r", encoding="utf-8") as f:
        config = json.load(f)

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

    print("========================================")
    print("           POLYSON PROBLEM STATUS       ")
    print("========================================")
    print(f" Problem Name : {config.get('problem_name', 'Unknown')}")
    print(f" Source       : {config.get('source', 'unspecified')}")
    print(f" Rating       : {config.get('rating', 'unspecified')}")
    print(f" Time Limit   : {config.get('time_limit_ms', 1000)} ms")
    print(f" Memory Limit : {config.get('memory_limit_mb', 256)} MB")
    print(f" Solution File: {config.get('solution_file', 'Unknown')}")
    print(f" Input Ext    : '{in_ext}'")
    print(f" Output Ext   : '{config.get('output_extension', '.out')}'")
    print(f" Tags         : {', '.join(config.get('tags', []))}")
    print("----------------------------------------")
    print(f" Custom Tests : {custom_count}")
    print(f" Script Tests : {script_count}")
    print("========================================")

def stress_test(ftl_command, sol1_path, sol2_path):
    if not os.path.exists("gen.cpp") or not os.path.exists("checker.cpp") or not os.path.exists(sol1_path) or not os.path.exists(sol2_path):
        print("[ERROR] Stress test failed: Ensure gen.cpp, checker.cpp, and both solution files exist.")
        return

    gen_exe = "generator.exe"
    chk_exe = "checker.exe"
    sol1_exe = "stress_sol1.exe"
    sol2_exe = "stress_sol2.exe"

    compile_cpp("gen.cpp", gen_exe)
    compile_cpp("checker.cpp", chk_exe)
    compile_cpp(sol1_path, sol1_exe)
    compile_cpp(sol2_path, sol2_exe)

    seed = random.randint(1, 1000000)
    iteration = 1

    print(f"[*] Starting infinite stress testing loop. Initial base seed: {seed}")
    print(f"[*] Verifying solution via checker.cpp: {sol2_path}")
    print("----------------------------------------------------------------")

    try:
        while True:
            ftl_script = f"<#assign seed = {seed}>\n{ftl_command}"
            commands = parse_freemarker_polygon(ftl_script)
            
            if not commands:
                print("[ERROR] Failed to parse the provided FreeMarker instruction token.")
                break

            tokens = commands[0].split()
            args = [t for t in tokens[1:] if t not in ('>', '$')]

            input_tmp = "stress_input.tmp"
            ans_tmp = "stress_ans.tmp"
            ouf_tmp = "stress_ouf.tmp"

            with open(input_tmp, "w", newline='\n') as infile:
                subprocess.run([gen_exe] + args, stdout=infile)

            with open(input_tmp, "r") as infile, open(ans_tmp, "w", newline='\n') as outfile:
                subprocess.run([sol1_exe], stdin=infile, stdout=outfile)

            with open(input_tmp, "r") as infile, open(output_file := ouf_tmp, "w", newline='\n') as outfile:
                subprocess.run([sol2_exe], stdin=infile, stdout=outfile)

            checker_res = subprocess.run([chk_exe, input_tmp, ouf_tmp, ans_tmp], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if checker_res.returncode != 0:
                print(f"\n[CHECKER VERDICT FAILED] Mismatch or error found on iteration {iteration} (Seed: {seed})!")
                
                os.rename(input_tmp, "stress_fail.in")
                os.rename(ans_tmp, "stress_fail.ans")
                os.rename(ouf_tmp, "stress_fail.ouf")
                
                print("[INFO] Saved counter-example dump files:")
                print("       -> Input data saved to: stress_fail.in")
                print(f"       -> Reference answer from {sol1_path} saved to: stress_fail.ans")
                print(f"       -> Wrong output from {sol2_path} saved to: stress_fail.ouf")
                
                if checker_res.stderr:
                    print(f"[CHECKER MESSAGE]:\n{checker_res.stderr.decode('utf-8', errors='ignore').strip()}")
                break

            if os.path.exists(input_tmp): os.remove(input_tmp)
            if os.path.exists(ans_tmp): os.remove(ans_tmp)
            if os.path.exists(ouf_tmp): os.remove(ouf_tmp)

            print(f"\r[OK] Iteration {iteration} passed successfully (Seed: {seed}).", end="", flush=True)
            
            seed += 1
            iteration += 1

    except KeyboardInterrupt:
        print("\n[INFO] Stress testing terminated manually by user interruption request.")
    finally:
        for f in [gen_exe, chk_exe, sol1_exe, sol2_exe, "stress_input.tmp", "stress_ans.tmp", "stress_ouf.tmp"]:
            if os.path.exists(f):
                os.remove(f)

def generate_pdf(paths):
    base_dir = os.path.dirname(__file__)
    statements_dir = os.path.join(base_dir, "defaults", "statements")
    
    if not os.path.exists(statements_dir):
        print("[ERROR] Statements template directory missing in defaults.")
        return

    contest_folder_pdf_name = None
    target_paths = []

    if len(paths) == 1 and paths[0].endswith("contest.json") and os.path.exists(paths[0]):
        folder_path = os.path.dirname(os.path.abspath(paths[0]))
        folder_name = os.path.basename(folder_path)
        contest_folder_pdf_name = f"{folder_name}.pdf"
        with open(paths[0], "r", encoding="utf-8") as f:
            c_data = json.load(f)
            target_paths = [os.path.join(folder_path, p) for p in c_data.get("problems", [])]
    elif not paths and os.path.exists("contest.json"):
        folder_name = os.path.basename(os.getcwd())
        contest_folder_pdf_name = f"{folder_name}.pdf"
        with open("contest.json", "r", encoding="utf-8") as f:
            c_data = json.load(f)
            target_paths = c_data.get("problems", [])
    else:
        target_paths = paths if paths else ["."]

    valid_tex_files = []
    for p in target_paths:
        abs_p = os.path.abspath(p)
        tex_file = os.path.join(abs_p, "statement.tex")
        if os.path.exists(tex_file):
            valid_tex_files.append(tex_file)
        else:
            print(f"[WARNING] Skipping '{p}': statement.tex not found.")

    if not valid_tex_files:
        print("[ERROR] No valid statement.tex files found to compile.")
        return

    if not shutil.which("latexmk"):
        print("[ERROR] 'latexmk' was not found in system PATH. Please ensure MiKTeX/TeX Live is installed.")
        return

    build_dir = os.path.abspath(".polyson_pdf_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    try:
        for item in os.listdir(statements_dir):
            s = os.path.join(statements_dir, item)
            d = os.path.join(build_dir, item)
            if os.path.isfile(s):
                shutil.copy(s, d)

        contents_path = os.path.join(build_dir, "contents.tex")
        with open(contents_path, "w", encoding="utf-8") as f:
            for i, tex in enumerate(valid_tex_files):
                formatted_path = tex.replace("\\", "/")
                f.write(f"\\input{{{formatted_path}}}\n")
                if i < len(valid_tex_files) - 1:
                    f.write("\\clearpage\n")

        print(f"[*] Compiling PDF using latexmk (-pdf) for {len(valid_tex_files)} problem(s)...")

        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
            cwd=build_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output_pdf = os.path.join(build_dir, "main.pdf")
        if os.path.exists(output_pdf):
            if contest_folder_pdf_name:
                final_name = contest_folder_pdf_name
            elif len(valid_tex_files) == 1 and paths:
                prob_name = os.path.basename(os.path.abspath(paths[0]))
                final_name = f"{prob_name}.pdf"
            elif len(valid_tex_files) == 1 and not paths:
                final_name = "statement.pdf"
            else:
                final_name = "contest.pdf"

            shutil.copy(output_pdf, os.path.join(os.getcwd(), final_name))
            print(f"[SUCCESS] Generated PDF: {final_name}")
        else:
            print("[ERROR] LaTeX compilation failed. Please check your statement.tex syntax.")

    finally:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)