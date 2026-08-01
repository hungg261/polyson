import subprocess
import sys

def compile_cpp(file_name, output_name):
    print(f"[*] Compiling {file_name}...")
    cmd = ["g++", "-O2", file_name, "-o", output_name]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[!] Compilation failed for {file_name}:\n{result.stderr}")
        sys.exit(1)
    print(f"[+] Compilation successful: {output_name}")
