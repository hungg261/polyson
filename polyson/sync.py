import hashlib
import json
import os
import random
import re
import string
import time
import zipfile
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_URL = "https://polygon.codeforces.com/api/"


def generate_api_sig(method_name: str, params: dict, api_secret: str) -> str:
    rand_prefix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    to_hash = f"{rand_prefix}/{method_name}?{param_string}#{api_secret}"
    return rand_prefix + hashlib.sha512(to_hash.encode("utf-8")).hexdigest()


def call_polygon_post(method_name: str, extra_params: dict = None, retries: int = 3):
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    api_key = os.getenv("POLYGON_API_KEY")
    api_secret = os.getenv("POLYGON_API_SECRET")

    if not api_key or not api_secret:
        return False, "Missing POLYGON_API_KEY or POLYGON_API_SECRET in .env file!"

    params = (extra_params or {}).copy()
    params["apiKey"] = api_key
    params["time"] = int(time.time())
    params["apiSig"] = generate_api_sig(method_name, params, api_secret)

    full_url = f"{BASE_URL}{method_name}"

    for attempt in range(retries):
        try:
            response = requests.post(full_url, data=params, timeout=60)
            try:
                res_json = response.json()
                if res_json.get("status") == "OK":
                    return True, res_json.get("result") if "result" in res_json else response.text
                else:
                    if attempt == retries - 1:
                        return False, response.text
            except json.JSONDecodeError:
                if response.status_code == 200:
                    return True, response.text
                if attempt == retries - 1:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            if attempt == retries - 1:
                return False, str(e)
        time.sleep(1)

    return False, "Timeout/Error"


def sanitize_short_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^a-z0-9-]', '', name)
    return name.strip('-')


def parse_solution_tag(file_name: str) -> str:
    name_lower = file_name.lower()
    prefix_map = {
        "ma": "MA", "ok": "OK", "wa": "WA", "tl": "TL",
        "ml": "ML", "re": "RE", "pe": "PE", "rj": "RJ",
    }
    if "_" in name_lower:
        prefix = name_lower.split("_")[0]
        if prefix in prefix_map:
            return prefix_map[prefix]

    return "OK"


def create_new_problem(short_name: str) -> int:
    print(f"[INFO] Creating new problem with short name '{short_name}' on Polygon...")
    ok, result = call_polygon_post("problem.create", {"name": short_name})
    if ok and isinstance(result, dict) and "id" in result:
        problem_id = result["id"]
        print(f"[SUCCESS] Problem created successfully! Problem ID: {problem_id}")
        return problem_id
    else:
        print(f"[ERROR] Failed to create new problem: {result}")
        return None


def enable_points_and_groups(problem_id: int):
    print("[INFO] Enabling points and groups for tests...")
    
    ok_p, res_p = call_polygon_post("problem.enablePoints", {
        "problemId": problem_id, 
        "testset": "tests", 
        "enable": "true"
    })
    if ok_p:
        print("[SUCCESS] Test points enabled!")
    else:
        print(f"[WARN] Could not enable points: {res_p}")

    ok_g, res_g = call_polygon_post("problem.enableGroups", {
        "problemId": problem_id, 
        "testset": "tests", 
        "enable": "true"
    })
    if ok_g:
        print("[SUCCESS] Test groups enabled!")
    else:
        print(f"[WARN] Could not enable groups: {res_g}")


def update_limits(problem_id: int, time_limit_ms: int = None, memory_limit_mb: int = None):
    params = {"problemId": problem_id}
    if time_limit_ms is not None:
        params["timeLimit"] = time_limit_ms
    if memory_limit_mb is not None:
        params["memoryLimit"] = memory_limit_mb

    if len(params) > 1:
        print(f"[INFO] Setting limits -> TL: {time_limit_ms}ms, ML: {memory_limit_mb}MB...")
        ok, res = call_polygon_post("problem.updateInfo", extra_params=params)
        if ok:
            print("[SUCCESS] Limits updated successfully!")
        else:
            print(f"[WARN] Could not update limits: {res}")


def upload_statement_with_image_names(problem_id: int, title: str, image_names: list):
    print(f"[INFO] Generating statement legend with image references...")
    images_sorted = sorted(image_names)
    legend = ""
    if images_sorted:
        legend = "\\begin{center}\n"
        for img_name in images_sorted:
            legend += f"    \\includegraphics{{{img_name}}}\n"
        legend += "\\end{center}"

    params = {
        "problemId": problem_id,
        "lang": "english",
        "name": title,
        "encoding": "UTF-8",
        "legend": legend,
        "input": "",
        "output": "",
        "notes": "",
    }
    ok, res = call_polygon_post("problem.saveStatement", extra_params=params)
    if ok:
        print("[SUCCESS] Statement (Image References Only) uploaded successfully!")
    else:
        print(f"[ERROR] Failed to upload statement: {res}")


def upload_solution(problem_id: int, file_path: Path, tag: str):
    print(f"[INFO] Uploading solution '{file_path.name}' [Tag: {tag}]...")
    file_content = file_path.read_text(encoding="utf-8")
    params = {
        "problemId": problem_id,
        "name": file_path.name,
        "tag": tag,
        "checkResult": "true",
        "file": file_content,
    }
    ok, res = call_polygon_post("problem.saveSolution", extra_params=params)
    if ok:
        print(f"[SUCCESS] Solution '{file_path.name}' uploaded!")
    else:
        print(f"[ERROR] Failed to upload solution '{file_path.name}': {res}")


def upload_source_file(problem_id: int, file_path: Path, file_type: str = "source"):
    if not file_path.exists():
        return False
    print(f"[INFO] Uploading {file_type} file '{file_path.name}'...")
    file_content = file_path.read_text(encoding="utf-8")
    params = {
        "problemId": problem_id,
        "type": file_type,
        "name": file_path.name,
        "file": file_content,
    }
    ok, res = call_polygon_post("problem.saveFile", extra_params=params)
    if ok:
        print(f"[SUCCESS] File '{file_path.name}' uploaded!")
        return True
    return False


def set_validator(problem_id: int, validator_name: str):
    print(f"[INFO] Setting validator to '{validator_name}'...")
    call_polygon_post("problem.setValidator", {"problemId": problem_id, "validator": validator_name})


def set_checker(problem_id: int, checker_name: str):
    checker_full = checker_name if checker_name.startswith("std::") else checker_name
    print(f"[INFO] Setting checker to '{checker_full}'...")
    call_polygon_post("problem.setChecker", {"problemId": problem_id, "checker": checker_full}, retries=5)


def save_test(problem_id: int, test_index: int, input_data: str, use_in_statements: bool = True):
    params = {
        "problemId": problem_id,
        "testset": "tests",
        "testIndex": test_index,
        "testInput": input_data,
        "testUseInStatements": "true" if use_in_statements else "false",
    }
    ok, res = call_polygon_post("problem.saveTest", extra_params=params)
    if ok:
        print(f"[SUCCESS] Sample Test #{test_index} uploaded!")
    else:
        print(f"[ERROR] Failed to upload test #{test_index}: {res}")


def save_script(problem_id: int, script_path: Path):
    if not script_path.exists():
        print(f"[WARN] Script file not found: {script_path}")
        return
    print("[INFO] Uploading test script from script.ftl...")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    params = {
        "problemId": problem_id,
        "testset": "tests",
        "source": content,
    }
    call_polygon_post("problem.saveScript", extra_params=params)
    print("[SUCCESS] Test script uploaded!")


def save_tags(problem_id: int, tags: list):
    if not tags:
        return
    tags_str = ", ".join(tags)
    print(f"[INFO] Saving tags: {tags_str}")
    call_polygon_post("problem.saveTags", {"problemId": problem_id, "tags": tags_str})


def sync_problem(args: list = None) -> int:
    args = args or []
    folder_dir = "."
    short_name = None

    i = 0
    clean_args = []
    while i < len(args):
        if args[i] in ("--path", "-p") and i + 1 < len(args):
            folder_dir = args[i + 1]
            i += 2
        else:
            clean_args.append(args[i])
            i += 1

    if clean_args:
        short_name = clean_args[0]

    folder = Path(folder_dir).resolve()
    json_path = folder / "problem.json"

    if not json_path.exists():
        print(f"[ERROR] Could not find 'problem.json' in {folder}")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    target_name = short_name if short_name else folder.name
    clean_name = sanitize_short_name(target_name)
    if not clean_name:
        clean_name = "new-problem"

    print(f"[INFO] Using sanitized short_name: '{clean_name}'")

    problem_id = create_new_problem(clean_name)
    if not problem_id:
        print("[ERROR] Could not create problem on Polygon. Aborting process.")
        return None

    print(f"[INFO] Synchronizing to Polygon Problem ID: {problem_id}")

    enable_points_and_groups(problem_id)

    tl_ms = config.get("time_limit_ms")
    ml_mb = config.get("memory_limit_mb")
    update_limits(problem_id, time_limit_ms=tl_ms, memory_limit_mb=ml_mb)

    image_names = []
    zip_path = folder / "statements.zip"
    extract_dir = folder / "_temp_statements"

    if zip_path.exists():
        print("[INFO] Reading image filenames from statements.zip...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        statement_img_dir = extract_dir / "statement"
        if statement_img_dir.exists():
            for img in statement_img_dir.glob("*"):
                if img.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    image_names.append(img.name)

    statement_title = config.get("problem_name", clean_name)
    upload_statement_with_image_names(problem_id, statement_title, image_names)
    save_tags(problem_id, config.get("tags", []))

    solutions_dir = folder / "solutions"
    if solutions_dir.exists():
        for sol_file in solutions_dir.glob("*"):
            if not sol_file.is_file():
                continue
            tag = parse_solution_tag(sol_file.name)
            upload_solution(problem_id, sol_file, tag=tag)

    val_path = folder / "validator.cpp"
    if upload_source_file(problem_id, val_path, file_type="source"):
        set_validator(problem_id, val_path.name)

    gen_path = folder / "gen.cpp"
    upload_source_file(problem_id, gen_path, file_type="source")

    if "checker" in config:
        chk_name = config["checker"]
        if not chk_name.startswith("std::"):
            chk_name = f"std::{chk_name}.cpp"
        set_checker(problem_id, chk_name)
    else:
        custom_checker_path = folder / "checker.cpp"
        if custom_checker_path.exists():
            if upload_source_file(problem_id, custom_checker_path, file_type="source"):
                set_checker(problem_id, custom_checker_path.name)
        else:
            print("[WARN] Key 'checker' is missing in problem.json and 'checker.cpp' was not found.")

    input_ext = config.get("input_extension", ".in")
    custom_dir = folder / "tests" / "custom"
    current_test_index = 1

    if custom_dir.exists():
        sample_pattern = f"sample*{input_ext}"
        sample_files = sorted([f for f in custom_dir.glob(sample_pattern) if f.is_file()])
        print(f"[INFO] Found {len(sample_files)} sample file(s) matching '{sample_pattern}'")
        for sample_in in sample_files:
            with open(sample_in, "r", encoding="utf-8") as f:
                input_data = f.read()
            save_test(problem_id, current_test_index, input_data, use_in_statements=True)
            current_test_index += 1
    else:
        print(f"[WARN] Custom tests directory not found at: {custom_dir}")

    script_path = folder / "script.ftl"
    save_script(problem_id, script_path)

    if extract_dir.exists():
        import shutil
        shutil.rmtree(extract_dir)

    print(f"[SUCCESS] Problem synchronized to Polygon ID: {problem_id}")
    return problem_id