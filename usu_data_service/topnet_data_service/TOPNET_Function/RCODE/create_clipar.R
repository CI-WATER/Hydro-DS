args<-commandArgs(TRUE)
library(zoo)
library(hydroTSM)
library(rgeos)
library(proj4)
library(rgdal)
library(raster)
library(shapefiles)
require(spsurvey)

dir=args[1]
#dir='C:\\Users\\shams\\.qgis2\\python\\plugins\\getClimateData'
setwd(dir)
newproj="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs +ellps=GRS80 +towgs84=0,0,0"
#rs=raster('demA1me.tif')
rs=raster(args[4])
z=projectRaster(rs,crs=newproj,res=4000)
top=rasterToPoints(z)
lat_lon_rg1=albersgeod(top[,1], top[,2], sph="GRS80", clon=-96, clat=23, sp1=29.5, sp2=45.5)

#list_files=list.files('E:\\USU_Research_work\\TOPNET PROJECT\\MODEL COMPARISON\\A1_watershed_final\\A1_CD\\DAYMET',pattern="^filename.*\\.csv")
list_files=list.files(dir,pattern="^filename.*\\.csv")
len=length(list_files)
xx="file"
nc=len
start_year=args[2]
#start_year="2000"
end_year=args[3]
#end_year="2010"
for (i in 1:nc){
  xx[i]=paste("filename",i,"_",args[2],"_",args[3],".csv",sep="")
}
rainfall <- function(file ){
  mydata2 = read.csv(file,skip=7)
  my.data.frame <- mydata2[(mydata2$year%%4==0) & (mydata2$yday ==365), ]
  my.data.frame$yday=my.data.frame$yday+1
  total <- rbind( my.data.frame,mydata2)
  gh= total[with(total, order(year,yday)), ]
  rain=data.frame(rainmm=gh$prcp..mm.day., tmaxcel=gh$tmax..deg.c.,tmincel=gh$tmin..deg.c.,vppa= gh$vp..Pa.)
  
  return(rain)
}


###########calculating lapse rate from station information #######

Elevation<- function(file ){
  station_ele = as.matrix(read.csv(file))[3]
  ele = (as.numeric((unlist(strsplit(station_ele, split=' ', fixed=TRUE))[2])))
  return(ele)
}

Ele_station=matrix(ncol =1, nrow = nc)


dates=seq(as.Date(paste(start_year,"/1/1",sep="")), as.Date(paste(end_year,"/12/31",sep="")), "day") ##assume that daymet data would be always completed by one year
strDates= as.character(dates)
gh=gsub("-","", strDates, fixed=TRUE)
dss=data.frame(time=gh)
hr=rep.int(240000, nrow(dss))


for ( m in 1:length(xx)){
  hjk=rainfall(xx[m])
  Ele_station[m,]=Elevation(xx[m])
  dss=cbind(dss,hjk)
}

min_temp=dss[,seq(4,ncol(dss),4)]
max_temp=dss[,seq(3,ncol(dss),4)]
avgT=0.5*(max_temp+min_temp)

##finding monthly average for clipar.dat

station_monthly<- data.frame(monthlyfunction(avgT, FUN=mean, na.rm=TRUE,dates=dates))
station_annual<- t(as.matrix(annualfunction(avgT, FUN=mean, na.rm=TRUE,dates=dates)))
sta_ID=seq(1,nc,1)
sta_ele=rep(-999,nc)
station_monthly=cbind(sta_ID,lat_lon_rg1[,2],lat_lon_rg1[,1],sta_ele,station_monthly)
lapse_mat=cbind(Ele_station,station_annual)
dddd=lm(lapse_mat[,2]~lapse_mat[,1])
station_monthly[,4]=lapse_mat[,1]
station_monthly[] <- lapply(station_monthly, function(.col){ if (is.numeric(.col)) return(sprintf("%8.2f",.col))else return(.col)}) 

#writng clipar.dat
sink("clipar.dat") 
cat(sprintf("This file provides meta-data for each temperature station"),file='clipar.dat',append=TRUE)
cat("\n", file="clipar.dat", append=TRUE)
cat(sprintf("Temperature ranges are in Degrees Celcius"),file='clipar.dat',append=TRUE)
cat("\n", file="clipar.dat", append=TRUE)
sites=seq(1,(nc),1)
cat(sprintf("%d %s ", nc,"! Number of temperature stations"),file='clipar.dat',append=TRUE) 
cat("\n", file="clipar.dat", append=TRUE)
##please change standard longitude according to watershed location

std_longitude=-120.00;
cat(sprintf("%3.2f %s ",std_longitude,"!Standard Longitude of time zone used in local time calculations"),file='clipar.dat',append=TRUE) 
cat("\n", file="clipar.dat", append=TRUE)
cat(sprintf("'Station_id  Lat    Lon     Elev_m   Jan    Feb    Mar     Apr       May    Jun    Jul      Aug     Sep    Oct      Nov    Dec"),file='clipar.dat',append=TRUE)
cat("\n", file="clipar.dat", append=TRUE)
write.table(station_monthly, file = "clipar.dat",row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE)
sink()

print("Clipar.dat file created")
