"""
AstroNeuDL
__init__
Written by Beatriz Fernandes
22nd January
"""

from AstroNeuDL.utils import *
from AstroNeuDL.segmentation.InstanceSegmentation import InstanceSegmentation
from AstroNeuDL.preprocessing.preprocessing import Preprocessing
from AstroNeuDL.evaluation.evaluation import Evaluation2DSeg

def GetPipeLine(configs):
    if "seeds" in configs:
        if configs["seeds"] == True:
            import numpy as np
            np.random.seed(123)
            import random as python_random
            python_random.seed(123)
            import tensorflow.compat.v1 as tf
            tf.random.set_random_seed(123)
            sess = tf.Session(graph=tf.get_default_graph())
            K.set_session(sess)
    if configs["use_algorithm"] == "Preprocessing":
        pipeline = Preprocessing(**configs)
        return pipeline
    elif configs["use_algorithm"] == "Evaluation2DSeg":
        pipeline = Evaluation2DSeg(**configs)
        return pipeline
    elif configs["use_algorithm"] == "InstanceSegmentation":
        pipeline = InstanceSegmentation(**configs)
        return pipeline
    # elif configs["use_algorithm"] == "Regression":
    #     pipeline = Regression(**configs)
    #     return pipeline
    # elif configs["use_algorithm"] == "SemanticSegmentation" :
    #     pipeline = SemanticSegmentation(**configs)
    #     return pipeline
    
    else: 
        raise KeyError("The use_algorithm should be set correctly")