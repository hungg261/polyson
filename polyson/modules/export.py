
import os
import re
import json
import shutil
import subprocess


def generate_pdf(args):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    statements_dir = os.path.join(base_dir, "defaults", "statements")
    
    if not os.path.exists(statements_dir):
        print("[ERROR] Statements template directory missing in defaults.")
        return

    enable_watermark = True
    watermark_text = None
    show_title = True
    show_toc = True
    open_after_build = False
    export_images = False
    custom_title = None
    custom_subtitle = None
    custom_hl = None
    custom_hr = None

    paths = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--open" or arg == "--view":
            open_after_build = True
        elif arg == "--img" or arg == "--image":
            export_images = True
        elif arg == "--no-watermark":
            enable_watermark = False
        elif arg == "--watermark" and i + 1 < len(args) and not args[i+1].startswith("--"):
            watermark_text = args[i+1]
            i += 1
        elif arg == "--no-title":
            show_title = False
        elif arg == "--no-toc":
            show_toc = False
        elif arg == "--title" and i + 1 < len(args):
            custom_title = args[i+1]
            i += 1
        elif arg == "--subtitle" and i + 1 < len(args):
            custom_subtitle = args[i+1]
            i += 1
        elif arg == "--header-left" and i + 1 < len(args):
            custom_hl = args[i+1]
            i += 1
        elif arg == "--header-right" and i + 1 < len(args):
            custom_hr = args[i+1]
            i += 1
        else:
            paths.append(arg)
        i += 1

    contest_folder_pdf_name = None
    target_paths = []

    if len(paths) == 1 and paths[0].endswith("contest.json") and os.path.exists(paths[0]):
        folder_path = os.path.dirname(os.path.abspath(paths[0]))
        folder_name = os.path.basename(folder_path)
        contest_folder_pdf_name = f"{folder_name}.pdf"
        with open(paths[0], "r", encoding="utf-8") as f:
            c_data = json.load(f)
            target_paths = [os.path.join(folder_path, p) for p in c_data.get("problems", [])]
            if not custom_title:
                custom_title = c_data.get("contest_name")
    elif not paths and os.path.exists("contest.json"):
        folder_name = os.path.basename(os.getcwd())
        contest_folder_pdf_name = f"{folder_name}.pdf"
        with open("contest.json", "r", encoding="utf-8") as f:
            c_data = json.load(f)
            target_paths = c_data.get("problems", [])
            if not custom_title:
                custom_title = c_data.get("contest_name")
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

    latex_escapes = {
        '\\': r'\textbackslash{}',
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in latex_escapes.keys()))

    def clean_latex(text):
        if not text:
            return text
        return pattern.sub(lambda m: latex_escapes[m.group(0)], str(text))

    watermark_text = clean_latex(watermark_text)
    custom_title = clean_latex(custom_title)
    custom_subtitle = clean_latex(custom_subtitle)
    custom_hl = clean_latex(custom_hl)
    custom_hr = clean_latex(custom_hr)

    build_dir = os.path.abspath(".polyson_pdf_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    try:
        for item in os.listdir(statements_dir):
            s = os.path.join(statements_dir, item)
            d = os.path.join(build_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)

        flags_path = os.path.join(build_dir, "config_flags.tex")
        with open(flags_path, "w", encoding="utf-8") as f:
            f.write(f"\\settoggle{{ShowTitlePage}}{{{'true' if show_title else 'false'}}}\n")
            f.write(f"\\settoggle{{ShowTOC}}{{{'true' if show_toc else 'false'}}}\n")
            f.write(f"\\settoggle{{EnableWatermark}}{{{'true' if enable_watermark else 'false'}}}\n")
            
            if watermark_text:
                f.write(f"\\renewcommand{{\\WatermarkText}}{{{watermark_text}}}\n")
            if custom_title:
                f.write(f"\\renewcommand{{\\Title}}{{{custom_title}}}\n")
            if custom_subtitle:
                f.write(f"\\renewcommand{{\\Subtitle}}{{{custom_subtitle}}}\n")
            if custom_hl:
                f.write(f"\\renewcommand{{\\HeaderL}}{{{custom_hl}}}\n")
            if custom_hr:
                f.write(f"\\renewcommand{{\\HeaderR}}{{{custom_hr}}}\n")

        contents_path = os.path.join(build_dir, "contents.tex")
        with open(contents_path, "w", encoding="utf-8") as f:
            for i, tex in enumerate(valid_tex_files):
                formatted_path = tex.replace("\\", "/")
                f.write(f"\\input{{{formatted_path}}}\n")
                if i < len(valid_tex_files) - 1:
                    f.write("\\clearpage\n")

        print(f"[*] Compiling for {len(valid_tex_files)} problem(s)...")

        has_latexmk = shutil.which("latexmk") is not None

        if has_latexmk:
            subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
                cwd=build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            compiler = "pdflatex"
            cmd = [compiler, "-interaction=nonstopmode", "main.tex"]
            subprocess.run(cmd, cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(cmd, cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output_pdf = os.path.join(build_dir, "main.pdf")
        if os.path.exists(output_pdf):
            if contest_folder_pdf_name:
                sub_folder_name = contest_folder_pdf_name.rsplit('.', 1)[0]
            elif len(valid_tex_files) == 1 and paths:
                sub_folder_name = os.path.basename(os.path.abspath(paths[0]))
            elif len(valid_tex_files) == 1 and not paths:
                sub_folder_name = "statement"
            else:
                sub_folder_name = "contest"

            if export_images:
                temp_img_dir = os.path.join(build_dir, "statements", sub_folder_name)
                os.makedirs(temp_img_dir, exist_ok=True)

                prefix_path = os.path.join(temp_img_dir, "page")
                subprocess.run(
                    ["pdftoppm", "-png", "-r", "150", output_pdf, prefix_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                root_to_zip = os.path.join(build_dir, "statements")
                zip_base_name = os.path.join(os.getcwd(), "statements")
                archive_path = shutil.make_archive(zip_base_name, 'zip', root_to_zip)

                print(f"[SUCCESS] Exported images zip: {os.path.basename(archive_path)}")

                if open_after_build:
                    os.startfile(archive_path)
            else:
                final_pdf_path = os.path.join(os.getcwd(), f"{sub_folder_name}.pdf")

                shutil.copy2(output_pdf, final_pdf_path)
                print(f"[SUCCESS] Generated PDF: {os.path.basename(final_pdf_path)}")

                if open_after_build:
                    os.startfile(final_pdf_path)
        else:
            print("[ERROR] LaTeX compilation failed. Please check your statement.tex syntax.")

    finally:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
