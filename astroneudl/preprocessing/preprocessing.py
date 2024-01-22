import os
import shutil
import imagej
import scyjava
from scyjava import jimport
import pandas as pd
import numpy as np
import logging

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

        self.path_split = self.path_data + "/layer 0/split channels dapi-gfap/"
        self.path_normalized = self.path_data + "/layer 1/normalized/"
        self.path_mean = self.path_data + "/layer 1/filter mean/"
        self.path_gaussian = self.path_data + "/layer 1/filter gaussian/"

        self.path_composite = self.path_data + "/layer 1/composite/"
        self.path_rgb = self.path_data + "/layer 2/images rgb/"
        self.path_maximum = self.path_data + "/layer 2/maximum projections/"
        self.path_nuclei2d = self.path_data + "/layer 2/nuclei 2d/"
        self.path_nuclei3d = self.path_data + "/layer 2/nuclei 3d/"

        self.path_results = self.path_data + "/results/"

        list_paths = [self.path_split,
                      self.path_normalized,
                      self.path_mean,
                      self.path_gaussian,
                      self.path_composite,
                      self.path_rgb,
                      self.path_maximum,
                      self.path_nuclei2d,
                      self.path_nuclei3d,
                      self.path_results]
        
        for path in list_paths:
            if not os.path.exists(path):
                os.makedirs(path)

        self.path_macros = "/Users/beatrizfernandes/Documents/GitHub/PIC/macros"

        scyjava.config.add_option('-Xmx6g')

        # ij = imagej.init('sc.fiji:fiji:2.14.0', add_legacy=False)
        # self.ij = imagej.init('sc.fiji:fiji:2.14.0', headless = False)
        self.ij = imagej.init('sc.fiji:fiji', mode='interactive')


        # try: ij
        # except NameError: ij = imagej.init('sc.fiji:fiji:2.14.0')

        # self.ij = ij

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
        """
        logging.info("Start duplicating dataset\n")
        self.prep_macros()

        dataset_list = os.listdir(self.path_data)
        image_ids = ["%03d" % i for i in range(1, len(dataset_list)+1)]

        macro_duplicate_split = open(file = self.path_macros + "/duplicate_split.ijm", mode='r').read()

        for im, image_name in enumerate(list(filter(lambda element: '.tif' in element, os.listdir(self.path_data)))):
            if image_name.split('.')[-1]=="tif":
                image_path = self.path_data + image_name
                image_id = image_ids[im]

                print(image_path)
                
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
                logging.info("{} done".format(image_id))
                self.ij.window().clear()
    
    def normalize_dataset(self):
        """
        Normalizes the dataset's histogram for 8-bit images.
        Sets the minimum value always to 0 and the maximum value to 255.
        """
        self.prep_macros()

        for image_name in np.sort(list(filter(lambda element: '.tif' in element, os.listdir(self.path_split)))):
            java_image = self.ij.io().open(self.path_split + image_name)
            py_image = self.ij.py.from_java(java_image)
            if py_image.min() != 0 or py_image.max() != 255:
                py_image = (py_image-py_image.min())/(py_image.max()-py_image.min())*255
            java_image = self.ij.py.to_java(py_image.astype(np.uint8))
            self.ij.io().save(java_image, self.path_normalized + image_name.split('.')[0] + '_normalized.tif')
    
    def filtering_dataset(self):
        """
        Applies the mean and gaussian filter to the the dataset and saves at the respective directories.
        """
        self.prep_macros()

        macro_filtering = open(file = self.path_macros + "/filtering.ijm", mode='r').read()

        for image_name in list(filter(lambda element: '.tif' in element, os.listdir(self.path_normalized))):
            image_name = '_'.join(image_name.split("_")[:3])
            print(image_name)

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
            print(self.path_split + image_name)
            self.ij.window().clear()

    def preparing_analysis(self,
                           path_input):
        """
        Creates the four datasets for image subsequent processing.
            * nuclei 2d: path_nuclei2d; maximum intensity projection of the DAPI channel for segmentation tasks.
            * nuclei 3d: path_3dnuclei; z-stack of the DAPI channel for segmentation tasks.
            * 2d composite: path_maximum; maximum intensity projection of composite images of DAPI and GFAP channels.
            * 3d composite: path_rgb; z-stack composites images of DAPI and GFAP channels.
        """
        self.prep_macros()

        macro_datasets = open(file = self.path_macros + "/datasets.ijm", mode='r').read()

        image_ids = []
        for i in os.listdir(path_input): image_ids.append(i.split("_")[1])
        image_ids = list(set(image_ids))

        for image_id in image_ids:
            files = list(filter(lambda element: image_id in element, os.listdir(path_input)))
            print(files)
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
            print(image_id + ' done')
            self.ij.window().clear()
    
    def get_statistics(self, 
                       path_input):
        """
        Detemine the histograms and mean value of each slice for each image of a dataset.
        Saves the results at _hist and _meanslices .csv's at ptah_results.

        PARAMETERS:
            path_input: the directory of the dataset to be analysed.
        """
        self.prep_macros()

        macro_results = open(file = self.path_macros + "/results.ijm", mode='r').read()

        for image_name in list(filter(lambda element: '.tif' in element, os.listdir(path_input))):
            image_name = image_name.split(".")[0]
            print(image_name)

            args ={
                'image_name': image_name,
                'path_input': path_input,
                'path_results': self.path_results
            }
            self.ij.py.run_macro(macro_results, args)
            print(self.path_split + image_name)
            self.ij.window().clear()

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

        PARAMETERS:
            path_input: directory of the dataset to be converted.
            path_roi2d: directory of fiji zip files containing the ROIs of the segemneted images.
            path_output: the path to output the dataset. If doesn't exist, is created.      
        """
        self.prep_macros()

        if path_input == None: path_input = self.path_nuclei3d

        if not os.path.exists(path_output):
            os.makedirs(path_output)

        macro_instance_segmentation = open(file = self.path_macros + "/instance_segmentation.ijm", mode='r').read()

        for image_id in list(filter(lambda element: 'image' in element, os.listdir(path_input))):
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
                print(path_roi2d + image_id.split('-')[0]+ "_RoiSet/" + roi_name)
                self.ij.py.run_macro(macro_instance_segmentation, args)
                self.ij.window().clear()
            print(image_id + ' done')

    def group_rois3d(self, 
                     path_roi3d,
                     path_nuclei3d = None):
        """
        Groups each observation rois into the same folder.
        """
        
        if path_nuclei3d == None: path_nuclei3d = self.path_nuclei3d

        for rois3d in list(filter(lambda element: '.zip' not in element and 'image' in element, os.listdir(path_roi3d))):
            image_id = rois3d[:-7]
            rois = list(filter(lambda element: 'cell' in element, os.listdir(path_roi3d + rois3d)))
            print(path_roi3d + rois3d)
            print(image_id)
            cell_ids = []
            args = {'file': path_nuclei3d + image_id,
                    'image_id': image_id}
            for i in rois: 
                cell_ids.append(i.split('_')[1])
            cell_ids = list(set(cell_ids))
            print(cell_ids)
            for cell_id in cell_ids:
                if not os.path.exists(path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id)-1)):
                    os.mkdir(path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id)-1))
                for roi in list(filter(lambda element: cell_id in element, os.listdir(path_roi3d + rois3d))):
                    shutil.move(path_roi3d + rois3d + '/' + roi, path_roi3d + rois3d + '/' + image_id + '_ind' + str(int(cell_id)-1))

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

        self.group_rois3d(path_roi3d=path_roi3d)

        if not os.path.exists(path_output):
            os.makedirs(path_output)
        
        macro_make_stack = open(file = self.path_macros + "/make_stack.ijm", mode='r').read()
        macro_make_mask = open(file = self.path_macros + "/make_mask.ijm", mode='r').read()

        if path_input == None: path_input = self.path_nuclei3d

        for rois3d in list(filter(lambda element: '.zip' not in element and 'image' in element, os.listdir(path_roi3d))):
            image_id = rois3d[:-7]
            f_image_path = path_output + image_id + "/image/"
            if not os.path.exists(f_image_path):
                os.makedirs(f_image_path)
            image_path = f_image_path + image_id + '.tif'

            image = self.ij.io().open(image_path)
            dump_info = self.dump_info(image)
            shutil.copyfile(path_input + image_id + '.tif', image_path)
            # mask folder
            mask_path = path_output + image_id + "/mask/"
            if not os.path.exists(mask_path):
                os.makedirs(mask_path)

            for mask_id in list(filter(lambda element: 'image' in element, os.listdir(path_roi3d + rois3d))):
                args = {
                        'path': mask_path,
                        'mask_id': mask_id,
                        'width': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'X')[0][0]],
                        'height': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'Y')[0][0]],
                        'depth': dump_info['shape'][np.where(np.array(dump_info['dims']) == 'Z')[0][0]]
                        }
                self.ij.py.run_macro(macro_make_stack, args)
                for roi in list(filter(lambda element: '.roi' in element, os.listdir(path_roi3d + rois3d + '/' + mask_id))):
                    print(roi)
                    slice = int(roi.split('_')[2].split('.')[0])
                    # print(path_roi3d + rois3d + '/' + mask_id + '/' + roi)
                    args = {
                        'rois_path': path_roi3d + rois3d + '/' + mask_id + '/',
                        'roi_id': roi.split('.')[0],
                        'path_mask': mask_path,
                        'mask_id': mask_id,
                        'slice': slice,
                        }
                    self.ij.py.run_macro(macro_make_mask, args)
                self.ij.py.run_macro("""run("Close All")""")

    def run(self):
        """
        Runs the preprocessing pipeline
        """
        if "duplicate" in self.preprocessing_steps:
            if self.preprocessing_steps["duplicate"] == True:
                logging.info("Starting dataset duplication.")
                self.duplicate_dataset()

        if "normalizing" in self.preprocessing_steps:
            if self.preprocessing_steps["normalizing"] == True:
                logging.info("Starting dataset normalization.")
                self.normalize_dataset()

        if "filtering" in self.preprocessing_steps:
            if self.preprocessing_steps["filtering"] == True:
                logging.info("Starting dataset filtration.")
                self.normalize_dataset()

        if "prepare_analysis" in self.preprocessing_steps:
            if self.preprocessing_steps["prepare_analysis"] == "mean" or self.preprocessing_steps["prepare_analysis"] == True:
                logging.info("Starting to prepare the secondary datasets for analysis.\nDataset:{}".format(self.path_mean))
                self.preparing_analysis(self.path_mean)
            if self.preprocessing_steps["prepare_analysis"] == "gaussian":
                logging.info("Starting to prepare the secondary datasets for analysis.\nDataset:{}".format(self.path_gaussian))
                self.preparing_analysis(self.path_gaussian)
        
        if self.dataset_2d_segmentation is not None:
            logging.info("Starting to prepare the dataset for the 2D instance segmentation analysis.")
            self.iseg_2d_structure(path_input=self.dataset_2d_segmentation["input"],
                                   path_output=self.dataset_2d_segmentation["output"],
                                   path_roi2d=self.dataset_2d_segmentation["rois"])
        
        if self.dataset_3d_segmentation is not None:
            logging.info("Starting to prepare the dataset for the 3D instance segmentation analysis.")
            self.iseg_3d_structure(path_input=self.dataset_3d_segmentation["input"],
                                   path_output=self.dataset_3d_segmentation["output"],
                                   path_roi3d=self.dataset_3d_segmentation["rois"])
        
        if self.statistics is not False:
            logging.info("Retrieving and saving statistics.")
            self.get_statistics(self.statistics)
        
        logging.info("Finished preprocessing!")

