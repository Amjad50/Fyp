import time
from argparse import ArgumentParser
from os import path

import pandas as pd
from PIL import Image
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from classifier.classifier import SVMClassifier
from parser.tree import SymbolTree
from parser.utils import optimize_latex_string

parser = ArgumentParser(description='Fyp1 system prediction tester')
parser.add_argument('--dataset', '-d', type=str, required=True, help='dataset dir containing the `metadata.csv` file')
parser.add_argument('--model', '-m', type=str, required=True, help='pickle model for the SVMClassifier')

args = parser.parse_args()

dataset_folder = args.dataset

dataset = pd.read_csv(path.join(dataset_folder, 'metadata.csv'))
dataset.head()

svm_model = SVMClassifier()
svm_model.import_from_pickle(args.model)

prediction_progress = tqdm(total=len(dataset))


def predict_latex(img_filename):
    prediction_progress.update(1)
    img = Image.open(path.join(dataset_folder, f'{img_filename}.png'))

    tree = SymbolTree.from_image(img, svm_model)

    tree.optimize_connections()

    return tree.get_latex_string(optimize=True)


exprs = dataset.expr.map(optimize_latex_string)

start_prediction_time = time.process_time_ns()
predicted_exprs = dataset.file_basename.map(predict_latex)
end_prediction_time = time.process_time_ns()

prediction_progress.close()

time_took = (end_prediction_time - start_prediction_time) / 1e9
score = accuracy_score(exprs, predicted_exprs)
print(f'prediction took {time_took:.05f} for {len(dataset)} images')
print('score', score)
