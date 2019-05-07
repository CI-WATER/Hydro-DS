

args<-commandArgs(TRUE)

require(zoo)
require(XML)
require(RCurl)
require(dataRetrieval)

#Get daily data
setwd(args[4])
siteNumber=args[1]
dates=seq(as.Date(args[2]), as.Date(args[3]), "day")
print("start Downloading")
streamflow_Daily = readNWISdv(siteNumber,"00060",args[2],args[3])
streamflow=data.frame(streamflow_Daily )
print(streamflow)
daily_streamflow=streamflow[,4]*0.0283168466 # convert to cfs to m3/s
match_index=match(dates,streamflow_Daily$Date)
match_flow=data.frame(daily_streamflow[match_index])

print("Finish Downloading")
##there are some missing data match_index=match(dates,streamflow_Daily$Date)
match_flow[] <- lapply(match_flow, function(.col){ if (is.numeric(.col)) return(sprintf("%8.2f",.col))else return(.col)}) 
streamflow=data.matrix(match_flow)
streamflow[is.na(streamflow)] <- -999

strDates= as.character(dates)
gh=gsub("-","", strDates, fixed=TRUE)
dss=data.frame(time=gh)
hr=rep.int(240000, nrow(dss))
observed_flow=data.frame(streamflow,dss[,1],hr)
print("start Writing")

sink('streamflow_calibration.dat')
cat(sprintf("This file provides mean daily values of streamflow"),file='streamflow_calibration.dat',append=TRUE)
cat("\n", file="streamflow_calibration.dat", append=TRUE)
cat(sprintf("Flow values are provided in m3/sec"),file='streamflow_calibration.dat',append=TRUE)
cat("\n", file="streamflow_calibration.dat", append=TRUE)
cat(sprintf(paste("USGS gauge number",as.character(siteNumber),sep="")),file='streamflow_calibration.dat',append=TRUE)
cat("\n", file="streamflow_calibration.dat", append=TRUE)

sites=seq(1,length(siteNumber),1)
cat(sprintf("%s %d ", "ver2",length(siteNumber)),file='streamflow_calibration.dat',append=TRUE) 
cat(sprintf( "%d", sites),(sprintf( "%s", "Date Hour","\n")),file='streamflow_calibration.dat',append=TRUE) 
cat("\n", file="streamflow_calibration.dat", append=TRUE)
write.table(observed_flow, file = "streamflow_calibration.dat",row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE)
sink()

print("Finish Writing")