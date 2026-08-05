import argparse
import sys
from polyson import __version__
from .modules.sync import sync_problem
from .modules import (
    create_problem, generate_and_validate, update_config, reset_problem,
    open_folder, validate_existing_tests, clean_workspace, show_status,
    stress_test, shuffle_tests, generate_pdf, create_contest
)

def main():
    parser = argparse.ArgumentParser(
        description="Polyson - Bộ công cụ quản lý và cấu hình bài tập chuẩn hóa.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version=f"Polyson version {__version__}")
    
    subparsers = parser.add_subparsers(dest="subcommand", title="Danh sách câu lệnh (Subcommands)")

    p_init = subparsers.add_parser("init", help="Create a problem directory from template")
    p_init.add_argument("problem_name")

    p_contest = subparsers.add_parser("contest", help="Create a contest directory containing multiple problems")
    p_contest.add_argument("dir_name")
    p_contest.add_argument("problems", nargs="*")

    p_config = subparsers.add_parser("config", help="Update property in problem.json")
    p_config.add_argument("key")
    p_config.add_argument("value")

    p_open = subparsers.add_parser("open", help="Open a directory or select a file in Explorer")
    p_open.add_argument("location")

    subparsers.add_parser("reset", help="Reset directory back to standard sample template")
    subparsers.add_parser("run", help="Compile, generate, validate raw inputs")
    subparsers.add_parser("validate", help="Run validator on all existing tests")
    subparsers.add_parser("shuffle", help="Shuffle test contents preserving filenames")
    subparsers.add_parser("clean", help="Remove compiled binaries from your directory")
    subparsers.add_parser("status", help="Display problem configuration profile overview")

    p_pdf = subparsers.add_parser("pdf", help="Compile statement.tex files into a unified PDF via latexmk")
    p_pdf.add_argument("paths", nargs="*")

    p_stress = subparsers.add_parser("stress", help="Infinite stress loop testing two distinct solutions")
    p_stress.add_argument("ftl_command")
    p_stress.add_argument("sol1_path")
    p_stress.add_argument("sol2_path")

    p_sync = subparsers.add_parser("sync", help="Synchronize local problem configuration and assets")
    p_sync.add_argument("args", nargs="*")

    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.subcommand == "init":
        create_problem(args.problem_name)
    elif args.subcommand == "contest":
        create_contest([args.dir_name] + args.problems)
    elif args.subcommand == "config":
        update_config(args.key, args.value)
    elif args.subcommand == "open":
        open_folder(args.location)
    elif args.subcommand == "reset":
        reset_problem()
    elif args.subcommand == "run":
        generate_and_validate()
    elif args.subcommand == "validate":
        validate_existing_tests()
    elif args.subcommand == "shuffle":
        shuffle_tests()
    elif args.subcommand == "pdf":
        generate_pdf(args.paths)
    elif args.subcommand == "clean":
        clean_workspace()
    elif args.subcommand == "status":
        show_status()
    elif args.subcommand == "stress":
        stress_test(args.ftl_command, args.sol1_path, args.sol2_path)
    elif args.subcommand == "sync":
        sync_problem(args.args)

if __name__ == "__main__":
    main()
