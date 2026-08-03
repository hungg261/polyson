import sys
from polyson.cli import (
    create_problem, generate_and_validate, update_config, reset_problem,
    open_folder, validate_existing_tests, clean_workspace, show_status,
    stress_test, shuffle_tests, generate_pdf, create_contest
)

def main():
    if len(sys.argv) < 2:
        print("Polyson Usage Manual:")
        print("  polyson init <problem_name>                     -> Create a problem directory from template")
        print("  polyson contest <dir_name> [p1 p2..] [-n name]  -> Create a contest directory containing multiple problems")
        print("  polyson config <key> <value>                    -> Update property in problem.json")
        print("  polyson open <location>                         -> Open a directory or select a file in Explorer")
        print("  polyson reset                                   -> Reset directory back to standard sample template")
        print("  polyson run                                     -> Compile, generate, validate raw inputs")
        print("  polyson validate                                -> Run validator on all existing tests")
        print("  polyson shuffle                                 -> Shuffle test contents preserving filenames")
        print("  polyson pdf [*paths_or_contest.json]            -> Compile statement.tex files into a unified PDF via latexmk")
        print("  polyson clean                                   -> Remove compiled binaries from your directory")
        print("  polyson status                                  -> Display problem configuration profile overview")
        print("  polyson stress \"<cmd>\" <s1> <s2>                -> Infinite stress loop testing two distinct solutions")
        return

    subcommand = sys.argv[1].lower()

    if subcommand == "init":
        if len(sys.argv) < 3:
            print("[ERROR] Missing parameter. Usage: polyson init <problem_name>")
        else:
            create_problem(sys.argv[2])
    elif subcommand == "contest":
        if len(sys.argv) < 3:
            print("[ERROR] Missing parameters. Usage: polyson contest <dir_name> [prob1 prob2 ...] [-n \"Display Name\"]")
        else:
            create_contest(sys.argv[2:])
    elif subcommand == "config":
        if len(sys.argv) < 4:
            print("[ERROR] Missing parameters. Usage: polyson config <key> <value>")
        else:
            update_config(sys.argv[2], sys.argv[3])
    elif subcommand == "open":
        if len(sys.argv) < 3:
            print("[ERROR] Missing target location. Example: polyson open tests")
        else:
            open_folder(sys.argv[2])
    elif subcommand == "reset":
        reset_problem()
    elif subcommand == "run":
        generate_and_validate()
    elif subcommand == "validate":
        validate_existing_tests()
    elif subcommand == "shuffle":
        shuffle_tests()
    elif subcommand == "pdf":
        generate_pdf(sys.argv[2:])
    elif subcommand == "clean":
        clean_workspace()
    elif subcommand == "status":
        show_status()
    elif subcommand == "stress":
        if len(sys.argv) < 5:
            print("[ERROR] Missing parameters. Usage: polyson stress \"<ftl_command>\" <sol1_path> <sol2_path>")
        else:
            stress_test(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(f"[ERROR] Unknown command: '{subcommand}'")

if __name__ == "__main__":
    main()