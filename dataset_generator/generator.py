import os
import subprocess
import sys
from os import path
from random import randint, choice
from string import ascii_letters

from utils.parallel_executer import ParallelExecutor
from .template import generate_latex_template, formula_strap

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


def fix_signs(expr):
    return expr.replace('--', '+') \
        .replace('- -', '+') \
        .replace('- +', '-') \
        .replace('-+', '-') \
        .replace('+-', '-') \
        .replace('+ -', '-')


def fill_template(template):
    return fix_signs(template.format(
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
    ))


def generate_pdfs_from_templates(templates, output_dir, count_for_each=10, naming_format="expr_{num:05}", updater=None,
                                 image_density=500):
    assert output_dir, "output_dir must not be empty"
    assert count_for_each >= 0, "count_for_each must be a positive number"
    assert naming_format, "naming_format must not be empty"
    assert updater is None or callable(updater), "updater must be callable or None"

    def updater_inner(a, b):
        if updater:
            updater(a, b)

    if not path.isdir(output_dir):
        # try to create directory
        assert not path.exists(output_dir), \
            f"Trying to create a directory with name {output_dir}, but there is a file that already exists with that " \
            f"name "

        os.mkdir(output_dir)

    # Go into the directory, because "pdflatex" outputs into the current working
    # directory
    os.chdir(output_dir)

    all_size = len(templates) * count_for_each
    # Because we have 3 stages
    full_progress = all_size * 3
    progress_counter = 0

    # Number of expressions so far
    expr_counter = 0

    # Step 0: put the formula.tex file
    with open("formula.tex", "w") as f:
        f.write(formula_strap)

    # Stage 1: creating uncropped PDFs
    file_names = []
    executor = ParallelExecutor(20)
    for template in templates:
        for _ in range(count_for_each):
            file_basename = naming_format.format(num=expr_counter)
            tex_filename = file_basename + ".tex"
            expr_counter += 1

            progress_counter += 1
            updater_inner(progress_counter, full_progress)

            if path.exists(tex_filename):
                print(f"[WARN]: Trying to generate file {tex_filename}, which already exists, skipping...",
                      file=sys.stderr)

                progress_counter += 2
                updater_inner(progress_counter, full_progress)
                continue

            with open(tex_filename, "w") as f:
                file_content = fill_template(template)
                f.write(file_content)

            file_names.append(file_basename)
            executor.execute(["pdflatex", tex_filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Stage 2: converting pdfs into images
    remaining_filenames = []
    old_processes = executor.finish()
    executor.clear()
    image_density = str(image_density)
    for file_basename, process in zip(file_names, old_processes):
        progress_counter += 1
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Cropping {file_basename}.pdf, returned with code={ret_code}, skipping...")
            progress_counter += 1
            updater_inner(progress_counter, full_progress)
            continue

        pdf_filename = file_basename + ".pdf"
        png_filename = file_basename + ".png"

        remaining_filenames.append(file_basename)
        executor.execute(["convert", "-density", image_density,
                          pdf_filename, "-quality", "10", "-colorspace", "RGB", "-alpha",
                          "remove", png_filename],
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Stage 3: finish up
    file_names = list(remaining_filenames)
    for file_basename, process in zip(file_names, executor.finish()):
        progress_counter += 1
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Converting {file_basename}.pdf to image failed, returned with code={ret_code}")

    os.chdir("..")
