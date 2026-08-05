import json
import os
import shutil


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
        "chk": "checker",
        "val": "validator",
        "setchecker": "checker_template",
        "setvalidator": "validator_template"
    }

    target_key = aliases.get(key.lower(), key)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    action = True
        
    with open("problem.json", "r", encoding="utf-8") as f:
        config: dict = json.load(f)
        
    if target_key not in config:
        if input("Key not in config, do you want to proceed? (y/N): ").strip().lower() != 'y':
            print("[INFO] Config operation cancelled.")
            return

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
    elif target_key == "validator_template":
        filename = value if value.endswith(".cpp") else f"{value}.cpp"
        src_path = os.path.join(base_dir, "defaults", "validators", filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, "validator.cpp")
            print(f"[SUCCESS] Applied shared validator template: '{filename}' -> validator.cpp")
            return
        else:
            print(f"[ERROR] Validator template '{filename}' not found in defaults/validators/")
            return
    elif target_key in ["time_limit_ms", "memory_limit_mb", "rating"]:
        try:
            value = int(value)
        except ValueError:
            print(f"[ERROR] Value for '{target_key}' must be an integer.")
            return
    elif target_key == "tags":
        value = [tag.strip() for tag in value.split(",")]
    elif target_key == "checker":
        if value == "checker.cpp":
            if target_key in config:
                del config[target_key]
            action = False
            
            if not os.path.exists("checker.cpp"):
                src_path = os.path.join(base_dir, "defaults", "checkers", "ncmp.cpp")
                if(os.path.exists(src_path)):
                    shutil.copy(src_path, "checker.cpp")
        else:
            filename = value if value.endswith(".cpp") else f"{value}.cpp"
            src_path = os.path.join(base_dir, "defaults", "checkers", filename)
            if not os.path.exists(src_path):
                print(f"[ERROR] Checker template '{filename}' not found in defaults/checkers/")
                return
            
        
    if action:
        config[target_key] = value
        print(f"[SUCCESS] Updated '{target_key}' to {value} in problem.json")
            
    with open("problem.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)