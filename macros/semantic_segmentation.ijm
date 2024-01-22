#@ String image_path
#@ String image_id
#@ String groundtruth_path
#@ String roi_path

open(roi_path);
roiManager("Open", roi_path); 
open(image_path + image_id);
roiManager("Combine");
run("Convert to Mask");
saveAs("Tiff", groundtruth_path + image_id);
run("Close All");