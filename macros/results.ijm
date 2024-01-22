#@ String image_name 
#@ String path_input
#@ String path_results

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