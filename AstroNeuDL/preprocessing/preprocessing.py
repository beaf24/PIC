"""
AstroNeuDL
Preprocessing pipeline
Written by Beatriz Fernandes
23rd January
"""

import os
import shutil
import imagej
import scyjava
from scyjava import jimport
import pandas as pd
import numpy as np
import logging
from alive_progress import alive_bar
from sklearn.model_selection import KFold
import shutil

from AstroNeuDL.preprocessing.utils import macro_duplicate_split, macro_filtering, macro_datasets, \
                                            macro_instance_segmentation, macro_make_mask, macro_make_stack, macro_statistics


class Preprocessing(object):

    def __init__(self,
                 use_algorithm,
                 data,
                 preprocessing_steps = dict(),
                 dataset_2d_segmentation = None,
                 dataset_3d_segmentation = None,
                 statistics = False) -> None:
        
        self.path_data = data
        self.preprocessing_steps = preprocessing_steps

        self.dataset_2d_segmentation = dataset_2d_segmentation
        self.dataset_3d_segmentation = dataset_3d_segmentation
        self.statistics = statistics

        self.path_originals = self.path_data + '/originals/'
        if not os.listdir(): logging.info("ATTENTION! NO DATA FOUND")

        self.path_split = self.path_data + "/layer 0/split channels dapi-gfap/"
        self.path_normalized = self.path_data + "/layer 1/normalized/"
        self.path_mean = self.path_data + "/layer 1/filter mean/"
        self.path_gaussian = self.path_data + "/layer 1/filter gaussian/"

        self.path_composite = self.path_data + "/layer 1/composite/"
        self.path_rgb = self.path_data + "/layer 2/composite 3d/"
        self.path_maximum = self.path_data + "/layer 2/composite 2d/"
        self.path_nuclei2d = self.path_data + "/layer 2/nuclei 2d/"
        self.path_nuclei3d = self.path_data + "/layer 2/nuclei 3d/"

        self.path_statistics = self.path_data + "/statistics/"

        self.path_macros = "/Users/beatrizfernandes/Documents/GitHub/PIC/macros"

        scyjava.config.add_option('-Xmx6g')
        self.ij = imagej.init('sc.fiji:fiji:2.14.0', add_legacy=True)

    def make_folders(self, list_paths):
        for path in list_paths:
            if not os.path.exists(path):
                os.makedirs(path)

    def dump_info(self, image) -> dict:
        """
        A handy function to get details of an image object.
        Retuns a dict.
        """
        name = image.name if hasattr(image, 'name') else None # xarray
        if name is None and hasattr(image, 'getName'): name = image.getName() # Dataset
        if name is None and hasattr(image, 'getTitle'): name = image.getTitle() # ImagePlus

        info  = dict()
        info['name'] = name or 'N/A'
        info['type'] = type(image)
        info['dtype'] = image.dtype if hasattr(image, 'dtype') else 'N/A'
        info['shape'] = image.shape
        info['dims'] = image.dims if hasattr(image, 'dims') else 'N/A'

        return info

    def prep_macros(self):
        """
        Close all windows in ImageJ background and created a dummy image necessary for the package.
        """
        self.ij.py.run_macro('run("Close All")')
        if self.ij.WindowManager.getIDList() is None:
            self.ij.py.run_macro('newImage("dummy", "8-bit", 1, 1, 1);')

    def duplicate_dataset(self):
        """
        Duplicates the original dataset to avoid irreversible changes.

        INPUTS from:
            - duplicate_split.ijm
            - path_originals

        OUTPUTS to:
            - path_split: ./layer0/split channels dapi-gfap/
        """
        logging.info("Start duplicating dataset\n")
        self.prep_macros()

        dataset_list = os.listdir(self.path_originals)
        image_ids = ["%03d" % i for i in range(1, len(dataset_list)+1)]

        list_dir = list(filter(lambda element: '.tif' in element, os.listdir(self.path_originals)))

        with alive_bar(len(list_dir)) as bar:
            for im, image_name in enumerate(list(list_dir)):
                if image_name.split('.')[-1]=="tif":
                    image_path = self.path_originals + image_name
                    image_id = image_ids[im]
                    
                    # image = ij.io().open(image_path)
                    # image_plus = ij.py.to_imageplus(image)
                    # image_plus.setTitle("image_" + image_id)
                    # image_plus.show()
                    args = {
                        'image_path': image_path,
                        'image_id': image_id,
                        'path_split': self.path_split
                    }
                    self.ij.py.run_macro(macro_duplicate_split, args)
                    self.ij.window().clear()
                    bar()
    
    def normalize_dataset(self):
        """
        Normalizes the dataset's histogram for 8-bit images.
        Sets the minimum value always to 0 and the maximum value to 255.

        INPUTS from:
            - path_split: ./layer 0/split channels dapi-gfap/

        OUTPUTS to:
            - path_normalized: ./layer 1/normalized/
        """
        self.prep_macros()

        list_dir = list(filter(lambda element: '.tif' in element, os.listdir(self.path_split)))

        with alive_bar(len(list_dir)) as bar:
            for image_name in np.sort(list_dir):
                java_image = self.ij.io().open(self.path_split + image_name)
                py_image = self.ij.py.from_java(java_image)
                if py_image.min() != 0 or py_image.max() != 255:
                    py_image = (py_image-py_image.min())/(py_image.max()-py_image.min())*255
                java_image = self.ij.py.to_java(py_image.astype(np.uint8))
                self.ij.io().save(java_image, self.path_normalized + image_name.split('.')[0] + '_normalized.tif')
                bar()
    
    def filtering_dataset(self):
        """
        Applies the mean and gaussian filter to the the dataset and saves at the respective directories.

        INPUTS from:
            - filtering.ijm
            - path_normalized: ./layer 1/normalized/
        OUTPUTS to:
            - path_mean: ./layer 1/filter mean/
            - path_gaussian: ./layer 1/filter gaussian/
        """
        self.prep_macros()

        list_dir = list(filter(lambda element: '.tif' in element, os.listdir(self.path_normalized)))
        
        with alive_bar(len(list_dir)) as bar:
            for image_name in list_dir:
                image_name = '_'.join(image_name.split("_")[:3])
                if image_name.split('_')[2] == 'dapi':
                    color = 'Magenta'
                else: 
                    color = 'Green'

                args ={
                    'image_name': image_name,
                    'image_path': self.path_normalized,
                    'path_mean': self.path_mean,
                    'path_gaussian': self.path_gaussian,
                    'color': color
                }
                self.ij.py.run_macro(macro_filtering, args)
                self.ij.window().clear()
                bar()

    def preparing_analysis(self,
                           path_input):
        """
        Creates the four datasets for image subsequent processing.
            * nuclei 2d: path_nuclei2d; maximum intensity projection of the DAPI channel for segmentation tasks.
            * nuclei 3d: path_3dnuclei; z-stack of the DAPI channel for segmentation tasks.
            * 2d composite: path_maximum; maximum intensity projection of composite images of DAPI and GFAP channels.
            * 3d composite: path_rgb; z-stack composites images of DAPI and GFAP channels.
        
        INPUTS from:
            - datasets.ijm
            - path_input (default): ./layer 1/filter mean/
        OUTPUTS to:
            - path_composite: ./layer 1/composite/
            - path_rbg: ./layer 2/composite 3d/
            - path_maximum: ./layer 2/composite 2d/
            - path_nuclei2d: ./layer 2/nuclei 2d/
            - path_nuclei3d: ./layer 2/nuclei 3d/
        """
        self.prep_macros()

        image_ids = []
        for i in os.listdir(path_input): image_ids.append(i.split("_")[1])
        image_ids = list(set(image_ids))

        with alive_bar(len(image_ids)) as bar: 
            for image_id in image_ids:
                files = list(filter(lambda element: image_id in element, os.listdir(path_input)))
                name_dapi = list(filter(lambda element: 'dapi' in element, files))[0].split('.')[0]
                name_gfap = list(filter(lambda element: 'gfap' in element, files))[0].split('.')[0]

                args ={
                    'images_path': path_input,
                    'image_id': 'image_' + image_id,
                    'name_dapi': name_dapi,
                    'name_gfap': name_gfap,
                    'path_composite': self.path_composite,
                    'path_rgb': self.path_rgb,
                    'path_maximum': self.path_maximum,
                    'path_nuclei2d': self.path_nuclei2d,
                    'path_nuclei3d': self.path_nuclei3d
                }
                self.ij.py.run_macro(macro_datasets, args)
                self.ij.window().clear()
                bar()
    
    def get_statistics(self, 
                       path_input):
        """
        Detemine the histograms and mean value of each slice for each image of a dataset.
        Saves the results at _hist and _meanslices .csv's at path_statistics.

        INPUTS from:
            - statistics.ijm
            - path_input: the directory of the dataset to be analysed.
        
        OUTPUTS to:
            - path_statistics: ./statistics/
        """
        self.prep_macros()

        list_dir = list(filter(lambda element: '.tif' in element, os.listdir(path_input)))
        
        with alive_bar(len(list_dir)) as bar:
            for image_name in list_dir:
                image_name = image_name.split(".")[0]
                args = {
                        'image_name': image_name,
                        'path_input': path_input,
                        'path_statistics': self.path_statistics
                        }
                self.ij.py.run_macro(macro_statistics, args)
                self.ij.window().clear()
                bar()

    def iseg_2d_structure(self, 
                          path_input, 
                          path_output, 
                          path_roi2d):
        """
        Creates a folder with the data input structure prepared for InstantDL analysis of 2D instance segmentation.

            path
            ├── train                    
            │   ├── image
            │   │    ├── 000003-num1.png
            │   │    ├── 000004-num9.png
            │   │    ├── 000006-num1.png
            │   │    ├── ...
            │   │    ├── ...
            │   │    ├── ...
            │   │    └── 059994-num1.png     
            │   └── groundtruth  
            │        └── groundtruth.csv
            │
            └── test                    
            ├── image
            │    ├── 000002-num1.png
            │    ├── 000005-num1.png
            │    ├── 000007-num9.png
            │    ├── ...
            │    ├── ...
            │    ├── ...
            │    └── 009994-num1.png     
            └── groundtruth  
                    └── groundtruth.csv

        INPUTS from:
            - instance_segmentation.ijm
            - path_input: directory of the dataset to be converted.
            - path_roi2d: directory of fiji zip files containing the ROIs of the segmented images.

        OUTPUTS to:
            - path_output: the path to output the dataset. If doesn't exist, is created.      
        """
        self.prep_macros()

        if path_input == None: path_input = self.path_nuclei3d

        if not os.path.exists(path_output):
            os.makedirs(path_output)

        list_dir = list(filter(lambda element: 'image' in element, os.listdir(path_input)))

        with alive_bar(len(list_dir)) as bar:
            for image_id in list_dir:
                # image folder
                f_image_path = path_output + image_id.split('.')[0] + "/image/"
                if not os.path.exists(f_image_path):
                    os.makedirs(f_image_path)
                image_path = f_image_path + image_id
                shutil.copyfile(path_input + image_id, image_path)
                # mask folder
                mask_path = path_output + image_id.split('.')[0] + "/mask/"
                if not os.path.exists(mask_path):
                    os.makedirs(mask_path)
                for roi_id, roi_name in enumerate(os.listdir(path_roi2d + image_id.split('.')[0] + "_RoiSet/")):  #.split('-')[0]
                    args = {
                        'image_path': image_path,
                        'image_id': image_id.split('.')[0],
                        'mask_path': mask_path,
                        'roi_path': path_roi2d + image_id.split('.')[0]+ "_RoiSet/" + roi_name,  #.split('-')[0]
                        'roi_id': roi_id
                    }
                    self.ij.py.run_macro(macro_instance_segmentation, args)
                    self.ij.window().clear()
                bar()

    def group_rois3d(self, 
                     image_id,
                     path_nuclei3d,
                     path_roi3d,
                     rois3d):
        """
        Groups each observation rois into the same folder.
        """

        rois = list(filter(lambda element: 'cell' in element and '.roi' in element, os.listdir(path_roi3d + rois3d)))
        cell_ids = []
        args = {'file': path_nuclei3d + image_id,
                'image_id': image_id}
        for i in rois: 
            cell_ids.append(i.split('_')[1])
        cell_ids = list(set(cell_ids))
        for cell_id in cell_ids:
            if not os.path.exists(path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id))):
                os.mkdir(path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id)))
            for roi in list(filter(lambda element: cell_id in element and '.roi' in element, os.listdir(path_roi3d + rois3d))):
                shutil.move(path_roi3d + rois3d + '/' + roi, path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id)))

    def iseg_3d_structure(self,
                          path_input = None,
                          path_output = None,
                          path_roi3d = None):
        """
        Creates a folder with the data input structure prepared for InstantDL analysis of 2D instance segmentation.

        PARAMETERS:
            path_input: directory of the dataset to be converted.
            path_roi2d: directory of fiji zip files containing the ROIs of the segemneted images.
            path_output: the path to output the dataset. If doesn't exist, is created.      
        """
        if path_input == None: path_input = self.path_nuclei3d
        if not os.path.exists(path_output):
            os.makedirs(path_output)

        
        for rois3d in list(filter(lambda element: '.zip' not in element and 'image' in element, os.listdir(path_roi3d))):
            image_id = rois3d[:-7]
            logging.info("Processing image: {}".format(image_id))
            f_image_path = path_output + image_id + "/image/"
            if not os.path.exists(f_image_path):
                os.makedirs(f_image_path)
            image_path = f_image_path + image_id + '.tif'
            # print("This: {}".format(path_input + image_id + '.tif'))
            # print("That: {}".format(image_path))
            shutil.copyfile(path_input + image_id + '.tif', image_path)
        
            self.group_rois3d(image_id, path_input, path_roi3d, rois3d)

            image_id = rois3d[:-7]
            f_image_path = path_output + image_id + "/image/"
            image_path = f_image_path + image_id + '.tif'

            image = self.ij.io().open(image_path)
            dump_info = self.dump_info(image)
            
            # mask folder
            mask_path = path_output + image_id + "/mask/"
            if not os.path.exists(mask_path):
                os.makedirs(mask_path)

            list_dir = list(filter(lambda element: 'image' in element, os.listdir(path_roi3d + rois3d)))
            with alive_bar(len(list_dir)) as bar:
                for mask_id in list_dir:
                    args = {
                            'path': mask_path,
                            'mask_id': mask_id,
                            'width': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'X')[0][0]],
                            'height': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'Y')[0][0]],
                            'depth': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'Z')[0][0]]
                            }
                    self.ij.py.run_macro(macro_make_stack, args)
                    for roi in list(filter(lambda element: '.roi' in element, os.listdir(path_roi3d + rois3d + '/' + mask_id))):
                        slice = int(roi.split('_')[2].split('.')[0])
                        args = {
                            'rois_path': path_roi3d + rois3d + '/' + mask_id + '/',
                            'roi_id': roi.split('.')[0],
                            'path_mask': mask_path,
                            'mask_id': mask_id,
                            'slice': slice,
                            }
                        self.ij.py.run_macro(macro_make_mask, args)
                    self.ij.py.run_macro("""run("Close All")""")
                    bar()

    def training_testing(self, k_fold, path_masks, path_output , dataset_name):
        images = sorted(list(filter(lambda element: '.DS_Store' not in element, os.listdir(path_masks))))
        kf = KFold(n_splits=k_fold, shuffle=True, random_state=0)
        
        with alive_bar(k_fold) as bar:
            for k, (train_index, test_index) in enumerate(kf.split(images)):
                new_path = path_output + dataset_name + 'k' + str(k_fold) + '_' + str(k+1)
                if not os.path.exists(new_path): os.makedirs(new_path)
                train_path = new_path + '/train/'
                if not os.path.exists(train_path): os.makedirs(train_path)
                test_path = new_path + '/test/'
                if not os.path.exists(test_path): os.makedirs(test_path)

                for tr in train_index:
                    obs_path = images[tr]
                    shutil.copytree(path_masks + obs_path, train_path + obs_path)
                
                for ts in test_index:
                    obs_path = images[ts]
                    shutil.copytree(path_masks + obs_path, test_path + obs_path)
                bar()

    def run(self):
        """
        Runs the preprocessing pipeline
        """
        if "duplicate" in self.preprocessing_steps:
            if self.preprocessing_steps["duplicate"] == True:
                logging.info("Starting dataset duplication.\nFetching data...")
                if not os.listdir(self.path_originals): logging.info("NO DATA FOUND: {}".format(self.path_originals))
                else: 
                    logging.info("Data fetched from: {}".format(self.path_originals))
                    self.make_folders([self.path_split])
                    logging.info("Output folder: {}".format(self.path_split))
                    self.duplicate_dataset()

        if "normalize" in self.preprocessing_steps:
            if self.preprocessing_steps["normalize"] == True:
                logging.info("Starting dataset normalization.")
                if not os.listdir(self.path_split): logging.info("NO DATA FOUND: {}".format(self.path_split))
                else: 
                    logging.info("Data fetched from: {}".format(self.path_split))
                    self.make_folders([self.path_normalized])
                    logging.info("Output folder: {}".format(self.path_normalized))
                    self.normalize_dataset()

        if "filter" in self.preprocessing_steps:
            if self.preprocessing_steps["filter"] == True:
                logging.info("Starting dataset filtration.")
                if not os.listdir(self.path_normalized): logging.info("NO DATA FOUND: {}".format(self.path_normalized))
                else: 
                    logging.info("Data fetched from: {}".format(self.path_normalized))
                    self.make_folders([self.path_mean, self.path_gaussian])
                    logging.info("Output folders: {}, and {}".format(self.path_mean, self.path_gaussian))
                    self.filtering_dataset()

        if "prepare_analysis" in self.preprocessing_steps:
            if self.preprocessing_steps["prepare_analysis"] == "mean" or self.preprocessing_steps["prepare_analysis"] == True:
                logging.info("Starting to prepare the secondary datasets for analysis.")
                if not os.listdir(self.path_mean): logging.info("NO DATA FOUND: {}".format(self.path_mean))
                else: 
                    logging.info("Data fetched from: {}".format(self.path_mean))
                    self.make_folders([self.path_composite, self.path_rgb, self.path_maximum, self.path_nuclei2d, self.path_nuclei3d])
                    logging.info("Output folders created.")
                    self.preparing_analysis(self.path_mean)
            if self.preprocessing_steps["prepare_analysis"] == "gaussian":
                logging.info("Starting to prepare the secondary datasets for analysis.")
                if not os.listdir(self.path_gaussian): logging.info("NO DATA FOUND: {}".format(self.path_gaussian))
                else: 
                    logging.info("Data fetched from: {}".format(self.path_gaussian))
                    self.make_folders([self.path_composite, self.path_rgb, self.path_maximum, self.path_nuclei2d, self.path_nuclei3d])
                    logging.info("Output folders created.")
                    self.preparing_analysis(self.path_gaussian)
        
        if self.dataset_2d_segmentation is not None:
            logging.info("Starting to prepare the dataset for the 2D instance segmentation analysis.")
            if not os.listdir(self.dataset_2d_segmentation["input"]): logging.info("NO DATA FOUND: {}".format(self.dataset_2d_segmentation["input"]))
            elif not os.listdir(self.dataset_2d_segmentation["rois"]): logging.info("NO ROIS FOUND: {}".format(self.dataset_2d_segmentation["rois"]))
            else:
                logging.info("Data fetched from: {}".format(self.dataset_2d_segmentation["input"]))
                logging.info("ROIs fetched from: {}".format(self.dataset_2d_segmentation["rois"]))
                self.iseg_2d_structure(path_input=self.dataset_2d_segmentation["input"],
                                       path_output=self.dataset_2d_segmentation["output"],
                                       path_roi2d=self.dataset_2d_segmentation["rois"])
                
                if self.dataset_2d_segmentation["k_fold"] is not False: 
                    self.path_maskrcnn_datasets = self.dataset_2d_segmentation["output"] + "/Mask RCNN datasets/"
                    self.training_testing(self.dataset_2d_segmentation["k_fold"], 
                                          dataset_name=self.dataset_2d_segmentation["name"], 
                                          path_masks=self.dataset_2d_segmentation["output"], 
                                          path_output=self.path_maskrcnn_datasets)
        
        if self.dataset_3d_segmentation is not None:
            logging.info("Starting to prepare the dataset for the 3D instance segmentation analysis.")
            if not os.listdir(self.dataset_3d_segmentation["input"]): logging.info("NO DATA FOUND: {}".format(self.dataset_2d_segmentation["input"]))
            elif not os.listdir(self.dataset_3d_segmentation["rois"]): logging.info("NO ROIS FOUND: {}".format(self.dataset_2d_segmentation["rois"]))
            else:
                logging.info("Data fetched from: {}".format(self.dataset_3d_segmentation["input"]))
                logging.info("ROIs fetched from: {}".format(self.dataset_3d_segmentation["rois"]))
                self.iseg_3d_structure(path_input=self.dataset_3d_segmentation["input"],
                                       path_output=self.dataset_3d_segmentation["output"],
                                       path_roi3d=self.dataset_3d_segmentation["rois"])
                
                if self.dataset_3d_segmentation["k_fold"] is not False: 
                    self.path_stardist3d_datasets = self.dataset_3d_segmentation["output"] + "/Stardist 3D datasets/"
                    self.training_testing(self.dataset_3d_segmentation["k_fold"], 
                                          dataset_name=self.dataset_3d_segmentation["name"], 
                                          path_masks=self.dataset_3d_segmentation["output"], 
                                          path_output=self.path_stardist3d_datasets)

        if self.statistics is not False:
            if not os.listdir(self.statistics): logging.info("NO DATA FOUND: {}".format(self.statistics))
            else:
                logging.info("Data fetched from: {}\nRetrieving and saving statistics.".format(self.statistics))
                self.get_statistics(self.statistics)
        
        logging.info("Finished preprocessing!")

