from PIL import ImageDraw, ImageFont

from segmenter.symbol_segmenter import segment_image
from .classifier import SVMClassifier


def draw_labeled_crops(img, labeled_crops):
    labeled_img = img.copy()
    labeled_img = labeled_img.convert('RGB')
    img_d = ImageDraw.Draw(labeled_img)

    font = ImageFont.truetype('arial.ttf', size=20)

    for i, labeled_crop in enumerate(labeled_crops):
        label, crop = labeled_crop
        l, t, r, d = crop
        l -= 1
        t -= 1
        fw, fh = font.getsize(label)
        img_d.text((l - fw, t - fh), label, font=font, fill=(67, 64, 255))

    return labeled_img


def get_labeled_crops(img, svm_model: SVMClassifier):
    crops_images = segment_image(img)
    crops, cropped_images = list(zip(*crops_images))

    predicted_labels = []

    for crop, cropped_img in crops_images:
        predicted_labels.append(svm_model.predict_label(cropped_img))

    return list(zip(predicted_labels, crops))