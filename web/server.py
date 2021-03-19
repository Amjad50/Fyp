from base64 import b64decode
from io import BytesIO
from os import path

from PIL import Image
from flask import Flask, jsonify

from classifier.classifier import SVMClassifier
from classifier.labeler import get_labeled_crops, draw_labeled_crops
from segmenter.labeler import draw_crops_rects
from segmenter.symbol_segmenter import segment_image_crops
from .utils import json_arguments, response_image

app = Flask(__name__)

_svm_file_path = path.join(path.dirname(__file__), "..", "model", "svm.pkl")
svm_model = SVMClassifier(_svm_file_path)


# return 400 errors in json format
@app.errorhandler(400)
def resource_not_found(e):
    return jsonify(error=str(e)), 400


@app.route('/api/v1/image_segments', methods=["GET"])
@json_arguments([('image', str)])
def api_image_segments(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io)

    crops = segment_image_crops(img)

    return {
        "crops": crops
    }


@app.route('/api/v1/draw_image_segments', methods=["GET"])
@json_arguments([('image', str)])
def api_draw_image_segments(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io)

    output_img = draw_crops_rects(img)

    return response_image(output_img)


@app.route('/api/v1/labeled_crops', methods=["GET"])
@json_arguments([('image', str)])
def api_labeled_crops(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io)

    labeled_crops = get_labeled_crops(img, svm_model)

    return {
        "labeled_crops": labeled_crops
    }


@app.route('/api/v1/draw_labeled_crops', methods=["GET"])
@json_arguments([('image', str)], [('no_crops', bool, False)])
def api_draw_labeled_crops(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io)

    labeled_crops = get_labeled_crops(img, svm_model)
    labels, crops = list(zip(*labeled_crops))

    # should we draw the crops rects or not
    if json_data['no_crops']:
        second_stage_img = img
    else:
        second_stage_img = draw_crops_rects(img, crops)

    output_img = draw_labeled_crops(second_stage_img, labeled_crops)

    return response_image(output_img)


def run_server():
    app.run(debug=True)
