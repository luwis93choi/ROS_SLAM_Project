### Image Indexer ###
# Import the necessary packages
import tensorflow as tf
from tensorflow.keras.models import Model 
from tensorflow.keras.models import load_model 
from tensorflow.keras.datasets import mnist
import numpy as np
import argparse
import pickle

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

# Construct the argument parser
ap = argparse.ArgumentParser()
ap.add_argument('-m', '--model', type=str, required=True,
    help='Path to trained autoencoder')
ap.add_argument('-i', '--index', type=str, required=True,
    help='Path to output features index file')
args = vars(ap.parse_args())

# Load MNIST dataset
print('[INFO] Loading MNIST training split...')
((trainX, _), (testX, _)) = mnist.load_data()

# Add a channel dimension to every image in the training split, 
# then scale the pixel intensities to the range [0, 1]
trainX = np.expand_dims(trainX, axis=-1)
trainX = trainX.astype('float32') / 255.0

# Load autoencoder CNN model from disk
print('[INFO] Loading autoencoder model...')
autoencoder = load_model(args['model'])

# Create the encoder model which consists of 'just' the encoder portion of the autoencoder
encoder = Model(inputs=autoencoder.input, outputs=autoencoder.get_layer('encoded').output)

# Quantify the contents of the input images using the encoder
# Feed foward training images into encoder CNN model in order to proudce features
print('[INFO] Encoding images...')
features = encoder.predict(trainX)

# Construct a dictionary that maps the index of the MNIST training images to
# its corresponding latent-space representations
indexes = list(range(0, trainX.shape[0]))
data = {'indexes':indexes, 'features':features}

# Write the data dictionary to disk
print('[INFO] Saving index...')
f = open(args['index'], 'wb')
f.write(pickle.dumps(data))
f.close()