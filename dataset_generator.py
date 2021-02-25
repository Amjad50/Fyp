from argparse import ArgumentParser

from tqdm import tqdm

from dataset_generator.generator import generate_pdfs_from_templates


def command_line_generation(out_dir, count_for_each):
    templates = [
        "{num1} {operator1} {num2}{latin1}",
        "{num1} {operator1} {num2}{latin1} {operator2} {num3}{latin1}^{{{num4}}} = 0",
        "\\frac{{{num1}{latin1}}}{{{num2}}}",
        "{latin1}_{latin2} =\\frac{{{latin4}^{{{digit1}}}}}{{{latin3}}}"
    ]

    progress = tqdm()
    last_progress = 0

    def updater(a, b):
        nonlocal last_progress
        if not last_progress:
            # first time only
            progress.reset(b)

        progress.update(a - last_progress)
        progress.display()
        last_progress = a

    generate_pdfs_from_templates(templates, out_dir, updater=updater, count_for_each=count_for_each)
    progress.close()


if __name__ == "__main__":
    parser = ArgumentParser(description='Fyp1 dataset generator')
    parser.add_argument('--outdir', '-o', type=str, required=True, help='run generation in command line')
    parser.add_argument('--count', '-c', type=int, action='store', default=20,
            help='number of images to generate for each template [only for commandline] (default 20)')

    args = parser.parse_args()

    command_line_generation(args.outdir, args.count)

