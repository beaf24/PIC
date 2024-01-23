"""
AstroNeuDL
Data Evalautaion
Written by Beatriz Fernandes
22nd January
"""

import os
import argparse
import logging
import json
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy.spatial.distance import pdist
from sklearn.metrics import jaccard_score


def load_json(file_path):
    with open(file_path, 'r') as stream:
        return json.load(stream)

class Evaluation2DSeg(object):

    def __init__(self,
                 use_algorithm,
                 data, 
                 divisions = 128):
        
        self.path_data = data
        self.divisions = divisions

        self.path_results = self.path_data + 'results/'
        self.path_metrics = self.path_data + 'metrics/'

        list_paths = [self.path_results,
                      self.path_metrics]
        for path in list_paths:
            if not os.path.exists(path):
                os.makedirs(path)

        self.divisions = divisions

        self.model = data.split("/")[-1]

    
    def compare(self, 
                prediction, 
                mask, 
                divisions):
        size = 1024//divisions
        n_preds, n_masks = prediction.shape[2], mask.shape[2]
        pred_dict = dict()
        msk_dict = dict()

        for p in np.arange(n_preds):
            pred_p = prediction[:,:,p].reshape(-1,size,size)
            for k in [i for i, n in enumerate(list(np.sign(pred_p.sum(axis=(1,2))))) if n == True]:
                if k in pred_dict.keys():
                    pred_dict[k].append(p)
                else:
                    pred_dict[k] = list([p])
        
        for m in np.arange(n_masks):
            msk_m = mask[:,:,m].reshape(-1,size,size)
            for k in [i for i, n in enumerate(list(np.sign(msk_m.sum(axis=(1,2))))) if n == True]:
                if k in msk_dict.keys():
                    msk_dict[k].append(m)
                else:
                    msk_dict[k] = list([m])

        combinations = list()
        combinations.append([(x,y) for key in np.intersect1d(list(msk_dict.keys()),list(pred_dict.keys())) for x in pred_dict[key] for y in msk_dict[key] ])

        return set(combinations[0])

    def run(self):
        logging.info("Starting to evaluate.\nModel: {}".format(self.path_data))
        n_pred, n_msk = [], []

        for id in list(filter(lambda element: '.npy' in element, os.listdir(self.path_results))):
            i,t = 1,0
            id = id.split('.')[0]
            pred = np.load(self.path_results + id + '.npy')
            msk_path = self.path_data + 'test/' + id + '/mask/'
            msk = np.zeros((pred.shape[0], pred.shape[1], len(os.listdir(msk_path))))
            for m, name in enumerate(os.listdir(msk_path)):
                msk[:, :, m] = np.sign(plt.imread(msk_path + name))

            logging.info("id {} - mask shape: {} - pred shape: {}\n".format(id, msk.shape, pred.shape))

            n_preds, n_masks = pred.shape[2], msk.shape[2]
            iou_global = np.zeros((n_preds, n_masks))

            combinations = self.compare(prediction=pred, mask=msk, divisions=self.divisions)

            logging.info("Starting the comparison of {} ROIs\n".format(len(combinations)))
            # setup toolbar
            toolbar_width = 50
            logging.info("Progress | [%s]" % (" " * toolbar_width))
            logging.getLogger()[0].flush()
            logging.info("\b" * (toolbar_width+1)) # return to start of line, after '['

            for (p,m) in combinations:
                mask = msk[:,:,m]
                prediction = pred[:,:,p]
                iou_global[p,m] = jaccard_score(mask.flatten(), prediction.flatten(), average = None)[1]            
                if (i+1)* 50//len(combinations) != t:
                    t+=1
                    logging.info("=")
                    logging.getLogger()[0].flush()
                i +=1
            
            pd.DataFrame(iou_global).to_csv("{}iou_test_{}.csv".format(self.path_metrics,id))
            n_pred.append(pred.shape[2])
            n_msk.append(msk.shape[2])
            logging.info("]\n")

        ratio = list(np.array(n_pred)/np.array(n_msk))

        image_ids= list(filter(lambda element: '.npy' in element, os.listdir(self.path_results)))
        metrics = pd.DataFrame(np.array([list([im.split('.')[0] for im in image_ids]), n_pred, n_msk, ratio]).T, columns=['Index', 'Pred', '# Masks', 'Ratio'])
        metrics.to_csv("{}counts.csv".format(self.path_metrics))