#/usr/bin/python
import os
import sys
#print sys.path
from CommonLib import *

TauDEM_dir='/home/nazmus/TauDEM'
In_Out_dir='/home/nazmus/TOPNET_PreProcessing/Test_C1/'
Input_Dem='demC1'
MPI_dir='/usr/lib64/openmpi/bin'
R_EXE_Path='/usr/bin/'
R_Code_Path='/home/nazmus/TOPNET_PreProcessing/TOPNET_Function/RCODE'



np=1
Src_threshold=1000
Min_threshold=1000
Max_threshold=3000
Number_threshold=10
Outlet='outletC1'
Exe_dir='/home/nazmus/TOPNET_PreProcessing/TOPNET_Basin_Properties/'
##running watershed delineation
##watershed_delineation(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Outlet,Src_threshold,Min_threshold,Max_threshold,Number_threshold)

##creating reachlink
##REACH_LINK(MPI_dir,np,Exe_dir,In_Out_dir,Input_Dem)
##Distance and wetness index
#DISTANCE_DISTRIBUTION(MPI_dir,np,Exe_dir,In_Out_dir,Input_Dem)

##download climate data


Start_year=2000
End_year=2010
Watershed_Raster=os.path.join(In_Out_dir,'demC1w.tif')

#daymet_download(Watershed_Raster,Start_year,End_year,R_EXE_Path,R_Code_Path)

climate_file_dir=In_Out_dir
Watershed_Raster_Name='demC1w.tif'
#create_rain_dat(climate_file_dir,Start_year,End_year,R_EXE_Path,R_Code_Path)
#create_tmaxtmin_dat(climate_file_dir,Start_year,End_year,R_EXE_Path,R_Code_Path)
create_clipar_dat(climate_file_dir,Watershed_Raster_Name,Start_year,End_year,R_EXE_Path,R_Code_Path)

