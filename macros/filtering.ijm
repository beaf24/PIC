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