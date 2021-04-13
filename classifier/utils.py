import numpy as np
from PIL import Image, ImageOps
from skimage.feature import hog

from segmenter.symbol_segmenter import segment_image


# convert to a size similar across all images
def normalize_image(img_array):
    img = Image.fromarray(img_array).convert('1')

    crops_images = segment_image(img)
    crops, cropped_images = list(zip(*crops_images))

    if len(crops) != 1:
        # FIXME: manual crop, since only one symbol per picture
        w, h = img.size

        img_arr = np.asarray(img)

        left, top, right, down = 1000, 1000, -1000, -1000

        for x in range(w):
            for y in range(h):
                # black
                if not img_arr[y, x]:
                    if y > down:
                        down = y
                    if y < top:
                        top = y
                    if x > right:
                        right = x
                    if x < left:
                        left = x

        crop = (left, top, right + 1, down + 1)
        cropped_images = [img.crop(crop)]

    cropped_img = cropped_images[0]

    w, h = cropped_img.size
    resize_ratio = min(128 / w, 128 / h)
    new_size = [int(resize_ratio * w), int(resize_ratio * h)]

    # sometimes, the frac will have 0 height, because of resize, so make sure to at least leave one pixel
    if new_size[0] == 0:
        new_size[0] = 1
    if new_size[1] == 0:
        new_size[1] = 1

    resized_img = cropped_img.resize(new_size)

    gray_img = resized_img.convert('L')
    inverted_gray_image = ImageOps.invert(gray_img)
    w, h = inverted_gray_image.size

    final_img = Image.new('L', (128, 128))
    final_img.paste(inverted_gray_image, ((128 - w) // 2, (128 - h) // 2))

    return np.asarray(final_img)


def extract_hog_features(img):
    img = normalize_image(np.asarray(img))
    fd = hog(img, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1))

    return fd
