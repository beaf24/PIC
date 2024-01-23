"""
AstroNeuDL
Utils for AstroNeuDL
Written by Beatriz Fernandes
22nd January
"""

import sys
import logging
import argparse
import os
import json
from AstroNeuDL.data_generator.data_generator import *
# from AstroNeuDL.data_generator.auto_evaluation_classification import classification_evaluation
# from AstroNeuDL.data_generator.auto_evaluation_segmentation_regression import segmentation_regression_evaluation
# from AstroNeuDL.segmentation.UNet_models import UNetBuilder
from keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping
import time
import tensorflow as tf
tf.get_logger().setLevel('WARNING')
from keras import backend as K
from keras.applications.resnet50 import ResNet50
# from AstroNeuDL.classification.ResNet50 import ResNet50
from AstroNeuDL.segmentation.RCNNSettings import RCNNInferenceConfig, train, detect
import AstroNeuDL.segmentation.RCNNmodel as RCNNmodel
from AstroNeuDL.segmentation.RCNNSettings import RCNNConfig
tf.compat.v1.config.experimental.list_physical_devices('GPU')
# from AstroNeuDL.classification.ResNet50 import ResNet50 #, get_imagenet_weights
import glob
from keras.optimizers import Adam, SGD
from AstroNeuDL.data_generator.data import write_logbook
logging.basicConfig(level=logging.INFO)
from AstroNeuDL.data_generator.metrics4losses import *

def load_json(file_path):
    with open(file_path, 'r') as stream:
        return json.load(stream)
