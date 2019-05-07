args<-commandArgs(TRUE)

require(rgeos)
require(proj4)
require(rgdal)
require(raster)
require(shapefiles)
require(dldir)
require(spsurvey)
require(DaymetR)
#setwd('E:\\USU_Research_work\\TOPNET_Web_Processing\\TOPNET_Web_services\\Test_Results\\DelineatedWatershed')
setwd(args[1])
newproj="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs +ellps=GRS80 +towgs84=0,0,0"
#rs=raster('demc1w.tif')
rs=raster(args[2])
print("testin1")

z=projectRaster(rs,crs=newproj,res=4*1000)
print(args[1])
top=rasterToPoints(z)
print("essspsruvey")
lat_lon_rg1=albersgeod(top[,1], top[,2], sph="GRS80", clon=-96, clat=23, sp1=29.5, sp2=45.5)
print("nospsruvey")

df2=data.frame(X=top[,1],Y=top[,2],ID=as.integer(seq(1,length(top[,1]),1)))
lots <- SpatialPointsDataFrame( coords = cbind(df2$X,df2$Y), data = df2) 
writeOGR( lots, dsn = 'Rain_Gauge', layer="Rain_Gauge",driver='ESRI Shapefile',overwrite=TRUE) 


len=(nrow(lat_lon_rg1))
for(i in 1:len){
  cat("filename",i, file="latlon.csv", sep="",append=TRUE)
  cat(",", file="latlon.csv", append=TRUE)
  cat(lat_lon_rg1[i,2], lat_lon_rg1[i,1], file="latlon.csv", sep=" ,",append=TRUE)
  cat(",", file="latlon.csv", append=TRUE)
  #cat("ignore stuff",i, file="latlon.txt", sep=",",append=TRUE)
  cat("\n", file="latlon.csv", append=TRUE)
}

batch.download.daymet(file_location='latlon.csv',start_yr=as.numeric(args[3]),end_yr=as.numeric(args[4]),internal=TRUE)
