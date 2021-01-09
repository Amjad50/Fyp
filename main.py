from argparse import ArgumentParser

from tqdm import tqdm

from dataset_generator.generator import generate_pdfs_from_templates
from web import server as web_server


def command_line_generation(out_dir, count_for_each):
    templates = [
        "{num1} {operator1} {num2}{latin1}",
        "{num1} {operator1} {num2}{latin1} {operator2} {num3}{latin1}^{{{num4}}} = 0",
        "\\frac{{{num1}{latin1}}}{{{num2}}}",
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--outdir', '-o', type=str, help='run generation in command line')
    group.add_argument('--web', '-w', action='store_true', help='run flask webserver frontend for dataset generation')
    parser.add_argument('--count', '-c', type=int, action='store', default=20,
            help='number of images to generate for each template [only for commandline] (default 20)')

    args = parser.parse_args()

    if args.web:
        # run web server
        web_server.run_server()
    elif args.outdir:
        command_line_generation(args.outdir, args.count)
    else:
        raise ValueError('invalid args')



