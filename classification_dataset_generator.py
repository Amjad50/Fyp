from argparse import ArgumentParser
from tqdm import tqdm
from dataset_generator.generator import generate_single_from_template
from string import digits, ascii_letters
import csv
import os

def generate_dataset(outdir):
    characters = list(digits + ascii_letters + "=-+")
    characters.extend(["\\Sigma", "\\pi"])

    csv_file = open(os.path.join(outdir, "metadata.csv"), "w")
    csv_writer = csv.writer(csv_file)

    counter = 0
    for i in tqdm(range(len(characters))):
        ch = characters[i]
        for template in ["{0}", "{0}^{{{{{0}^{{{{{0}}}}}}}}}"]:
            filename = f"{counter:04}"
            counter += 1
            expr = generate_single_from_template(template.format(ch), outdir, filename)
            csv_writer.writerow([expr, filename])

if __name__ == "__main__":
    parser = ArgumentParser(description='Fyp1 classfication dataset generator')
    parser.add_argument('--outdir', '-o', type=str, required=True, help='run generation in command line')

    args = parser.parse_args()

    generate_dataset(args.outdir)
