#@ String image_path
#@ String image_id
#@ String path_duplicated
#@ String path_split
open(image_path);
run("Duplicate...", "title=image_" + image_id + ".tif duplicate");
//saveAs("Tiff", path_duplicated + "image_" + image_id + ".tif");

selectImage("image_" + image_id + ".tif");
run("Split Channels");
selectImage("C1-image_" + image_id + ".tif");
run("Green");
saveAs("Tiff", path_split + "image_" + image_id + "_gfap.tif");
selectImage("C2-image_"+ image_id + ".tif");
run("Magenta");
saveAs("Tiff", path_split + "image_" + image_id + "_dapi.tif");
run("Close All");