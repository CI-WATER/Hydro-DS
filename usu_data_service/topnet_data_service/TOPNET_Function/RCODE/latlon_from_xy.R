args<-commandArgs(TRUE)
require(raster)
require(proj4)
require(spsurvey)
dir=args[1]
setwd(dir)
#setwd("E:\\USU_Research_work\\CI-WATER PROJECT\\climate_data\\climate_data")
newproj="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs +ellps=GRS80 +towgs84=0,0,0"
rs=raster(args[2])
z=projectRaster(rs,crs=newproj,res=4000)
top=rasterToPoints(z)
lat_lon_rg1=albersgeod(top[,1], top[,2], sph="GRS80", clon=-96, clat=23, sp1=29.5, sp2=45.5)
lat_lon_rg=cbind(top[,1], top[,2])

##Generatign latlonfrom xy.txt
dd=lat_lon_rg1[,c(1,2)]
df=lat_lon_rg[,1:2]
long_fit=lm(dd[,1]~df[,1])
lo_f1=long_fit$coefficients[1]
lo_f2=long_fit$coefficients[2]
lat_fit=lm(dd[,2]~df[,2])
la_f1=lat_fit$coefficients[1]
la_f2=lat_fit$coefficients[2]
sink("latlongfromxy.txt") 
cat(sprintf("This file provides the parameters for conversion from local X,Y coordinates to latitude and longitude coordinates used in the solar radiation calculations."),file='latlongfromxy.txt',append=TRUE)
cat("\n", file="latlongfromxy.txt", append=TRUE)
cat(sprintf("A linear transformation is assumed to be adequate.Equations used:latitude=(flat)*Y+(clat);longitude=(flong)*X+(clong).See the file latlongfromxy.xls for calculation of these values from rain gage x, y, lat and long coordinates"),file='latlongfromxy.txt',append=TRUE)
cat("\n", file="latlongfromxy.txt", append=TRUE)
cat(sprintf("%g %s %s", la_f2,"flat","Latitude factor"),file='latlongfromxy.txt',append=TRUE) 
cat("\n", file="latlongfromxy.txt", append=TRUE)
cat(sprintf("%1.6f %s %s", la_f1,"clat","Latitude constant"),file='latlongfromxy.txt',append=TRUE) 
cat("\n", file="latlongfromxy.txt", append=TRUE)    
cat(sprintf("%g %s %s", lo_f2,"flong ","Longitude factor"),file='latlongfromxy.txt',append=TRUE) 
cat("\n", file="latlongfromxy.txt", append=TRUE)       
cat(sprintf("%1.6f %s %s", lo_f1,"clong","Longitude constant"),file='latlongfromxy.txt',append=TRUE) 
cat("\n", file="latlongfromxy.txt", append=TRUE)       
sink()