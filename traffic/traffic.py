import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from tensorflow.keras import layers, models

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    dimensions = (IMG_WIDTH, IMG_HEIGHT)

    # Go through every label category in directory
    for i, dir in enumerate(os.listdir(data_dir)):

        # Go through each image in current directory
        for image_path in os.listdir(os.path.join(data_dir, dir)):
            pth = (os.path.join(data_dir, dir, image_path))

            # Convert image to numpy array
            img = cv2.imread(pth)

            # Resizing image
            resized = cv2.resize(img, dimensions)

            # Append image array to list
            images.append(resized)

            # Add to labels the category (subdirectory) this image is in
            labels.append(int(dir))
    return (images, labels)

def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # Initializing Sequential model
    # Add Layers
    # Inspired by tensorflow's own CNN tutorial https://www.tensorflow.org/tutorials/images/cnn
    model = models.Sequential([

    layers.Conv2D(
        32, (3, 3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
    ),

    layers.MaxPooling2D(pool_size=(3, 3)),

    layers.Conv2D(64, (3, 3), activation='relu'),

    layers.MaxPooling2D(pool_size=(2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),

    # Flattening 3D array into 1D
    layers.Flatten(),

    # Hidden dropout layer
    layers.Dense(NUM_CATEGORIES*32, activation='relu'),
    layers.Dropout(0.3),

    # Output layer
    layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Compiling model
    model.compile(
    optimizer='adam',
    loss="categorical_crossentropy",
    metrics=['accuracy']
    )

    return model

if __name__ == "__main__":
    main()
