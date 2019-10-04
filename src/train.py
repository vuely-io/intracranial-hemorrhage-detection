import sys
import os
import numpy as np
import datetime
import tensorflow as tf
from tensorflow import keras as K
from tensorflow import ConfigProto
from tensorflow import InteractiveSession
from data_loader import DataGenerator
import data_flow
import parse_config
from model_defs import *


if parse_config.USING_RTX_20XX:
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    tf.keras.backend.set_session(tf.Session(config=config))


MODEL_NAME = sys.argv[1]
DATA_DIRECTORY = data_flow.TRAIN_DATA_PATH
TRAIN_CSV = parse_config.VALIDATE_CSV
VALIDATE_CSV = parse_config.VALIDATE_CSV
BATCH_SIZE = 16
EPOCHS = 2
TRAINING_DATA = DataGenerator(csv_filename=TRAIN_CSV, data_path=DATA_DIRECTORY, batch_size=BATCH_SIZE)
VALIDATION_DATA = DataGenerator(csv_filename=VALIDATE_CSV, data_path=DATA_DIRECTORY, batch_size=BATCH_SIZE)


# Saved models
checkpoint = K.callbacks.ModelCheckpoint(os.path.join('../models/', sys.argv[1] + '.pb'), verbose=1, save_best_only=True)
                                                       
# TensorBoard    
tb_logs = K.callbacks.TensorBoard(log_dir = os.path.join('tensorboards/', sys.argv[1]), histogram_freq=1)
# log_dir="logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


############## Model Definition goes here ##############
num_chan_in = 2
height = 512
width = 512
num_classes = 6

inputs = K.layers.Input([height, width, num_chan_in], name="DICOM")

params = dict(kernel_size=(3, 3), activation="relu",
                      padding="same",
                      kernel_initializer="he_uniform")

convA = K.layers.Conv2D(name="convAa", filters=32, **params)(inputs)
convA = K.layers.Conv2D(name="convAb", filters=32, **params)(convA)
poolA = K.layers.MaxPooling2D(name="poolA", pool_size=(2, 2))(convA)

convB = K.layers.Conv2D(name="convBa", filters=64, **params)(poolA)
convB = K.layers.Conv2D(
    name="convBb", filters=64, **params)(convB)
poolB = K.layers.MaxPooling2D(name="poolB", pool_size=(2, 2))(convB)

convC = K.layers.Conv2D(name="convCa", filters=32, **params)(poolB)
convC = K.layers.Conv2D(
    name="convCb", filters=32, **params)(convC)
poolC = K.layers.MaxPooling2D(name="poolC", pool_size=(2, 2))(convC)

flat = K.layers.Flatten()(poolC)

drop = K.layers.Dropout(0.5)(flat)

dense1 = K.layers.Dense(128, activation="relu")(drop)

dense2 = K.layers.Dense(num_classes, activation="sigmoid")(dense1)

model = K.models.Model(inputs=[inputs], outputs=[dense2])

opt = K.optimizers.Adam()

model.compile(loss=K.losses.categorical_crossentropy,
              optimizer=opt,
              metrics=[tf.keras.metrics.CategoricalCrossentropy()])

# loss = tf.nn.weighted_cross_entropy_with_logits()
# https://www.tensorflow.org/api_docs/python/tf/nn/weighted_cross_entropy_with_logits

                                                                 
model.fit_generator(TRAINING_DATA, 
                    validation_data=VALIDATION_DATA, 
                    callbacks=[checkpoint, tb_logs],
                    epochs=EPOCHS)
