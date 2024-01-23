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
</center>

### Configurations:

* ```use_algorithm```: "Preprocessing"
* ```data```: the path for the parent directory of the dataset
* ```preprocessing_steps```:
  * ```duplicating```: true #false

## 2D Segmentation

The segmentation algorithm is intended to train the 2D instance segmentation of images with Mask R-CNN algorithm. The code was almost completly reused from the InstantDL pipeline.


