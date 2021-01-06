
from os import path
import os
import sys
import subprocess
from tqdm import tqdm
from random import randint, choice
from string import ascii_letters

from template import generate_latex_template

# TODO: add operators like power, sub, frac and other stuff that need
#  special format in LaTeX
operators = "+-="

def _get_random_num():
    return randint(-1000, 1000)

def _get_random_latin_letter():
    return choice(ascii_letters)

def _get_random_operator():
    return choice(operators)

def load_templates_from_file(file_path):
    assert path.exists(file_path), f"The file_path {file_path}, does not exist"

    templates = []
    with open(file_path, "r") as f:
        for line in f:
            templates.append(generate_latex_template(line))

    return templates

def fill_template(template):
    return template.format(
            num1=_get_random_num(),
            num2=_get_random_num(),
            num3=_get_random_num(),
            num4=_get_random_num(),
            num5=_get_random_num(),
            latin1=_get_random_latin_letter(),
            latin2=_get_random_latin_letter(),
            latin3=_get_random_latin_letter(),
            latin4=_get_random_latin_letter(),
            latin5=_get_random_latin_letter(),
            operator1=_get_random_operator(),
            operator2=_get_random_operator(),
            operator3=_get_random_operator(),
            operator4=_get_random_operator(),
            operator5=_get_random_operator(),
        )

def generate_pdfs_from_templates(templates, output_dir, count_for_each=10, naming_format="expr_{num:05}", updater=None):
    assert output_dir, "output_dir must not be empty"
    assert count_for_each >= 0, "count_for_each must be a positive number"
    assert naming_format, "naming_format must not be empty"
    assert updater is None or callable(updater), "updater must be callable or None"

    def updater_inner(a, b):
        if updater:
            updater(a, b)

    if not path.isdir(output_dir):
        # try to create directory
        assert not path.exists(output_dir),\
                f"Trying to create a directory with name {output_dir}, but there is a file that already exists with that name"

        os.mkdir(output_dir)

    # Go into the directory, because "pdflatex" outputs into the current working
    # directory
    os.chdir(output_dir)

    all_size = len(templates) * count_for_each
    # Because we have 3 stages
    full_progress = all_size * 4
    progress_counter = 0

    # Number of expressions so far
    expr_counter = 0

    # Stage 1: creating uncropped PDFs
    pdf_processes = []
    file_names = []
    for template in templates:
        for _ in range(count_for_each):
            file_basename = naming_format.format(num=expr_counter)
            tex_filename = file_basename + ".tex"
            expr_counter += 1

            progress_counter += 1
            updater_inner(progress_counter, full_progress)

            if path.exists(tex_filename):
                print(f"[WARN]: Trying to generate file {tex_filename}, which already exists, skipping...",\
                        file=sys.stderr)

                progress_counter += 3
                updater_inner(progress_counter, full_progress)
                continue;

            with open(tex_filename, "w") as f:
                file_content = fill_template(template)
                f.write(file_content)

            file_names.append(file_basename)
            pdf_processes.append(subprocess.Popen(["pdflatex", tex_filename],\
                    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL))

    # Stage 2: cropping pdfs
    crop_processes = []
    remaing_filenames = []
    for file_basename, process in zip(file_names, pdf_processes):
        progress_counter += 1
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Generating {file_basename}.pdf, returned with code={ret_code}, skipping...")
            progress_counter += 2
            updater_inner(progress_counter, full_progress)
            continue;

        pdf_filename = file_basename + ".pdf"

        remaing_filenames.append(file_basename)
        crop_processes.append(subprocess.Popen(["pdfcrop", "--margins", "5 5 5 5",\
                pdf_filename, pdf_filename],\
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL))

    # Stage 3: converting pdfs into images
    file_names = list(remaing_filenames)
    remaing_filenames.clear()
    image_processes = []
    for file_basename, process in zip(file_names, crop_processes):
        progress_counter += 1
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Cropping {file_basename}.pdf, returned with code={ret_code}, skipping...")
            progress_counter += 1
            updater_inner(progress_counter, full_progress)
            continue;

        pdf_filename = file_basename + ".pdf"
        png_filename = file_basename + ".png"

        remaing_filenames.append(file_basename)
        image_processes.append(subprocess.Popen(["convert", "-density", "1000",\
                pdf_filename, "-quality", "100", "-colorspace", "RGB", "-alpha",\
                "remove", png_filename],\
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL))


    # Stage 4: finish up
    file_names = list(remaing_filenames)
    for file_basename, process in zip(file_names, image_processes):
        progress_counter += 1
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Converting {file_basename}.pdf to image failed, returned with code={ret_code}")

    os.chdir("..")

if __name__ == "__main__":
    templates = [
            generate_latex_template("{num1} {operator1} {num2}{latin1}")
        ]

    if len(sys.argv) < 2:
        print(f"USAGE: {sys.argv[0]} <out_dir>")
    else:
        progress = tqdm()
        def updater(a, b):
            progress.reset(b)
            progress.update(a)
            progress.display()
        generate_pdfs_from_templates(templates, sys.argv[1], updater=updater)
        progress.close()

