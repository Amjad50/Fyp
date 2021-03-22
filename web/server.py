from base64 import b64decode
from io import BytesIO
from os import path, remove as os_remove_file
from tempfile import mkdtemp, mktemp

from PIL import Image
from flask import Flask, jsonify, abort

from classifier.classifier import SVMClassifier
from classifier.labeler import get_labeled_crops, draw_labeled_crops
from dataset_generator.generator import generate_single_from_template
from parser.tree import SymbolTree
from segmenter.labeler import draw_crops_rects
from segmenter.symbol_segmenter import segment_image_crops
from .utils import json_arguments, response_image

app = Flask(__name__)

_svm_file_path = path.join(path.dirname(__file__), "..", "model", "svm.pkl")
svm_model = SVMClassifier(_svm_file_path)

generation_temp_folder = mkdtemp(prefix="latex_generation")


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


@app.route('/api/v1/symbol_tree', methods=["GET"])
@json_arguments([('image', str)])
def api_symbol_tree(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io)

    tree = SymbolTree.from_image(img, svm_model)
    tree_nodes_data = []

    for node in tree.nodes:
        single_node_data = dict()
        tree_nodes_data.append(single_node_data)

        single_node_data['position'] = node.position
        single_node_data['label'] = node.label
        node_relations_data = dict()
        single_node_data['relations'] = node_relations_data

        for relation_name, children in node.relations.items():
            # if a main relation and has members
            if 'inverse' not in relation_name and len(children) > 0:
                children_relations_positions = []
                node_relations_data[relation_name] = children_relations_positions

                for child_node in children:
                    children_relations_positions.append(child_node.position)

    return {"tree": tree_nodes_data}


@app.route('/api/v1/generate_latex', methods=["GET"])
@json_arguments([('template', str)])
def api_generate_latex(json_data):
    img_filename = mktemp(prefix="latex_img", dir=generation_temp_folder)

    try:
        generate_single_from_template(json_data['template'], generation_temp_folder, path.basename(img_filename))
    # here `ValueError` is meant to only catch the formatting error that may happen due to wrong template from the user
    except ValueError as e:
        abort(400, f"Error in formatting: {e}")

    img = Image.open(img_filename + ".png")

    # remove the file after generation as they are not needed now
    os_remove_file(img_filename + ".png")

    return response_image(img)


@app.route('/api/v1/latex_template_variables', methods=["GET"])
def api_latex_template_variables():
    # TODO: this is very manual, and in case of any change in the generation module we would need to change this.
    #  so fix this
    return {
        'variables': [
            "digit[1-5]: a single digit",
            "num[1-5]: a number from -1000 to 1000",
            "latin[1-5]: a single ascii (upper/lower)case letter",
            "operator[1-5]: a single operator character from ['+', '-', '=']",
        ]
    }


def run_server():
    app.run(debug=True)
