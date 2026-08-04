import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

SYSTEM_PROMPT = (
    "You are an expert competitive programming problem setter assistant for Polygon/Polyson.\n"
    "CRITICAL MANDATORY RULES (VIOLATION IS STRICTLY FORBIDDEN):\n"
    "1. SOLUTION FILE:\n"
    "   - MUST START EXACTLY WITH `#include <bits/stdc++.h>` OR `#include <iostream>` AS LINE 1.\n"
    "   - ABSOLUTELY NEVER OMIT HEADER INCLUDES. NO EXCEPTIONS.\n"
    "   - MUST NOT include testlib.h.\n"
    "2. GENERATOR (gen.cpp):\n"
    "   - MUST START WITH `#include \"testlib.h\"`.\n"
    "   - MUST USE `opt<int>(1)`, `opt<int>(2)` (positional CLI args) or `opt<int>(\"seed\")` for parameters, NOT raw inputs like `opt<int>(\"a\")` unless providing defaults.\n"
    "   - MUST NEVER call `inf` or `inf.readInt()`. Generator reads NO stdin.\n"
    "   - MUST use `rnd.next(min_v, max_v)` to generate random test data.\n"
    "3. SCRIPT (script.ftl):\n"
    "   - MUST generate EXACTLY 40 tests in total across all subtasks.\n"
    "   - Output redirection MUST BE strictly `> $` (e.g. `gen ${i} 1000 2000 > $`).\n"
    "4. VALIDATOR (validator.cpp):\n"
    "   - MUST START WITH `#include \"testlib.h\"`.\n"
    "   - Use EXACT testlib methods: `inf.readSpace()`, `inf.readEoln()`, `inf.readEof()`. NEVER `readEol()`.\n"
    "5. FORMATTING:\n"
    "   - Output ultra-concise, fully working C++ code using standard newlines (\\n).\n"
    "   - Do NOT include comments, explanations, or markdown."
)

def clean_code_response(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    if "\n" not in text and "\\n" in text:
        text = text.replace("\\n", "\n")
    return text.strip()

def enforce_solution_headers(code: str) -> str:
    if "#include" not in code:
        code = "#include <bits/stdc++.h>\nusing namespace std;\n" + code
    elif "<iostream>" not in code and "<bits/stdc++.h>" not in code:
        code = "#include <iostream>\n" + code
    return code

def run_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found in environment or .env file.")
        return

    client = Groq(api_key=api_key)
    model = "llama-3.3-70b-versatile"

    statement_path = Path("statement.tex")
    config_path = Path("problem.json")

    if not statement_path.exists():
        print("[ERROR] statement.tex not found.")
        return
    if not config_path.exists():
        print("[ERROR] problem.json not found.")
        return

    statement_content = statement_path.read_text(encoding="utf-8")
    config = json.loads(config_path.read_text(encoding="utf-8"))

    # Phase 1: Reference Solution
    sol_rel_path = config.get("solution_file", "solutions/ma_solution.cpp")
    sol_path = Path(sol_rel_path)
    sol_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[AGENT] Generating Solution -> {sol_path} ...")
    sol_prompt = (
        f"Problem Statement:\n{statement_content}\n\n"
        "Write standard C++ reference solution.\n"
        "LINE 1 MUST BE: #include <bits/stdc++.h>\n"
        "LINE 2 MUST BE: using namespace std;\n"
        "Do NOT include testlib.h. Output ONLY raw C++ code."
    )
    res_sol = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": sol_prompt}
        ],
        temperature=0.1
    )
    sol_code = clean_code_response(res_sol.choices[0].message.content)
    sol_code = enforce_solution_headers(sol_code)
    sol_path.write_text(sol_code, encoding="utf-8")

    # Phase 2: Checker (Optional)
    if "checker" not in config or not config["checker"]:
        print("[AGENT] Generating Checker -> checker.cpp ...")
        chk_prompt = (
            f"Problem Statement:\n{statement_content}\n\n"
            'Write a testlib.h C++ checker using #include "testlib.h". '
            "Output ONLY raw C++ code."
        )
        res_chk = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chk_prompt}
            ],
            temperature=0.1
        )
        chk_code = clean_code_response(res_chk.choices[0].message.content)
        Path("checker.cpp").write_text(chk_code, encoding="utf-8")

    # Phase 3: Generator, Script.ftl, and Validator Combined
    print("[AGENT] Generating Generator, script.ftl & Validator ...")
    combined_prompt = (
        f"Problem Statement:\n{statement_content}\n\n"
        'Generate 3 components:\n'
        '1. gen.cpp: C++ test generator using #include "testlib.h" and rnd.next(min, max). CLI args must use opt<int>(1, default_val) or opt<int>(2). NEVER call inf.readInt().\n'
        '2. script.ftl: Freemarker script generating EXACTLY 40 tests using > $.\n'
        '3. validator.cpp: C++ validator using #include "testlib.h" (inf.readSpace, inf.readEoln, inf.readEof).\n\n'
        'Return JSON format:\n'
        '{\n'
        '  "gen_code": "raw C++ generator code",\n'
        '  "script_code": "raw Freemarker script",\n'
        '  "validator_code": "raw C++ validator code"\n'
        '}'
    )
    res_combined = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": combined_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    data = json.loads(res_combined.choices[0].message.content)

    Path("gen.cpp").write_text(clean_code_response(data.get("gen_code", "")), encoding="utf-8")
    Path("script.ftl").write_text(clean_code_response(data.get("script_code", "")), encoding="utf-8")
    Path("validator.cpp").write_text(clean_code_response(data.get("validator_code", "")), encoding="utf-8")

    print("[AGENT] All files generated successfully!")

if __name__ == "__main__":
    run_agent()