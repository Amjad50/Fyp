import pickle

from .utils import extract_hog_features
from .trainer import train_svm_model


class SVMClassifier:
    def __init__(self, svm_pickle_filename=None):
        if svm_pickle_filename:
            svm_pickle_file = open(svm_pickle_filename, 'rb')
            self.model = pickle.load(svm_pickle_file)
        else:
            self.model = None

    def import_from_pickle(self, svm_pickle_filename):
        assert svm_pickle_filename, "svm_pickle_filename must not be None"

        svm_pickle_file = open(svm_pickle_filename, 'rb')
        self.model = pickle.load(svm_pickle_file)

    def train_new_model(self, classification_dataset_dir, augmentation_count=10):
        model, score = train_svm_model(classification_dataset_dir,
                augmentation_count=augmentation_count)

        print(f'[LOG] trained a new model, with score = {score}')

        self.model = model

    def predict_label(self, img):
        if not self.model:
            raise Exception('There is no model, train a new model or import one from pickle')
        features = extract_hog_features(img)
        return self.model.predict([features])[0]
