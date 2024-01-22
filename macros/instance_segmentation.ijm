#@ String image_path
#@ String image_id
#@ String mask_path
#@ String roi_path
#@ String roi_id

open(image_path);
open(roi_path);
selectImage(image_id + ".png");
run("Create Mask");
saveAs("Tiff", mask_path + image_id + "_ind" + roi_id + ".png");
run("Close All");
