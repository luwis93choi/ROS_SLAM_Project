### Image retrieval using CNN-based encoder (Feature extractor) ###
# Import the necessary packages
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.models import load_model
from tensorflow.keras.datasets import mnist
from imutils import build_montages
import numpy as np
import argparse
import pickle
import cv2

### GPU Support Activation ###
# Enable the use of GPUs by allowing their memory growth
# Reference : https://inpages.tistory.com/155
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)

# Function for computing the similarity between two feature vectors using Euclidean distance
def euclidean(a, b):
    # Compute and return the euclidean distance between two vectors
    return np.linalg.norm(a - b)

# Searching Function
def perform_search(queryFeatures, index, maxResults=64):
    # Initialize the list of results
    results = []

    # Loop over the indexes
    for i in range(0, len(index['features'])):
        # Compute the euclidean distance between the query image features 
        # and the current input image features
        # Update the result list with 2-tuple consisting of the computed distance
        # and the index of the image
        d = euclidean(queryFeatures, index['features'][i])
        results.append((d, i))

    # Sort the results and grab the top results
    results = sorted(results)[:maxResults]

    # Return the list of results
    return results

# Construct the argument parser
ap = argparse.ArgumentParser()
ap.add_argument('-m', '--model', type=str, required=True,
    help='Path to trained autoencoder')
ap.add_argument('-i', '--index', type=str, required=True,
    help='Path to features index file')
ap.add_argument('-s', '--sample', type=int, default=10,
    help='Number of testing queries to perform')
args = vars(ap.parse_args())

# Load MNIST dataset
print('[INFO] Loading MNIST dataset...')
((trainX, _), (testX, _)) = mnist.load_data()

# Add a channel dimension to every image in the dataset,
# then scale the pixel intensities to the range [0, 1]
trainX = np.expand_dims(trainX, axis=-1)
testX = np.expand_dims(testX, axis=-1)
trainX = trainX.astype('float32') / 255.0
testX = testX.astype('float32') / 255.0

# Load the autoencoder model and index from disk
print('[INFO] Loading autoencoder and index...')
autoencoder = load_model(args['model'])
index = pickle.loads(open(args['index'], 'rb').read())

# Create the encoder model which consists of 'just' the encoder portion of the autoencoder
encoder = Model(inputs=autoencoder.input, outputs=autoencoder.get_layer('encoded').output)

# Quantify the contents of input testing images using the encoder
print('[INFO] Encoding testing images...')
features = encoder.predict(testX)

### Take a random sample of images and turn them into queries
# Randomly sample a set of testing query image indexes
queryIdxs = list(range(0, testX.shape[0]))
queryIdxs = np.random.choice(queryIdxs, size=args['sample'], replace=False)

# Loop over the testing indexes
for i in queryIdxs:
    # Take the features for the current query image
    # Find all similar images in our dataset and initialize the list of result images
    queryFeatures = features[i]
    results = perform_search(queryFeatures, index, maxResults=255)
    images = []

    # Loop over the results
    for (d, j) in results:
        # Grab the result image and convert it back to the range [0, 255]
        # Update the image list
        image = (trainX[j] * 255).astype('uint8')
        image = np.dstack([image] * 3)
        images.append(image)

    # Display the query image
    query = (testX[i] * 255).astype('uint8')
    cv2.imshow('Query', query)

    # Build a montage from the results and display it
    montage = build_montages(images, (28, 28), (15, 15))[0]
    cv2.imshow('Results', montage)
    cv2.waitKey(0)