
from CommonLib import *
import os
import subprocess

R_EXE_Path='C:\\Program Files\\R\\R-3.1.1\\bin\\x64'
R_Code_Path='E:\\USU_Research_work\\TOPNET_Web_Processing\\TOPNET_Web_services\\RCODE'
Exe_dir="E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\TOPNET_Exe"
TauDEM_dir='C:\\Program Files\\Microsoft HPC Pack 2012\\Bin',8,'E:\\USU_Research_work\\MMW_PROJECT\\TauDEM_Geo_Deliverables\\Taudem5PCVS2010Soln_512\\Taudem5PCVS2010\\x64\\Release'
Watershed_Name_Dir="E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\Test_Results\DelineatedWatershed\demc1w.tif"
PRISM_Name_Dir="E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\Base_Data\PRISMavgWesternUS\PRISM_ppt_30yr_normal_4kmM2_annual_bil.bil"
Input_Dem_Name_Dir="E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\Test_Results\DelineatedWatershed\demC1.tif"
In_Out_dir="E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\Test_Results\DelineatedWatershed"
Soil_Data_Dir='E:\USU_Research_work\TOPNET_Web_Processing\TOPNET_Web_services\Base_Data\gssurgoWesternUS\Oregon_Soil.tif'
NLCD_Data_Dir='E:\\USU_Research_work\\TOPNET_Web_Processing\\TOPNET_Web_services\\Base_Data\\nlcdWesternUS\\nlcd2011CONUS.tif'
Input_Dem="demC1"
USGS_gage="07014500"



#watershed_delineation(TauDEM_dir,In_Out_dir,'enogeo','Outlets',500,500,5000,15)
#REACH_LINK(Exe_dir,In_Out_dir,'enogeo')
#download_Soil_Data(Watershed_Name_Dir,Soil_Data_Dir,R_EXE_Path,R_Code_Path)
#daymet_download(Watershed_Name_Dir,2000,2010,R_EXE_Path,R_Code_Path)
#getLULCdata(NLCD_Data_Dir,R_EXE_Path,R_Code_Path)
#Create_Parspcfile(Input_Dem_Name_Dir,R_EXE_Path,R_Code_Path)
#BASIN_PARAM(Exe_dir,Input_Dem_Name_Dir)
#create_latlonfromxy(Watershed_Name_Dir,R_EXE_Path,R_Code_Path)
#crop_PRISM_Rain(Watershed_Name_Dir,PRISM_Name_Dir,R_EXE_Path,R_Code_Path)
#Create_rain_weight(Exe_dir,Watershed_Name_Dir)
#format_Rain_Weight(In_Out_dir,R_EXE_Path,R_Code_Path)
#create_rain_dat(In_Out_dir,2000,2010,R_EXE_Path,R_Code_Path)
#create_tmaxtmin_dat(In_Out_dir,2000,2010,R_EXE_Path,R_Code_Path)
#create_clipar_dat(In_Out_dir,Input_Dem+"w.tif",2000,2010,R_EXE_Path,R_Code_Path)
#download_streamflow(USGS_gage,2000,2010,In_Out_dir,R_EXE_Path,R_Code_Path)






