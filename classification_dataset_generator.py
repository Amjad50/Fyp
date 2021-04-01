import csv
from argparse import ArgumentParser
from os import path, mkdir, remove
from string import digits, ascii_letters

from PIL import Image
from tqdm import tqdm

from dataset_generator.generator import generate_single_from_template
from segmenter.symbol_segmenter import segment_image


def generate_dataset(outdir):
    characters = list(digits + ascii_letters + "=-+()[],.")
    characters.extend(["\\Sigma", "\\pi", "\\int"])

    if not path.isdir(outdir):
        # try to create directory
        assert not path.exists(outdir), \
            f"Trying to create a directory with name {outdir}, but there is a file that already exists with that " \
            f"name "

        mkdir(outdir)

    csv_file = open(path.join(outdir, "metadata.csv"), "w")
    csv_writer = csv.writer(csv_file)

    counter = 0

    def get_next_filename():
        nonlocal counter
        filename = f"{counter:04}"
        counter += 1
        return filename

    plain_template = "{0}"
    power_template = "{0}^{{{{{0}^{{{{{0}}}}}}}}}"

    for i in tqdm(range(len(characters))):
        ch = characters[i]

        plain_filename = get_next_filename()
        power_filename = 'tmp_power_expr'
        plain_expr = generate_single_from_template(plain_template.format(ch),
                                                   outdir, plain_filename)
        _power_expr = generate_single_from_template(power_template.format(ch),
                                                    outdir, power_filename)

        csv_writer.writerow([plain_expr, plain_filename])

        tmpimg = Image.open(path.join(outdir, power_filename + ".png"))
        crops_images = segment_image(tmpimg)

        if len(crops_images) != 3:
            print(f"[ERROR] element {plain_expr} did not produce 3 crops, but produced {len(crops_images)}")

        for crop, cropped_img in crops_images:
            filename = get_next_filename()
            cropped_img.save(path.join(outdir, filename + ".png"))
            csv_writer.writerow([plain_expr, filename])

    remove(path.join(outdir, 'tmp_power_expr.png'))


if __name__ == "__main__":
    parser = ArgumentParser(description='Fyp1 classfication dataset generator')
    parser.add_argument('--outdir', '-o', type=str, required=True, help='run generation in command line')

    args = parser.parse_args()

    generate_dataset(args.outdir)
