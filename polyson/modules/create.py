import json
import os
import shutil

def create_problem(name):
    if os.path.exists(name):
        print(f"[ERROR] Directory '{name}' already exists!")
        return
    
    modules_dir = os.path.dirname(__file__)
    base_dir = os.path.dirname(modules_dir)
    
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
