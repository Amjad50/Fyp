from base64 import b64decode
from io import BytesIO
from os import path, remove as os_remove_file
from tempfile import mkdtemp, mktemp

from PIL import Image
from flask import Flask, jsonify, abort, render_template, request

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


@app.route('/api/v1/image_segments', methods=["POST"])
@json_arguments([('image', str)])
def api_image_segments(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    crops = segment_image_crops(img)

    return {
        "crops": crops
    }


@app.route('/api/v1/draw_image_segments', methods=["POST"])
@json_arguments([('image', str)])
def api_draw_image_segments(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    output_img = draw_crops_rects(img)

    return response_image(output_img)


@app.route('/api/v1/labeled_crops', methods=["POST"])
@json_arguments([('image', str)])
def api_labeled_crops(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    labeled_crops = get_labeled_crops(img, svm_model)

    return {
        "labeled_crops": labeled_crops
    }


@app.route('/api/v1/draw_labeled_crops', methods=["POST"])
@json_arguments([('image', str)], [('no_crops', bool, False)])
def api_draw_labeled_crops(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    labeled_crops = get_labeled_crops(img, svm_model)
    labels, crops = list(zip(*labeled_crops))

    # should we draw the crops rects or not
    if json_data['no_crops']:
        second_stage_img = img
    else:
        second_stage_img = draw_crops_rects(img, crops)

    output_img = draw_labeled_crops(second_stage_img, labeled_crops)

    return response_image(output_img)


@app.route('/api/v1/symbol_tree', methods=["POST"])
@json_arguments([('image', str)])
def api_symbol_tree(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

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


@app.route('/api/v1/draw_symbol_tree', methods=["POST"])
@json_arguments([('image', str)], [('no_crops', bool, False), ('no_labels', bool, False)])
def api_draw_symbol_tree(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    labeled_crops = get_labeled_crops(img, svm_model)
    labels, crops = list(zip(*labeled_crops))

    tree = SymbolTree.from_labeled_crops(labeled_crops)

    if json_data['no_crops']:
        second_stage_img = img
    else:
        second_stage_img = draw_crops_rects(img, crops)

    if json_data['no_labels']:
        third_stage_img = second_stage_img
    else:
        third_stage_img = draw_labeled_crops(second_stage_img, labeled_crops)

    output_img = tree.draw_min_connections(third_stage_img)

    return response_image(output_img)


@app.route('/api/v1/predict_latex', methods=["POST"])
@json_arguments([('image', str)], [('optimize', bool, True)])
def api_predict_latex(json_data):
    image_raw = b64decode(json_data['image'])
    image_bytes_io = BytesIO(image_raw)

    img = Image.open(image_bytes_io).convert('1')

    tree = SymbolTree.from_image(img, svm_model)

    latex_string = tree.get_latex_string(optimize=json_data['optimize'])

    return {"latex": latex_string}


@app.route('/api/v1/compile_latex', methods=["GET"])
def api_compile_latex():
    template = request.args.get('template')

    if template is None:
        abort(400, "Please specify `template` argument")

    img_filename = mktemp(prefix="latex_img", dir=generation_temp_folder)

    try:
        generate_single_from_template(template, generation_temp_folder, path.basename(img_filename))
    # here `ValueError` is meant to only catch the formatting error that may happen due to wrong template from the user
    except ValueError as e:
        abort(400, f"Error in formatting: {e}, try use double curly brackets, extra: {e}")
    except KeyError as e:
        abort(400, f"Error in formatting: {e}, try use double curly brackets, extra: {e}")
    except IndexError as e:
        abort(400, f"Error in formatting: {e}, try use double curly brackets, extra: {e}")

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
            ["digit", [1, 5], "A single digit"],
            ["num", [1, 5], "A number from -999 to 999"],
            ["pos", [1, 5], "A number from 1 to 999"],
            ["neg", [1, 5], "A number from -999 to -1"],
            ["latin", [1, 5], "A single ascii (upper/lower)case letter"],
            ["operator", [1, 5], "A single operator character from ['+', '-', '=']"],
        ]
    }


@app.route('/')
def page_home():
    return render_template('home.html')


@app.route('/latex_compiler')
def page_latex_compiler():
    return render_template('latex_compiler.html', template_variables=api_latex_template_variables())


@app.route('/tester')
def page_tester():
    return render_template('tester.html', template_variables=api_latex_template_variables())


def run_server(port: int):
    app.run(debug=True, host="0.0.0.0", port=port)
