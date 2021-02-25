# helper script to find the default sizes of all symbols in the default
# font size (no power or sub)

from os import chdir
from tempfile import mkdtemp
from string import digits, ascii_letters

from PIL import Image
from tqdm import tqdm

from dataset_generator.generator import generate_single_from_template
from segmenter.symbol_segmenter import segment_image_crops
from segmenter.utils import box_size

def get_symbol_size(expr):
    filename = "tmp_file"

    _ = generate_single_from_template(expr, "." , filename)

    img = Image.open(filename + ".png")
    crops = segment_image_crops(img)

    assert len(crops) == 1

    return box_size(crops[0])

if __name__ == "__main__":
    characters = list(digits + ascii_letters + "=-+")
    characters.extend(["\\Sigma", "\\pi"])

    tmp_dir = mkdtemp()
    chdir(tmp_dir)

    symbol_sizes_dict = {
        ch: get_symbol_size(ch)
        for ch in tqdm(characters)
    }

    print(symbol_sizes_dict)

