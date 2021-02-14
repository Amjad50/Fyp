import os
import subprocess
import sys
import csv
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

def fill_expression_template(template):
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

def fill_latex_file_template(expr):
    return generate_latex_template(expr)

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

    csv_file = open("metadata.csv", "w")
    csv_writer = csv.writer(csv_file)

    # header
    csv_writer.writerow(["file_basename", "expr"])

    all_size = len(templates) * count_for_each
    # Because we have 3 stages
    full_progress = all_size * 2
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

            expr = fill_expression_template(template)
            csv_writer.writerow([file_basename, expr])

            with open(tex_filename, "w") as f:
                file_content = fill_latex_file_template(expr)
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
                          pdf_filename, "-quality", "10", "-colorspace", "Gray",
                          "-depth", "1", "-alpha", "remove", png_filename],
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Stage 3: finish up
    file_names = list(remaining_filenames)
    for file_basename, process in zip(file_names, executor.finish()):
        updater_inner(progress_counter, full_progress)
        ret_code = process.wait()
        if ret_code != 0:
            print(f"[ERROR] Converting {file_basename}.pdf to image failed, returned with code={ret_code}")

        for ext in ["tex", "aux", "pdf", "log"]:
            os.remove(f"{file_basename}.{ext}")

    os.remove("formula.tex")

    csv_file.close()
    os.chdir("..")

def generate_single_from_template(template, output_dir, file_basename, image_density=500):
    assert output_dir, "output_dir must not be empty"
    assert file_basename, "naming_format must not be empty"

    if not path.isdir(output_dir):
        # try to create directory
        assert not path.exists(output_dir), \
            f"Trying to create a directory with name {output_dir}, but there is a file that already exists with that " \
            f"name "

        os.mkdir(output_dir)

    # Go into the directory, because "pdflatex" outputs into the current working
    # directory
    os.chdir(output_dir)

    # Step 0: put the formula.tex file
    with open("formula.tex", "w") as f:
        f.write(formula_strap)

    tex_filename = file_basename + ".tex"

    if path.exists(tex_filename):
        print(f"[WARN]: Trying to generate file {tex_filename}, which already exists, skipping...",
              file=sys.stderr)

    expr = fill_expression_template(template)

    with open(tex_filename, "w") as f:
        file_content = fill_latex_file_template(expr)
        f.write(file_content)

    subprocess.Popen(["pdflatex", tex_filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

    # Stage 2: converting pdfs into images
    pdf_filename = file_basename + ".pdf"
    png_filename = file_basename + ".png"

    image_density = str(image_density)
    subprocess.Popen(["convert", "-density", image_density,
                      pdf_filename, "-quality", "10", "-colorspace", "Gray",
                      "-depth", "1", "-alpha", "remove", png_filename],
                     stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()

    # Stage 3: finish up
    for ext in ["tex", "aux", "pdf", "log"]:
        os.remove(f"{file_basename}.{ext}")

    os.remove("formula.tex")

    os.chdir("..")

    return expr
