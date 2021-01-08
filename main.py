import sys

from dataset_generator.generator import generate_pdfs_from_templates
from dataset_generator.template import generate_latex_template
from tqdm import tqdm

if __name__ == "__main__":
    templates = [
            generate_latex_template("{num1} {operator1} {num2}{latin1}"),
            generate_latex_template("{num1} {operator1} {num2}{latin1} {operator2} {num3}{latin1}^{{{num4}}} = 0"),
            generate_latex_template("\\frac{{{num1}{latin1}}}{{{num2}}}"),
        ]

    if len(sys.argv) < 2:
        print(f"USAGE: {sys.argv[0]} <out_dir>")
    else:
        progress = tqdm()
        last_progress = 0

        def updater(a, b):
            global last_progress
            if not last_progress:
                # first time only
                progress.reset(b)

            progress.update(a - last_progress)
            progress.display()
            last_progress = a

        generate_pdfs_from_templates(templates, sys.argv[1], updater=updater, count_for_each=100)
        progress.close()