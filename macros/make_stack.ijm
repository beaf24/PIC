#@ String path
#@ String mask_id
#@ Integer width
#@ Integer height
#@ Integer depth

newImage("HyperStack", "8-bit color-mode", width, height, 1, depth, 1);
run("Hyperstack to Stack");
saveAs("Tiff", path + mask_id + ".tif");
run("Close All");