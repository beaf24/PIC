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