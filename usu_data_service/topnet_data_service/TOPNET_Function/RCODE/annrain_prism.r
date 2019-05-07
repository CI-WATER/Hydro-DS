args<-commandArgs(TRUE)
library(raster)

#setwd("C:\\Users\\shams\\.qgis2\\python\\plugins\\getClimateData")

arus=raster(args[1]) # annual rainfall for whole united states downloaded from PRISM
ar_proj=projection(arus)
newproj="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs +ellps=GRS80 +towgs84=0,0,0"
#newproj= "+proj=utm +zone=18 +datum=NAD83 +units=m +no_defs +ellps=GRS80 +towgs84=0,0,0"
arus_projected=projectRaster(arus, crs=newproj)
dir=args[2]
setwd(dir)
ME=args[3]
watershed=raster(ME) # my model element
arus_tif=writeRaster(arus_projected,"arus.tif") # write raster to 
arwatershed=crop(arus_tif,watershed,"arwatershed.tif",overwrite=TRUE) # crop for the watershed area but got some pixel value out side boundary
arwat_samcell= resample(arwatershed, watershed, method='bilinear') # make same cell size as watershed
sum_ar_watrshed= overlay(arwat_samcell, watershed, fun=function(x,y){return(x+y)}) # sumof watershed and croped rainfall 
annual_rain_watershed=overlay(sum_ar_watrshed, watershed, fun=function(x,y){return(x-y)}) # subtract (sum of watershed and croped rainfall) to watershed for getting annural rainfall for watrshed
annrain_watershed=writeRaster(annual_rain_watershed,"annrain.tif",datatype='FLT4S',options="COMPRESS=NONE") ## change datatype which will change 64 bit to 32 bit

