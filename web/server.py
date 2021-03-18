from base64 import b64decode
from io import BytesIO

from PIL import Image
from flask import Flask, jsonify

from segmenter.labeler import draw_crops_rects
from segmenter.symbol_segmenter import segment_image_crops
from .utils import json_arguments, response_image

app = Flask(__name__)


# return 400 errors in json format
@app.errorhandler(400)
def resource_not_found(e):
    return jsonify(error=str(e)), 400


@app.route('/api/v1/segment_image', methods=["GET"])
@json_arguments([('image', str)])
def api_segment_image(json_data):
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


def run_server():
    app.run(debug=True)
