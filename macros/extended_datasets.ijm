#@ String images_path
#@ String image_id
#@ String name_dapi
#@ String name_gfap
#@ String path_composite
#@ String path_rgb
#@ String path_maximum
#@ String path_nuclei2d + 'extended/'
#@ String path_nuclei3d

open(images_path + name_dapi + ".tif");
open(images_path + name_gfap + ".tif");
//MAKE COMPOSITE
run("Merge Channels...", "c2=" + name_gfap +".tif c6=" + name_dapi + ".tif create keep");
Property.set("CompositeProjection", "Sum");
Stack.setDisplayMode("composite");
saveAs("Tiff", path_composite + image_id + "_composite.tif");

//RGB STACK...
selectImage(image_id + "_composite.tif")
run("Duplicate...", "title=" + image_id + "_composite.tif duplicate");
run("Stack to RGB", "slices keep");
saveAs("Tiff", path_rgb + image_id + "_rgb.tif");

//MAXIMUM INTENSITY
selectImage(image_id + "_rgb.tif")
run("Z Project...", "projection=[Max Intensity]");
saveAs("Tiff", path_maximum + image_id + "_rgb_MAX.tif");

//Adjust composite
selectImage(image_id + "_composite.tif")
Property.set("CompositeProjection", "null");
Stack.setDisplayMode("color");
run("Save");

//NUCLEI
selectImage(image_id + "_composite.tif")
run("Split Channels");
saveAs("Tiff", path_nuclei3d + image_id + "_nuclei3d.tif");
selectImage(image_id + "_nuclei3d.tif");
run("Z Project...", "projection=[Max Intensity]");
saveAs("PNG", path_nuclei2d + image_id + "_nuclei2d-0.png");
//Change contrast
selectImage(image_id + "_nuclei2d-0.png");
run("Duplicate...", " ");
setMinAndMax(0, 130);
saveAs("PNG", path_nuclei2d + image_id + "_nuclei2d-1.png");
//Change contrast
selectImage(image_id + "_nuclei2d-0.png");
run("Duplicate...", " ");
setMinAndMax(0, 20);
saveAs("PNG", path_nuclei2d + image_id + "_nuclei2d-2.png");


run("Close All")