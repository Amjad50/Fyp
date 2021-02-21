import pickle
import time
from argparse import ArgumentParser

from classifier.trainer import train_svm_model_from_features_dataset, generate_features_dataset


def run_training(classification_dataset_dir, augmentation_count=10, pickle_file_out=None):
    start = time.process_time_ns()
    dataset = generate_features_dataset(classification_dataset_dir, augmentation_count, progress=True)
    print('Training model...')
    model, score = train_svm_model_from_features_dataset(dataset)
    print('score:', score)
    end = time.process_time_ns()

    diff = (end - start) / 1e9
    print(f'took {diff:.05f} seconds')

    if pickle_file_out:
        print(f'outputting model object pickle to {pickle_file_out}...')

        with open(pickle_file_out, 'wb') as f:
            pickle.dump(model, f)


if __name__ == "__main__":
    parser = ArgumentParser(description='Fyp1 classfication trainer, will output a final report for model accuracy')
    parser.add_argument('--dir', '-d', type=str, required=True, help='the dataset directory (input)')
    parser.add_argument('--count', '-c', type=int, help='image augmentation count (dataset increase)')
    parser.add_argument('--out', '-o', type=str, help='pickled output of the model')

    args = parser.parse_args()

    run_training(args.dir, args.count, args.out)
