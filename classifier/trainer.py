from os import path

import albumentations
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from skimage.feature import hog
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from tqdm import tqdm

from segmenter.symbol_segmenter import segment_image


def generate_image_augmentation(image, count):
    transform = albumentations.Compose([
        albumentations.RandomScale(),
        albumentations.Rotate(limit=(-15, 15)),
        albumentations.Blur(),
    ])

    return [transform(image=image)['image'] for _ in range(count)]


def generate_features_dataset(classification_dataset_dir, augmentation_cont, progress=False):
    """
    Parse the dataset in the input directory and extract `hog` features from them, also if the dataset is small
    it will add more elements using augmentation
    """
    if not path.exists(classification_dataset_dir):
        raise FileNotFoundError(classification_dataset_dir)
    if not path.isdir(classification_dataset_dir):
        raise Exception(f"{classification_dataset_dir} is found but it is a file and not a directory")

    tqdm_reading_images = None
    tqdm_augmentation = None
    tqdm_preprocessing = None
    tqdm_feature_extraction = None

    metadata_file = path.join(classification_dataset_dir, 'metadata.csv')

    if not path.isfile(metadata_file):
        raise FileNotFoundError(metadata_file)

    # read the dataset
    dataset = pd.read_csv(metadata_file, header=None, dtype=str)
    dataset.columns = ['expr', 'base_filename']

    if progress:
        tqdm_reading_images = tqdm(total=len(dataset))
        tqdm_reading_images.set_description("Reading images")

    # helper to get images of all files
    def get_image(base_filename):
        if progress:
            tqdm_reading_images.update(1)

        filename = path.join(classification_dataset_dir, f'{base_filename}.png')

        return np.asarray(Image.open(filename).convert('L'))

    dataset['raw_image'] = dataset.base_filename.map(get_image)

    if progress:
        tqdm_reading_images.close()

    # if we don't have a lot of data, then augment
    if len(dataset) < 1000:
        if progress:
            tqdm_augmentation = tqdm(total=len(dataset))
            tqdm_augmentation.set_description("Augmenting images")

        # controls how many new images to generate for each input image
        def image_augmentation_wrapper(label_image_pair):
            if progress:
                tqdm_augmentation.update(1)
            label = label_image_pair[0]
            input_img = label_image_pair[1]

            transformed_images = [[label, img] for img in generate_image_augmentation(input_img, augmentation_cont)]

            return transformed_images

        new_labeled_images = dataset[['expr', 'raw_image']].apply(image_augmentation_wrapper, axis=1)
        if progress:
            tqdm_augmentation.close()

        dataset_extension = pd.concat(
            [pd.DataFrame(new_images, columns=['expr', 'raw_image']) for new_images in new_labeled_images],
            ignore_index=True)

        # extend the dataset with the new data
        dataset = dataset.append(dataset_extension, ignore_index=True)

    if progress:
        tqdm_preprocessing = tqdm(total=len(dataset))
        tqdm_preprocessing.set_description("Preprocessing images")

    # convert to a size similar across all images
    def normalize_image(img_array):
        if progress:
            tqdm_preprocessing.update(1)
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

        resized_img = cropped_img.resize((int(resize_ratio * w), int(resize_ratio * h)))

        gray_img = resized_img.convert('L')
        inverted_gray_image = ImageOps.invert(gray_img)
        w, h = inverted_gray_image.size

        final_img = Image.new('L', (128, 128))
        final_img.paste(inverted_gray_image, ((128 - w) // 2, (128 - h) // 2))

        return np.asarray(final_img)

    dataset['normalized_image'] = dataset.raw_image.map(normalize_image)
    if progress:
        tqdm_preprocessing.close()

    if progress:
        tqdm_feature_extraction = tqdm(total=len(dataset))
        tqdm_feature_extraction.set_description("Feature extraction")

    def get_hog_image_and_feature(img):
        if progress:
            tqdm_feature_extraction.update(1)
        fd, hog_image = hog(img, orientations=8, pixels_per_cell=(16, 16),
                            cells_per_block=(1, 1), visualize=True)

        return hog_image, fd

    dataset[['hog_image', 'hog_feature']] = pd.DataFrame(
        dataset.normalized_image.map(get_hog_image_and_feature).to_list())

    if progress:
        tqdm_feature_extraction.close()

    return dataset


def train_svm_model_from_features_dataset(dataset):
    """
    Will create a new svm model trained with the processed and extracted features dataset, which
    can be generated from the function `generate_features_dataset`
    """
    y = np.asarray(dataset.expr)
    X = np.stack(dataset.hog_feature)

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=100, test_size=0.2)

    model = SVC(kernel='linear')
    model.fit(X_train, y_train)

    y_predict = model.predict(X_test)
    score = accuracy_score(y_test, y_predict)

    return model, score


def train_svm_model(classification_dataset_dir, augmentation_count=10):
    """
    Will create a new svm model trained with the images data available in classification_dataset_dir
    """
    dataset = generate_features_dataset(classification_dataset_dir, augmentation_count)

    return train_svm_model_from_features_dataset(dataset)
