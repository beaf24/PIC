path_data = "/Users/beatrizfernandes/PIC2/data/preprocessing_auto";
path_input = path_data + "/layer 2/nuclei 2d/"
path_roi2d = path_data + "/rois_nuclei2d/"
path_output_semantic = path_data + "/train_semantic_segmentation/"

id = "023"

image_path = path_output_semantic + "image/"
groundtruth_path = path_output_semantic + "groundtruth/"

image_id = "image_"+ id + "_nuclei2d"
roi_path = path_roi2d + image_id + "_RoiSet.zip"

open(roi_path);
roiManager("Open", roi_path); 
open(image_path + image_id + "-0.png");
roiManager("Combine");
run("Create Mask");
saveAs("Tiff", groundtruth_path + image_id + "-0.tif");
saveAs("Tiff", groundtruth_path + image_id + "-1.tif");
saveAs("Tiff", groundtruth_path + image_id + "-2.tif");
run("Close All");