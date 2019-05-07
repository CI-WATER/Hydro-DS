args<-commandArgs(TRUE)
library(raster)
lc_imag=args[1]
#uslulc=raster('nlcd2006_landcover_4-20-11_se5.img')
#watershed=raster("lrdemprjmme1.tif") # my model element
uslulc=raster(lc_imag)
#me=args[2]

#r <- raster('soilC212.tif')
setwd(args[2])
r=raster(args[3])

lulcwatershed=crop(uslulc,r,"lulcwatershed1.tif",overwrite=TRUE)
sum_lulc_watrshed1= overlay(lulcwatershed, r, fun=function(x,y){return(x+y)}) # sumof watershed and croped lulc
sum_lulc_watershed2=overlay(sum_lulc_watrshed1,r, fun=function(x,y){return(x-y)}) # subtract (sum of watershed and croped rainfall) to watershed for getting annural rainfall for watrshed
my=setExtent(sum_lulc_watershed2, r, keepres=FALSE, snap=FALSE)
lulc_intersted_area=writeRaster(my,"lulcmmef.tif",overwrite=TRUE,datatype='INT4S',options="COMPRESS=NONE") ## change datatype which will change 64 bit to 32 bit
