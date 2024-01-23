'''
AstroNeuDL
Written by Beatriz Fernandes
22nd January
'''

import os
import argparse
from AstroNeuDL.utils import load_json
from AstroNeuDL.data_generator.metrics4losses import *
from AstroNeuDL import GetPipeLine
import logging
from keras import backend as K

def start_learning(configs):
    logging.info("Start learning")
    logging.info(configs["use_algorithm"])

    pipeline = GetPipeLine(configs)

    pipeline.run()
    K.clear_session()


if __name__ == "__main__":

    parser = argparse.ArgumentParser( \
                            description='Starting the in silico characterization pipeline')
    parser.add_argument('-c',\
                        '--config', \
                        default="config.json", \
                        help='config json file address', \
                        type=str)

    args = vars(parser.parse_args())

    configs = load_json(args['config'])

    for k in configs:
        logging.info("%s : %s \n" % (k,configs[k]))

   
    '''
    Sanity checks in order to ensure all settings in config
    have been set so the programm is able to run
    '''
    assert configs["use_algorithm"] in ['Preprocessing',
                                        'Evaluation2DSeg',
                                        'InstanceSegmentation']

    if "batchsize" in configs:
        if not isinstance(configs["batchsize"], int):
            logging.warning("Batchsize has not been set. Setting batchsize = 2")
            batchsize = 2
    # else:
    #     logging.warning("Batchsize has not been set. Setting batchsize = 2")
    #     configs["batchsize"] = 2

    if "iterations_over_dataset" in configs:
        if not isinstance(configs["iterations_over_dataset"], int):
            logging.warning("Epochs has not been set. Setting epochs = 500 and using early stopping")
            iterations_over_dataset = 1

    if "pretrained_weights" in configs:
        if not isinstance(configs["pretrained_weights"], str):
            if not os.path.isfile((configs["pretrained_weights"])):
                configs["pretrained_weights"] = None
    # else:
    #     configs["pretrained_weights"] = None

    if "loss_function" in configs:
        if configs["loss_function"] in ["dice_loss", "dice loss", "dice"]:
            configs["loss_function"] = dice_loss

        if configs["loss_function"] in ["tversky_loss", "tversky loss", "tversky"] :
            configs["loss_function"] = tversky_loss

        if configs["loss_function"] in ["focal_loss", "focal loss", "focal"] :
            configs["loss_function"] = binary_focal_loss_fixed

        if configs["loss_function"] == "binary crossentropy dice loss":
            configs["loss_function"] = dice_crossentropy_loss

    start_learning(configs)