#@ String rois_path
#@ String roi_id
#@ String path_mask
#@ String mask_id
#@ Integer slice

print(rois_path + roi_id + ".roi")
open(path_mask + mask_id + ".tif");
open(rois_path + roi_id + ".roi");
selectImage(mask_id + ".tif");
run("Create Mask");
rename("Mask");
selectImage(mask_id + ".tif");
setSlice(slice);
run("Add Image...", "image=Mask x=0 y=0 opacity=100");
selectImage(mask_id + ".tif");
saveAs("Tiff", path_mask + mask_id + ".tif");
run("Close All");