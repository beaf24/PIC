import os
import shutil
import imagej
import scyjava
from scyjava import jimport
import bioformats
import pandas as pd
import numpy as np
import logging

class Preprocessing(object):


    def __init__(self,
                 path_data,
                 ) -> None:
        
        self.path_data = path_data
        self.path_split = path_data + "/layer 0/split channels dapi-gfap/"
        self.path_normalized = path_data + "/layer 1/normalized/"
        self.path_mean = path_data + "/layer 1/filter mean/"
        self.path_gaussian = path_data + "/layer 1/filter gaussian/"

        self.path_composite = path_data + "/layer 1/composite/"
        self.path_rgb = path_data + "/layer 2/images rgb/"
        self.path_maximum = path_data + "/layer 2/maximum projections/"
        self.path_nuclei2d = path_data + "/layer 2/nuclei 2d/"
        self.path_nuclei3d = path_data + "/layer 2/nuclei 3d/"

        list_paths = [self.path_split,
                      self.path_normalized,
                      self.path_mean,
                      self.path_gaussian,
                      self.path_composite,
                      self.path_rgb,
                      self.path_maximum,
                      self.path_nuclei2d,
                      self.path_nuclei3d]
        
        for path in list_paths:
            if not os.path.exists(path):
                os.makedirs(path)

        self.path_macros = "/Users/beatrizfernandes/Documents/GitHub/PIC/macros"

        try: self.ij
        except NameError: self.ij = imagej.init('sc.fiji:fiji:2.14.0')


    def prep_macros(self):
        """close all windows in ImageJ background and created a dummy image necessary for the package"""
        self.ij.py.run_macro('run("Close All")')
        if self.ij.WindowManager.getIDList() is None:
            self.ij.py.run_macro('newImage("dummy", "8-bit", 1, 1, 1);')

    def duplicate_dataset(self):
        logging.info("Start duplicating dataset\n")
        self.prep_macros()

        dataset_list = os.listdir(self.path_originals)
        image_ids = ["%03d" % i for i in range(1, len(dataset_list)+1)]

        macro_duplicate_split = open(file = self.path_macros + "/duplicate_split.ijm", mode='r').read()

        for im, image_name in enumerate(list(filter(lambda element: '.tif' in element, os.listdir(self.path_originals)))):
            if image_name.split('.')[-1]=="tif":
                image_path = self.path_originals + image_name
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
        self.prep_macros()

        for image_name in np.sort(list(filter(lambda element: '.tif' in element, os.listdir(self.path_split)))):
            java_image = self.ij.io().open(self.path_split + image_name)
            py_image = self.ij.py.from_java(java_image)
            if py_image.min() != 0 or py_image.max() != 255:
                py_image = (py_image-py_image.min())/(py_image.max()-py_image.min())*255
            java_image = self.ij.py.to_java(py_image.astype(np.uint8))
            self.ij.io().save(java_image, self.path_normalized + image_name.split('.')[0] + '_normalized.tif')
    
    def filtering_dataset(self):
        self.prep_macros()

        macro_filtering = open(file = self.path_macros + "/filtering.ijm", mode='r').read()

        for image_name in list(filter(lambda element: '.tif' in element, os.listdir(path_normalized))):
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

    def preparing_analysis(self):
        self.prep_macros()

        macro_datasets = open(file = self.path_macros + "/datasets.ijm", mode='r').read()
        layer2_source = self.path_mean

        image_ids = []
        for i in os.listdir(layer2_source): image_ids.append(i.split("_")[1])
        image_ids = list(set(image_ids))

        image_names = os.listdir(layer2_source)

        for image_id in image_ids:
            files = list(filter(lambda element: image_id in element, os.listdir(layer2_source)))
            print(files)
            name_dapi = list(filter(lambda element: 'dapi' in element, files))[0].split('.')[0]
            name_gfap = list(filter(lambda element: 'gfap' in element, files))[0].split('.')[0]

            args ={
                'images_path': layer2_source,
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
