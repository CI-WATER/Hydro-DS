args<-commandArgs(TRUE)

dir=args[1]
#dir='C:\\Users\\shams\\.qgis2\\python\\plugins\\getClimateData'
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

x <- readLines(list_files[1]) 
last_year=strsplit(x[length(x)],",")[[1]][1]

dates=seq(as.Date(paste(start_year,"/1/1",sep="")), as.Date(paste(end_year,"/12/31",sep="")), "day") ##assume that daymet data would be always completed by one year
strDates= as.character(dates)
gh=gsub("-","", strDates, fixed=TRUE)
dss=data.frame(time=gh)
hr=rep.int(240000, nrow(dss))

for ( m in 1:length(xx)){
  hjk=rainfall(xx[m])
  dss=cbind(dss,hjk)
}

dewT=matrix(ncol =nc, nrow = nrow(dss))
actVp=matrix(ncol = nc, nrow = nrow(dss))
precipitation=matrix(ncol = nc, nrow = nrow(dss))
tmaxtmintdew=matrix(ncol = 1, nrow = nrow(dss))

for (j in 1:(nc)){for (i in 1:nrow(dss))
{
  
  actVp[i,j]=log(dss[i,(4*j+1)]/(1000*0.6108))# convert vapor pressure to kpa
  dewT[i,j]=(actVp[i,j]*237.3)/(17.27-actVp[i,j])
}
}

min_temp=dss[,seq(4,ncol(dss),4)]
max_temp=dss[,seq(3,ncol(dss),4)]
avgT=0.5*(max_temp+min_temp)

for ( k in 1:(nc)){
 tmaxtmintdew=cbind(tmaxtmintdew,dss[,4*k-1],dss[,4*k],dewT[,k])
}

temper=data.frame(tmaxtmintdew[,-1])
temper[] <- lapply(temper, function(.col){ if (is.numeric(.col)) return(sprintf("%8.2f",.col))else return(.col)})
temper=data.frame(temper,dss[,1],hr)

##writing tmaxtmintdew.dat file

sink('tmaxtmintdew.dat')
cat(sprintf("This file provides daily values of Tmax/Tmin/Tdew for each temperature station"),file='tmaxtmintdew.dat',append=TRUE)
cat("\n", file="tmaxtmintdew.dat", append=TRUE)
cat(sprintf("Temperature is provided in degrees Celcius"),file='tmaxtmintdew.dat',append=TRUE)
cat("\n", file="tmaxtmintdew.dat", append=TRUE)
sites=seq(1,(nc),1)
cat(sprintf("%s %d ", "ver2",nc),file='tmaxtmintdew.dat',append=TRUE) 
cat(sprintf( "%d", sites),(sprintf( "%s", "Date Hour","\n")),file='tmaxtmintdew.dat',append=TRUE) 
cat("\n", file="tmaxtmintdew.dat", append=TRUE)
write.table(temper, file = "tmaxtmintdew.dat",row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE)
sink()

print ("Tmaxtmimn tdew created ")