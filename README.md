# 2nd Cycle Integrated Project
## High-throughput _in silico_ characterization of 3D astrocyte-neuron cell cultures.

The present repository encompasses the pipeline exerpt developed during the 2nd Cycle Integrated Project. The code was elaborated to meet the needs of image preprocessing, segmentation and evaluation of a dataset containing 21 images of astrocyte cultures obtained from murine-derived gray matter from P5-6 pos-natal mice.

The work here presented was developed between September 2023 and January 2024.

## Preprocessing

The images underwent preprocessing in Fiji via an automated algorithm designed to diminish background noise and fine-tune contrast levels. This preprocessing pipeline was scripted in Python, using version 2.14.0 of the Fiji python package, pyimagej (Rueden et al., 2022).

The preprocessing consists of:
  1. Splitting GFAP and DAPI channels
  2. Normalizing the histograms to a 8-bit scale
  3. Apply filtering (mean and gaussian)
  4. Generate datasets for learning tasks

<center>
  <img width="524" alt="image" src="https://github.com/beaf24/PIC/assets/85555689/1c2e8be8-f885-4e49-9f4c-fe84a345db53">
<\center>

### Configurations:

* `use_algorithm`: "Preprocessing"
* `data`: the path for the parent directory of the dataset
* `preprocessing_steps`: a dictionary containing these parameters
  * `duplicating`: true or false
  * `normalize`: true or false
  * `filter`: true or false
  * `prepare_analysis`: true or false
* `dataset_2d_segmentation`: a dictionary containing these parameters
  * `input`: folder of the dataset to be converted for **2D Segmentation** input format
  * `rois`: folder of the rois obtained in Fiji correspondent to the data in the input
  * `output`: folder to output the formated dataset
* `dataset_3d_segmentation`: a dictionary containing these parameters
  * `input`: folder of the dataset to be converted for **3D Segmentation** input format
  * `rois`: folder of the rois obtained in Fiji correspondent to the data in the input
  * `output`: folder to output the formated dataset
* `statistics`: false or path for the data to extract statistics

### Structure

```bash
data path
├── originals                    
│    ├── image_001
│    ├── image_002
│    │   ...
│    │   ...
│    └── image_N  
│
├── rois_nuclei2d                    
│    ├── image_001_nuclei2d_RoiSet
│    ├── image_002_nuclei2d_RoiSet
│    │   ...
│    │   ...
│    └── image_N_nuclei2d_RoiSet
│         ├── 0001_0001.roi
│         │   ...
│         │   ...
│         └── 9999_9999.roi 
│
└── rois_nuclei3d                    
     ├── image_001_nuclei3d_RoiSet
     ├── image_002_nuclei3d_RoiSet
     │   ...
     │   ...
     └── image_N_nuclei3d_RoiSet
          ├── image_N_nuclei3d_ind1
          ├── image_N_nuclei3d_ind2
          │   ...
          │   ...
          └── image_N_nuclei3d_indK
               ├── cell_K_001.roi
               │   ...
               │   ...
               └── cell_K_L.roi
```


## 2D Segmentation

The segmentation algorithm is intended to train the 2D instance segmentation of images with Mask R-CNN algorithm. The code was almost completly reused from the InstantDL pipeline.


