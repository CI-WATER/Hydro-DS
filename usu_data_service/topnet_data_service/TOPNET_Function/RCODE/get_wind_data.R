args<-commandArgs(TRUE)
dir=args[1]
s1=as.numeric(args[2])
s2=as.numeric(args[3])
library(RNCEP)
library(raster)
#setwd("C:\\Users\\shams\\.qgis2\\python\\plugins\\getClimateData")
setwd(dir)
rs=raster('dem_A1.tif')
b=extent(rs)
be <- c(xmin(b),ymin(b),xmax(b),ymax(b))
u_wind <- NCEP.gather(variable='uwnd.sig995',level='surface',months.minmax=c(1,12), years.minmax=c(s1,s2),lat.southnorth=c(ymax(b),ymin(b)), lon.westeast=c(360+xmin(b),360+xmax(b)),reanalysis2 = FALSE, return.units = TRUE)
v_wind <- NCEP.gather(variable='vwnd.sig995',level='surface',months.minmax=c(1,12), years.minmax=c(s1,s2),lat.southnorth=c(ymax(b),ymin(b)), lon.westeast=c(360+xmin(b),360+xmax(b)),reanalysis2 = FALSE, return.units = TRUE)
wx.df <- NCEP.array2df(wx.data=list(u_wind , v_wind),var.names=c('Uwind', 'Vwind'))
wind_six_hours=data.frame(time=wx.df$datetime,wind=(sqrt(wx.df$Uwind^2+wx.df$Vwind^2)))
x1=length(unique(wx.df$latitude))
x2=length(unique(wx.df$longitude))
wind_data_h=t(matrix(wind_six_hours$wind,nrow=4*x1*x2,ncol=dim(wx.df)[1]/(4*x1*x2)))
wind=data.frame(rowMeans(wind_data_h) )
wind <- lapply(wind, function(.col){ if (is.numeric(.col)) return(sprintf("%8.2f",.col))else return(.col)}) 

start_year=toString(args[2])
end_year=toString(args[3])

dates=seq(as.Date(paste(start_year,"/1/1",sep="")), as.Date(paste(end_year,"/12/31",sep="")), "day") ##assume that daymet data would be always completed by one year
strDates= as.character(dates)
gh=gsub("-","", strDates, fixed=TRUE)
dss=data.frame(time=gh)
hr=rep.int(240000, nrow(dss))

wind_speed=data.frame(wind,dss,hr) ##Need to change dss
wind_speed=data.frame(wind,dss,hr) ##Need to change dss

sink('wind.dat')
cat(sprintf("This file provides daily values of wind speed for each wind station"),file='wind.dat',append=TRUE)
cat("\n", file="wind.dat", append=TRUE)
cat(sprintf("Wind speed is provided in m/sec"),file='wind.dat',append=TRUE)
cat("\n", file="wind.dat", append=TRUE)
sites=seq(1,1,1) ## need to automate this one
cat(sprintf("%s %d ", "ver2",1),file='wind.dat',append=TRUE) 
cat(sprintf( "%d", sites),(sprintf( "%s", "Date Hour","\n")),file='wind.dat',append=TRUE) 
cat("\n", file="wind.dat", append=TRUE)
write.table(wind_speed, file = "wind.dat",row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE)
sink()