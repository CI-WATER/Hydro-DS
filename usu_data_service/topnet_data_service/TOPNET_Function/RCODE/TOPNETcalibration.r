args<-commandArgs(TRUE)
require(hydroGOF)
require(zoo)
require(plyr)
require(hydroPSO)

#install.packages("hydroPSO")


#setwd("E:\\USU_Research_work\\TOPNET PROJECT\\MODEL COMPARISON\\A1_watershed_final_DAYMET\\matlab_cali")
#setwd("E:\\USU_Research_work\\RAINFALL_COMPARISON\\B21_watershed\\Maurer_RUN")
#trying to do some calibration:
# setwd(args[1])
# start_date_arg=args[2]  # integer 19970101
# length_cali_args=args[3] ##2191
# start_date1_args=args[4] ##1997/1/1
# end_date1_args=args[5]   ##2002/12/31
# length_cali_start_args=args[6] ##731
# warm_date1_args=args[7]       ##1999/1/1

# start_date_arg=19970101  # integer 19970101
# length_cali_args=2191 ##2191
# start_date1_args="1997/1/1" ##1997/1/1
# end_date1_args="2002/12/31"   ##2002/12/31
# length_cali_start_args=731 ##731
# warm_date1_args="1999/1/1"       ##1999/1/1
setwd(args[1])

assign("start_date_arg", as.numeric(args[2]), envir = .GlobalEnv)

assign("length_cali_args", as.numeric(args[3]), envir = .GlobalEnv)
assign("start_date1_args", args[4], envir = .GlobalEnv)
assign("end_date1_args", args[5], envir = .GlobalEnv)

assign("length_cali_start_args",as.numeric(args[6]), envir = .GlobalEnv)
assign("warm_date1_args", args[7], envir = .GlobalEnv)

xe1=c(as.numeric(args[8]),as.numeric(args[9]),as.numeric(args[10]),as.numeric(args[11]),as.numeric(args[12]),as.numeric(args[13]),as.numeric(args[14]),as.numeric(args[15]))
xe2=c(as.numeric(args[16]),as.numeric(args[17]),as.numeric(args[18]),as.numeric(args[19]),as.numeric(args[20]),as.numeric(args[21]),as.numeric(args[22]),as.numeric(args[23]))



topnet_calibration=function(x){
  f_parm=x[1]
  k_parm=x[2]
  dth1_parm=x[3]
  dth2_parm=x[4]
  soilc_parm=x[5]
  c_parm=1
  psif_parm=1
  chv_parm=1
  cc_parm=x[6]
  cr_parm=x[7]
  sro_parm=1
  cvo_parm=1
  n_parm=1
  T_parm=x[8]

  model_read=as.matrix(read.delim(file="modelspc.dat", header=F, sep = " "))
  bn=as.numeric(model_read[3,2])
  streamflow_cal=as.matrix(read.delim(file="streamflow_calibration.dat", header=F, sep = " "))
  cal_min=streamflow_cal[5,2]
  cal_max=streamflow_cal[dim(streamflow_cal)[1],2]
  dd1=as.matrix(strsplit(cal_min,""))
  dd2=as.matrix(strsplit(cal_max,""))
  
  dd1=unlist(dd1)
  dd2=unlist(dd2)
  calfile_start_date=paste(paste(dd1[1],dd1[2],dd1[3],dd1[4],sep=""),"/",paste(dd1[5],dd1[6],sep=""),"/",paste(dd1[7],dd1[8],sep=""),sep="")
  calfile_end_date=paste(paste(dd2[1],dd2[2],dd2[3],dd2[4],sep=""),"/",paste(dd2[5],dd2[6],sep=""),"/",paste(dd2[7],dd2[8],sep=""),sep="")
  
 # print("tesingfffffffff")
  
  sink('topinp.dat')
  cat(sprintf("%d  %s", start_date_arg, "start_date"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d  %s", 240000, "start_hour"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d  %s", 86400, "timestep(86400 s = 1 day)"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d  %d  %s",length_cali_args,length_cali_args, "nsteps  (11325 is 31 years, 19591001 to 19901002.  16894 is 46 years 19591001 to 20051231)"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d  %s", 1, "detailstart"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d  %s", 0, "detailend"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%d %d %d %s", 0,0,0, "Detail/Debug Output Control (3 flags.  OutputYes, Basin, IrrigDrainCase.  The first is 0 or 1 to indicate if topsbd_v7.txt is to be written or not.  The second flag controls whether detail output should be written for one basin or all basins. A value of 0 (with OutputYes=1) results in all basins being output. The third flac controls whether detail output should be written for one or all irrigation drainage cases.  A value of 0 implies all cases, otherwise just the case indicated is output (1: no irrig, no drainage, 2: tile no irrig, 3: ditch no irrig, 4: irrig no drainage, 5: irrig tile, 6: irrig ditch) "),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", f_parm, "f"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", k_parm, "Ko"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f %s", dth1_parm, "DTH1"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f %s", dth2_parm, "DTH2"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s",soilc_parm, "SOILC"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f %s", c_parm, "C"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s",psif_parm, "PSIF"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s",chv_parm, "CHV"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  
  cat(sprintf("%f  %s",cc_parm, "CC"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", cr_parm, "CR"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s",1, "Albedo"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", sro_parm, "SRO"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f %s", 1, "ZBARO"),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", cvo_parm, "CVO"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", n_parm, "n"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f %s", T_parm, "Transmissivity "),file='topinp.dat',append=TRUE); cat("\n", file="topinp.dat", append=TRUE)
  cat(sprintf("%f  %s", 0.5, "ImperviousFraction"),file='topinp.dat',append=TRUE) ;cat("\n", file="topinp.dat", append=TRUE)
  sink()
  
  system(paste("topnet_modified"))
  ff=scan("FlowAtStreamNodes_cms.txt", what="")
  #l=basin_number+2
  l=bn+2
  ff1=ff[seq(l,length(ff),1)] ## need to change theis things later
  simu_flow=matrix(as.numeric(ff1[seq(2,length(ff1),l-1)])) ##need to change this later
  sf=scan("streamflow_calibration.dat", what="")
  sf1=sf[seq(21,length(sf),1)] ## need to change theis things later
  obs_flow=(as.numeric(sf1[seq(1,length(sf1),3)])) ##need to change this later
  
  #time_all= seq(as.Date("1980/1/1"), as.Date("2012/12/31"), "day") #create time series
  #time_warm_cali= seq(as.Date("1997/1/1"), as.Date("2002/12/31"), "day") # create time series based on start and end date
  time_all= seq(as.Date(calfile_start_date), as.Date(calfile_end_date), "day") #create time series
  time_warm_cali= seq(as.Date(start_date1_args), as.Date(end_date1_args), "day") # create time series based on start and end date
  
  
  date_overlap=match(time_warm_cali,time_all) # get overlap time interval
  observd_flow=matrix(obs_flow[date_overlap])
  observd_flow[observd_flow<0] <- NA
  #calibrated_flow=data.frame(simu=simu_flow[731:2191,],observ=observd_flow[731:2191,]) ##take only from 2010/01/01---2012/12/31
  #time= seq(as.Date("1999/1/1"), as.Date("2002/12/31"), "day") # create time series based on start and end date
  calibrated_flow=data.frame(simu=simu_flow[length_cali_start_args:length_cali_args,],observ=observd_flow[length_cali_start_args:length_cali_args,]) ##take only from 2010/01/01---2012/12/31
  time= seq(as.Date(warm_date1_args), as.Date(end_date1_args), "day") # create time series based on start and end date
  
  
  
  #plot(time,calibrated_flow$observ, type="o", col="blue",,xlab=" Time(days)",ylab="stream flow (m3/s)",cex.lab=1.5,cex.axis=1.5,cex.main=1.5,cex.sub=1.5)
  #lines(time,calibrated_flow$simu, type="o", pch=22, lty=2, col="red")
  #legend(14650, max(calibrated_flow$observ), c("observed flow","simulated flow"), cex=1, col=c("blue","red"), pch=21:22, lty=1:2,pt.cex=1);
  CE=NSE(calibrated_flow$simu,calibrated_flow$observ,na.rm=TRUE)
  BIAS=sum(calibrated_flow$simu,na.rm=TRUE)/sum(calibrated_flow$observ,na.rm=TRUE)
  return(CE)
  
}


#xe1=c(0.15,1,0.5,0.5,0.5,0.1,0.75,0.5)
#xe2=c(5,500,1,2,2,10,10,5)


hydroPSO(fn=topnet_calibration,lower=xe1,upper=xe2,control=list(MinMax='max'))
print("tesingfffffffff")


