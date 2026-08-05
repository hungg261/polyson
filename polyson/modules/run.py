import os
import json
import random
import subprocess

from polyson.compiler import compile_cpp
from polyson.engine import parse_freemarker_polygon


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
    
    sol_src = config.get("solution_file", "solutions/ma_solution.cpp")
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


def stress_test(ftl_command, sol1_path, sol2_path):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    chk_src = "checker.cpp"
    if os.path.exists("problem.json"):
        try:
            with open("problem.json", "r", encoding="utf-8") as f:
                chk_src = json.load(f).get("checker", "checker.cpp")
                
                if chk_src != "checker.cpp":
                    preset_path = os.path.join(base_dir, "defaults", "checkers", f"{chk_src}.cpp")
                    if os.path.exists(preset_path):
                        chk_src = preset_path
        except Exception:
            pass
        
    if not os.path.exists("gen.cpp") or not os.path.exists(chk_src) or not os.path.exists(sol1_path) or not os.path.exists(sol2_path):
        print("[ERROR] Stress test failed: Ensure gen.cpp, checker, and both solution files exist.")
        return

    gen_exe = "generator.exe"
    chk_exe = "checker.exe"
    sol1_exe = "stress_sol1.exe"
    sol2_exe = "stress_sol2.exe"

    compile_cpp("gen.cpp", gen_exe)
    compile_cpp(chk_src, chk_exe, extra_args=["-I."])
    compile_cpp(sol1_path, sol1_exe)
    compile_cpp(sol2_path, sol2_exe)

    seed = random.randint(1, 1000000)
    iteration = 1

    print(f"[*] Starting infinite stress testing loop. Initial base seed: {seed}")
    print(f"[*] Verifying solution via checker: {sol2_path}")
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
