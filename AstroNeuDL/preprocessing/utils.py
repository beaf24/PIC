"""
AstroNeuDL
FIJI auxiliary macros for python
Written by Beatriz Fernandes
23rd January
"""

macro_duplicate_split = """
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
"""

macro_filtering = """
#@ String image_name
#@ String image_path
//#@ String path_contrast
#@ String path_mean
#@ String path_gaussian
//#@ String path_gaussian3d
#@ String color

open(image_path + image_name + "_normalized.tif")
selectImage(image_name + "_normalized.tif");
//run("Duplicate...", "title=" + image_name + "_contrast.tif duplicate");
//setSlice(32);
//if (color == "Magenta") {setMinAndMax(8, 30);} //{setMinAndMax(11, 30);}
//else {setMinAndMax(8, 65);}
run(color);
//saveAs("Tiff", path_contrast + image_name + "_contrast.tif");

//FILTER MEAN
selectImage(image_name + "_normalized.tif");
run("Duplicate...", "title=" + image_name + "_mean.tif duplicate");
run("Mean...", "radius=1 stack");
run(color);
saveAs("Tiff", path_mean + image_name + "_mean.tif");
//FILTER GAUSSIAN
selectImage(image_name + "_normalized.tif");
run("Duplicate...", "title=" + image_name + "_gaussian.tif duplicate");
run("Gaussian Blur...", "sigma=1 scaled stack");
run(color);
saveAs("Tiff", path_gaussian + image_name + "_gaussian.tif");
//FILTER GAUSSIAN 3D
//selectImage(image_name + "_normalized.tif");
//run("Duplicate...", "title=" + image_name + "_gaussian3D.tif duplicate");
//run("Gaussian Blur 3D...", "x=1 y=1 z=1");
//run(color);
//saveAs("Tiff", path_gaussian3d + image_name + "_gaussian3D.tif");
run("Close All");
"""

macro_datasets = """
#@ String images_path
#@ String image_id
#@ String name_dapi
#@ String name_gfap
#@ String path_composite
#@ String path_rgb
#@ String path_maximum
#@ String path_nuclei2d
#@ String path_nuclei3d

open(images_path + name_dapi + ".tif");
open(images_path + name_gfap + ".tif");
//MAKE COMPOSITE
run("Merge Channels...", "c2=" + name_gfap +".tif c6=" + name_dapi + ".tif create keep");
Property.set("CompositeProjection", "Sum");
//Stack.setDisplayMode("composite");
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
//run("Bio-Formats Exporter", "save=[" + path_nuclei2d + "bio" + image_id + "_nuclei2d_bio.png]");
saveAs("PNG", path_nuclei2d + image_id + "_nuclei2d.png");
run("Close All")
"""

macro_statistics = """
#@ String image_name 
#@ String path_input
#@ String path_statistics

open(path_input + image_name + ".tif");
selectImage(image_name + ".tif");
run("Histogram", "stack");
getHistogram();
saveAs("Results", path_results + image_name + "_hist.csv");
selectImage(image_name + ".tif");

//slices = Stack.getDimensions("slices");

for (i = 0; i < 64; i++) {
	Table.deleteRows(0, Table.size);
	run("Measure");
}
	
saveAs("Results", path_results + image_name + "_meanslices.csv");
"""

macro_instance_segmentation = """
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
"""

macro_make_stack = """
#@ String path
#@ String mask_id
#@ Integer width
#@ Integer height
#@ Integer depth

newImage("HyperStack", "8-bit color-mode", width, height, 1, depth, 1);
run("Hyperstack to Stack");
saveAs("Tiff", path + mask_id + ".tif");
run("Close All");
"""

macro_make_mask = """
#@ String rois_path
#@ String roi_id
#@ String path_mask
#@ String mask_id
#@ Integer slice

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
"""

## EXTRA 
macro_correction =  """
#@ String image_name
#@ String mean_min
#@ String path_corrected
#@ String m
#@ String b

open("/Users/beatrizfernandes/PIC2/data/preprocessing_auto/layer 0/split channels dapi-gfap/" + image_name + ".tif");
run("Duplicate...", "title=" + image_name + "_corrected.tif duplicate");
selectImage(image_name + "_corrected.tif");
run("Macro...", "code=v=(v/" + mean_min + ")/(" + m + "*log(z+1)+" + b + ") stack");
saveAs("Tiff", path_corrected + image_name + "_corrected.tif");

//for (i = 1; i < 65; i++) {
//	setSlice(i);
//	run("Measure");
//}

run("Close All")
"""

macro_extended_datasets = """
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
"""

macros_semantic_segmentation = """
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
"""