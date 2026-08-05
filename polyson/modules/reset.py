

import os
import shutil


def reset_problem():
    if not os.path.exists("problem.json") or not os.path.exists("script.ftl") or not os.path.exists("gen.cpp"):
        print("[ERROR] Execution error: You must be inside a valid problem directory to reset it.")
        return

    choice = input("Are you sure you want to reset all files to factory defaults? (y/N): ").strip().lower()
    if choice != 'y':
        print("[INFO] Reset operation cancelled.")
        return

    base_dir = os.path.dirname(os.path.dirname(__file__))
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
