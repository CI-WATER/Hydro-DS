args<-commandArgs(TRUE)

# install.packages('raster', dep=TRUE)
# install.packages('plyr', dep=TRUE)
# install.packages('Hmisc', dep=TRUE)
# install.packages('soilDB', dep=TRUE) # stable version from CRAN + dependencies
# install.packages("soilDB", repos="http://R-Forge.R-project.org") # most recent copy from r-forge
# install.packages("SSOAP", repos = "http://www.omegahat.org/R", type="source") # SSOAP and XMLSchema



#Input: 

#(1)SSURGO grid for interested area
#(2)Landcover raster data  
#(3)nodelinks.txt
#(4)Pit removed DEM
#(5)parameter specification file
#(6)lookup table for lulc and kc,cc,cr,albedo

#Output:

#(1)basinpars.txt
print("testing")
require(raster)
require(plyr)
require(Hmisc)
require(soilDB)
require(SSOAP)
require(foreign)
require(shapefiles)
library(rgdal)

dir=args[1]
setwd(dir)

r <- raster(args[2]) # get grid info from gssurgo data (download soil spatial and tabular data as tif format is big size)
r <- ratify(r,count=TRUE)
rat <- levels(r)[[1]]
mu=data.frame(rat)
names(mu)[1] <- 'MUKEY'
names(mu)[2] <- 'Count'
#mu=mu[-1,]
in.statement <- format_SQL_in_statement(mu$MUKEY)


##make query for each variable

q1 <- paste("SELECT component.mukey, component.cokey, compname, comppct_r, hzdept_r, hzdepb_r, hzname,awc_r, ksat_r,wthirdbar_r,wfifteenbar_r,dbthirdbar_r,
            sandtotal_r,claytotal_r,om_r
            FROM component JOIN chorizon ON component.cokey = chorizon.cokey
            AND mukey IN ", in.statement, "ORDER BY mukey, comppct_r DESC, hzdept_r ASC", sep="")

# now get component and horizon-level data for these map unit keys
res <- SDA_query(q1)



##query for soil depth
q2 <- paste("SELECT mukey,brockdepmin
            FROM muaggatt
            WHERE  mukey IN ", in.statement, "
            ", sep="")

res2 <- SDA_query(q2)


# # function for copmuting weighted-mean  within a component key unit
co.mean.whc <- function(i) {
  wt <- i$comppct_r[1] # keep the first component pct (they are all the same)
  thick1 <- with(i, hzdepb_r - hzdept_r)# compute horizon thickness
  thick=thick1/100 ##in m
  #ksat <- thick/i$ksat_r #compute saturated hydraulic conductivity
  #ksat<-i$ksat_r[1]*3600*10^(-6)
  wcthirdbar <- thick * i$wthirdbar_r # compute water content at 1/3 bar with horizon
  wctfifteendbar  <- thick * i$wfifteenbar_r # compute water content at 15 bar with horizon
  dbthirdbar  <- thick * i$dbthirdbar_r # compute density at 1/3 bar with horizon
  sand <- thick * i$sandtotal_r# compute percentage of sand by weight with horizon
  clay<- thick * i$claytotal_r # compute percentage of clay  by weight with horizon
  om <- thick * i$om_r # compute percentage of organic matter by weight  with horizon
  awc <-  i$awc_r # available water capacity 
  
  thick.total=sum(thick, na.rm=TRUE)
  awc.total=sum(awc, na.rm=TRUE)
  awc.depth=( sum((thick *((!is.na(awc))*1)),na.rm=TRUE))
  #ksat.total <- sum(thick, na.rm=TRUE)/(sum(ksat, na.rm=TRUE)) # Harmonic mean
  #ksat.total<-ksat
  
  wcthirdbar.total <- (sum( wcthirdbar , na.rm=TRUE))/ (sum((thick *((!is.na( wcthirdbar))*1)),na.rm=TRUE))# depth weighted average of water content at 1/3 bar for each component  key
  wctfifteendbar.total <- (sum(wctfifteendbar, na.rm=TRUE))/(sum((thick *((!is.na( wctfifteendbar))*1)),na.rm=TRUE))# depth weighted average of water content at 15 bar for each component  key
  dbthirdbar.total <- (sum(dbthirdbar, na.rm=TRUE))/ (sum((thick *((!is.na( dbthirdbar))*1)),na.rm=TRUE))# depth weighted average of bulk density  at 1/3 bar for each component  key
  sand.total <- (sum(sand, na.rm=TRUE))/ (sum((thick *((!is.na( sand))*1)),na.rm=TRUE))# depth weighted average of sand   for each component  key
  clay.total <- (sum(clay, na.rm=TRUE))/ (sum((thick *((!is.na(clay))*1)),na.rm=TRUE)) # depth weighted average of clay  for each component  key
  om.total <- (sum(om, na.rm=TRUE))/ (sum((thick *((!is.na( om))*1)),na.rm=TRUE)) # depth weighted average of organic matter  for each component  key
  
  yy=log(3600*10^(-6)*i$ksat_r)
  xx=i$hzdept_r/100
  len=length(xx)
  if(len>1){
    
    hh=lm(yy~xx)
    fval=hh$coefficients[2]
    ko=exp(hh$coefficients[1])
  }else{
    fval=NA
    ko=NA}
  
  
  fval[fval>=0]=-1/thick.total ##positive value replace by inverse of depth
  #fval[fval>=0]=-0.001 ##from TOPNET paper
  fval=abs(fval)
  fval[fval<0.001]=1/thick.total ###constant k gives very low value of f , so replace those by inverse of depth
  # fval[fval<0.001]=0.001
  #fval[fval>5]=5
  ksat.total=ko
  ksat.total[is.na(ksat.total)]=i$ksat_r[1]*3600*10^(-6)
  trans=ksat.total/fval
  #trans=ksat.total*thick.total ##testing only for A1 has problem with base flow??
  #yy1=(3600*10^(-6)*i$ksat_r)
  #xx1=thick
  #tri=sum(yy1*xx1,na.rm=TRUE)/sum(xx1,na.rm=TRUE)
  
  #trans=tri*thick.total
  
  data.frame(ksat=ksat.total,wcthird=wcthirdbar.total,wctfifteendbar=wctfifteendbar.total,  dbthirdbar=dbthirdbar.total,
             sand=sand.total,clay=clay.total,om=om.total,awc=awc.total,awcdepth=awc.depth, thick=1/fval,wt=wt,f=fval,tr=trans) # return profile water storage and component pct
  
  #,f=fval
}

# function for copmuting weighted-mean whc within a map unit
mu.mean.whc <- function(i) {
  thick <- wtd.mean(i$ thick, weights=i$wt) # safely compute wt. mean ksat for each map unit key
  ksat <- wtd.mean(i$ ksat, weights=i$wt) # safely compute wt. mean ksat for each map unit key
  
  wcthird<- wtd.mean(i$wcthird, weights=i$wt) # safely compute wt. mean water content at 1/3 bar for each map unit key
  wctfifteendbar <- wtd.mean(i$wctfifteendbar, weights=i$wt) # safely compute wt. mean water content at 15 bar for each map unit key
  dbthirdbar <- wtd.mean(i$dbthirdba, weights=i$wt) # safely compute wt. mean bulk density at 1/3 bar for each map unit key
  sand <- wtd.mean(i$sand, weights=i$wt) # safely compute wt. mean sand for each map unit key
  clay<- wtd.mean(i$ clay, weights=i$wt) # safely compute wt. mean clay for each map unit key
  om<- wtd.mean(i$om, weights=i$wt) # safely compute wt. mean organic matter for each map unit key
  fvalue= wtd.mean(i$f, weights=i$wt,na.rm=TRUE)
  
  ts= wtd.mean(i$tr, weights=i$wt,na.rm=TRUE)
  data.frame(depth=thick,ksat=ksat,wcthird=wcthird,wctfifteendbar=wctfifteendbar, dbthirdbar= dbthirdbar,sand=sand,clay=clay,om=om,fval=fvalue,tr=ts) # return wt. mean water storage
  #,fval=fvalue*-1
}

# aggregate by component  unit
co.whc <- ddply(res, c('mukey', 'cokey'), co.mean.whc)
# aggregate by map unit
mu.whc <- ddply(co.whc, 'mukey', mu.mean.whc)



# saturated hydraulic conductivity
ko=mu.whc$ksat 

# drainable moisture content
porosity=1-mu.whc$dbthirdbar/2.65
dth1=porosity-mu.whc$wcthird/100   

# plant available moisture content
dth2=(mu.whc$wcthird-mu.whc$wctfifteendbar)/100 
dth2[dth2<0]=0

#soil depth 
#soildepth=res2$brockdepmin

# pore disconnectedness index
b=(log(1500)-log(33))/(log(mu.whc$wcthird)-log(mu.whc$wctfifteendbar)) ## from Rawsl 1992 et al
c1=1; ## TOPNET use c=1
c=2*b+3 # from Dingman
b=(c-3)/2

##Green-Ampt wetting front suction parameter in m
##equations are taking from Rawls et at 1992
suctiont1=-21.67*mu.whc$sand/100-27.93*mu.whc$clay/100-81.97*dth1+71.12*(mu.whc$sand*dth1/100) +8.29*(mu.whc$clay*dth1/100)+14.05*(mu.whc$sand*mu.whc$clay/10000)+27.16
suction=suctiont1+(0.02*suctiont1*suctiont1-0.113*suctiont1-0.70) #unit kpa 
suction_meter=suction*0.102 # convert kpa=m of water
psif=((2*b+3)/(2*b+6))*abs(suction_meter) #equation from Dingman


soil_data=data.frame(mukey=mu.whc$mukey, depth=mu.whc$depth,fvalue=mu.whc$fval,ksat=ko,dth1=dth1,dth2=dth2,c=c1,psif=psif,tr=mu.whc$tr)
#soil_data=data.frame(mukey=mu.whc$mukey, depth=mu.whc$depth,fvalue=f,ksat=ko,dth1=dth1,dth2=dth2,c=c,psif=psif)


## need to think about soil depth

names(soil_data)[1]='ID'
names(mu)[1]='ID'
soildata_join=join( mu,soil_data, by='ID')
rat.new=join(rat,soildata_join,type='left')
rat.new <- rat.new[,c("ID", "COUNT","fvalue","ksat","dth1","dth2","psif","depth","tr")]


##Need to discuss and think



levels(r)=rat.new

q=c("f","ko","dth1","dth2","psif","sd","Trans")

#setwd(args[3])
for(i in 1:length(q)){
  r.new=deratify(r,att=names( rat.new)[i+2]) 
  r.new[is.na(r.new[])] <- cellStats(r.new,mean) ## fill missing data with mean value
  writeRaster(r.new,(paste(q[i],".tif",sep="")),overwrite=TRUE,datatype='FLT4S',format="GTiff",options="COMPRESS=NONE")
}




