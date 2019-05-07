args<-commandArgs(TRUE)

dir=args[1]
#dir='E:\\USU_Research_work\\TOPNET_Web_Processing\\TOPNET_Web_services\\Test_Results\\DelineatedWatershed'
setwd(dir)
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
  xx[i]=paste("filename",i,"_",start_year,"_",end_year,".csv",sep="")
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

dates=seq(as.Date(paste(start_year,"/1/1",sep="")), as.Date(paste(end_year,"/12/31",sep="")), "day") ##assume that daymet data would be always completed by one year
strDates= as.character(dates)
gh=gsub("-","", strDates, fixed=TRUE)
dss=data.frame(time=gh)
hr=rep.int(240000, nrow(dss))

for ( m in 1:length(xx)){
  hjk=rainfall(xx[m])
  dss=cbind(dss,hjk)
}

precipitation=matrix(ncol = nc, nrow = nrow(dss))
for ( k in 1:(nc)){
  precipitation[,k]=dss[,4*k-2]
}
precip=data.frame(precipitation)
precip[] <- lapply(precip, function(.col){ if (is.numeric(.col)) return(sprintf("%8.2f",.col))else return(.col)}) 
precip=data.frame(precip,dss[,1],hr)

##writing rain.dat file

sink("rain.dat") 
cat(sprintf("This file provides daily precipitation rate for each rain station"),file='rain.dat',append=TRUE)
cat("\n", file="rain.dat", append=TRUE)
cat(sprintf("Precipitation is provided in mm/day"),file='rain.dat',append=TRUE)
cat("\n", file="rain.dat", append=TRUE)
sites=seq(1,(nc),1)
cat(sprintf("%s %d ", "ver2",nc),file='rain.dat',append=TRUE) 
cat(sprintf( "%d", sites),(sprintf( "%s", "Date Hour","\n")),file='rain.dat',append=TRUE) 
cat("\n", file="rain.dat", append=TRUE)
write.table(precip, file = "rain.dat",row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE)
sink()
