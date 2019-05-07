import shapefile
import numpy
from numpy import zeros
from numpy import logical_and
#import pandas as pd
import  os
import time
# from shapely.geometry import Point, LineString, mapping, shape
# from shapely.ops import cascaded_union
# import fiona
# from fiona import collection
from osgeo import ogr,osr,gdal
import rasterio.features
from numpy import *
import numpy as np
from affine import Affine
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
#import fiona
#import itertools
from osgeo import gdal
import os
import sys
#from rasterstats import zonal_stats
start_time = time.time()
import subprocess
import gdal,ogr
import sys
import glob
import sys
import os
from osgeo import ogr
from osgeo import osr
import numpy as np
from osgeo import gdal
from usu_data_service.servicefunctions.utils import *
from usu_data_service.servicefunctions.watershedFunctions import *
R_Code_Path = '/home/ahmet/ciwater/usu_data_service/topnet_data_service/TOPNET_Function/RCODE'
MPI_dir='/usr/local/bin'
np=8
TauDEM_dir='/home/ahmet/ciwater/usu_data_service/topnet_data_service/TauDEM'
Exe_dir='/home/ahmet/ciwater/usu_data_service/topnet_data_service/TOPNET_Basin_Properties'
Base_Data_dir_prism='/home/ahmet/hydosdata/PRISM_annual/PRISM_annual_projected.tif'
Base_Data_dir_Soil=os.path.join('/home/ahmet/hydosdata/gSSURGO','soil_mukey_westernUS.tif')
def watershed_delineation(DEM_Raster,Outlet_shapefile,Src_threshold,Min_threshold,Max_threshold,Number_threshold, output_pointoutletshapefile,output_watershedfile,output_treefile,output_coordfile,output_streamnetfile,output_slopareafile,output_distancefile):

    head,tail=os.path.split(str(DEM_Raster))

    In_Out_dir=str(head)
    base_name=os.path.basename(DEM_Raster)
    Input_Dem=os.path.splitext(base_name)[0]
    Outlet=Outlet_shapefile

    input_raster = os.path.splitext(DEM_Raster)[0]      #remove the .tif
    # pit remove
    #cmdString = "pitremove -z "+input_raster+".tif"+" -fel "+input_raster+"fel.tif"
    #retDictionary = call_subprocess(cmdString,'pit remove')
    #if retDictionary['success']=="False":
        #return retDictionary



    cmdstring=PITREMOVE(MPI_dir,np,TauDEM_dir, In_Out_dir,Input_Dem)
    print(cmdstring)
    retDictionary=call_subprocess(cmdstring,'pitremove')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(D8FLOWDIRECTIONS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'d8flow')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(D8CONTRIBUTING_AREA(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'d8area')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(THRESHOLD(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Src_threshold),'threshold')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(MOVEOUTLETTOSTREAMS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Outlet,output_pointoutletshapefile),'moveoutlet')
    if retDictionary['success'] == "False":
        return retDictionary
    #
    # driverName = "ESRI Shapefile"
    # driver = ogr.GetDriverByName(driverName)
    # dataset = driver.Open(Outlet_shapefile)
    # layer = dataset.GetLayer()
    # srs = layer.GetSpatialRef()
    # baseName = os.path.splitext(output_pointoutletshapefile)[0]
    # projFile = baseName+".prj"
    # #srsString = "+proj=utm +zone="+str(utmZone)+" +ellps=GRS80 +datum=NAD83 +units=m"
    # #srs = osr.SpatialReference()
    # #srs.ImportFromEPSG(epsgCode)
    # #srs.ImportFromProj4(srsString)
    # srs.MorphFromESRI()
    # file = open(projFile, "w")
    # file.write(srs.ExportToWkt())
    # file.close()

    ##add ID field to move outlets to stream file
    # Read in our existing shapefile
    r = shapefile.Reader(output_pointoutletshapefile)
   # Create a new shapefile in memory
    w = shapefile.Writer()
   # Copy over the existing fields
    w.fields = list(r.fields)
   #  Add our new field using the pyshp API
    w.field("ID", "C", "40")

   # We'll create a counter in this example
   # to give us sample data to add to the records
   #  so we know the field is working correctly.
    i=1

   # Loop through each record, add a column.  We'll
   # insert our sample data but you could also just
   # insert a blank string or NULL DATA number
   # as a place holder
    for rec in r.records():
       rec.append(i)
       i+=1
       # Add the modified record to the new shapefile
       w.records.append(rec)

   # Copy over the geometry without any changes
    w._shapes.extend(r.shapes())
    w.save(output_pointoutletshapefile)

   # Save as a new shapefile


    retDictionary=call_subprocess(PEUKERDOUGLAS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'peuker')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(ACCUMULATING_STREAM_SOURCE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_pointoutletshapefile),'aread8')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary= call_subprocess(DROP_ANALYSIS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Min_threshold,Max_threshold,Number_threshold,output_pointoutletshapefile),'dropana')
    if retDictionary['success'] == "False":
        return retDictionary
    fileHandle = open (os.path.join(In_Out_dir,Input_Dem+"drp.txt"),"r")
    lineList = fileHandle.readlines()
    fileHandle.close()
    LL= lineList[-1]
    thres=float(LL[25:35])
    if(thres>0):
        thres=thres
    else:
        thres=float(Max_threshold)

    retDictionary=call_subprocess(STREAM_SOURCE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,thres),'create strea')
    if retDictionary['success'] == "False":
        return retDictionary

    retDictionary=call_subprocess(StreamNet(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_pointoutletshapefile,output_watershedfile,output_treefile, output_coordfile,output_streamnetfile),'delineatewatershed')
    if retDictionary['success'] == "False":
        return retDictionary

    retDictionary=call_subprocess(WETNESS_INDEX(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_slopareafile),'sloparearatio')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(DISTANCE_DOWNSTREAM(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem, output_distancefile),'distactnetostream')
    if retDictionary['success'] == "False":
        return retDictionary
    return {'success': 'True', 'message': 'Watershed Delineation successful'}


def PITREMOVE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))
    commands.append(os.path.join(TauDEM_dir, "pitremove"));commands.append("-z")
    commands.append(os.path.join(In_Out_dir,Input_Dem+".tif"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"fel.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def D8FLOWDIRECTIONS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np));

    commands.append(os.path.join(TauDEM_dir, "d8flowdir"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-sd8")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"sd8.tif"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"fel.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def D8CONTRIBUTING_AREA(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np));

    commands.append(os.path.join(TauDEM_dir, "aread8"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-ad8")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ad8.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def DINFFLOWDIRECTIONS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "dinfflowdir"));commands.append("-ang")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ang.tif"));commands.append("-slp")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"slp.tif"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"fel.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def DINFCONTRIBUTINGAREA(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "areadinf"));commands.append("-ang")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ang.tif"));commands.append("-sca")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"sca.tif"));
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command


def THRESHOLD(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Src_threshold):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "threshold"));commands.append("-ssa")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ad8.tif"));commands.append("-src")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"src.tif"));commands.append("-thresh");commands.append(str(Src_threshold))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def MOVEOUTLETTOSTREAMS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Outlet,output_pointoutletshapefile):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "moveoutletstostrm"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-src")
    commands.append(os.path.join(In_Out_dir, Input_Dem+"src.tif"));commands.append("-o");commands.append(os.path.join((In_Out_dir+Outlet), Outlet))
    commands.append("-om");commands.append(os.path.join(In_Out_dir, output_pointoutletshapefile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def PEUKERDOUGLAS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "peukerdouglas"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"fel.tif"));commands.append("-ss")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ss.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command


def ACCUMULATING_STREAM_SOURCE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_pointoutletshapefile):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "aread8"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-o")
    commands.append(os.path.join(In_Out_dir, output_pointoutletshapefile));commands.append("-ad8")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ssa.tif"));commands.append("-wg")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ss.tif"))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def DROP_ANALYSIS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,Min_threshold,Max_threshold,Number_threshold,output_pointoutletshapefile):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))
    commands.append(os.path.join(TauDEM_dir, "dropanalysis"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"fel.tif"));commands.append("-ad8")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ad8.tif"));commands.append("-ssa")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ssa.tif"));commands.append("-drp")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"drp.txt"));commands.append("-o")
    commands.append(os.path.join(In_Out_dir, output_pointoutletshapefile));commands.append("-par")
    commands.append(str(Min_threshold));commands.append(str(Max_threshold));commands.append(str(Number_threshold));commands.append(str(0))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def FIND_OPTIMUM(In_Out_dir,Input_Dem):
    fileHandle = open(os.path.join(In_Out_dir,Input_Dem+"drp.txt"),"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    LL= lineList[-1]
    #global thres
    thres=LL[25:35]

    return thres

def STREAM_SOURCE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,thershold):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "threshold"));commands.append("-ssa")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ssa.tif"));commands.append("-src")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"src2.tif"));commands.append("-thresh")
    commands.append(str(thershold))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command



def StreamNet(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_pointoutletshapefile,output_watershedfile,output_treefile,output_coordfile,output_streamnetfile):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "streamnet"));commands.append("-fel")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"fel.tif"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-ad8")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ad8.tif"));commands.append("-src")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"src2.tif"));commands.append("-ord")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ord2.tif"));commands.append("-tree")
    commands.append(os.path.join(In_Out_dir,output_treefile));commands.append("-coord")
    commands.append(os.path.join(In_Out_dir,output_coordfile));commands.append("-net")
    commands.append(os.path.join(In_Out_dir,output_streamnetfile));commands.append("-w")
    commands.append(os.path.join(In_Out_dir,output_watershedfile));commands.append("-o")
    commands.append(os.path.join(In_Out_dir,output_pointoutletshapefile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def WETNESS_INDEX(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_slopareafile):
    commands=[]
   # commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "slopearearatio"));commands.append("-slp")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"sd8.tif"));commands.append("-sca")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"ad8.tif"));commands.append("-sar")
    commands.append(os.path.join(In_Out_dir,output_slopareafile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command

def DISTANCE_DOWNSTREAM(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem,output_distancefile):
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(np))

    commands.append(os.path.join(TauDEM_dir, "d8hdisttostrm"));commands.append("-p")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"p.tif"));commands.append("-src")
    commands.append(os.path.join(In_Out_dir,Input_Dem+"src.tif"));commands.append("-dist")
    commands.append(os.path.join(In_Out_dir,output_distancefile));
    fused_command = ''.join(['"%s" ' % c for c in commands])
    return fused_command



def REACH_LINK(DEM_Raster,Watershed_Raster,treefile,coordfile,output_reachfile,output_nodefile,output_reachareafile,output_rchpropertiesfile):
    head,tail=os.path.split(str(DEM_Raster))
    In_Out_dir=str(head)
    base_name=os.path.basename(DEM_Raster)
    Input_Dem=os.path.splitext(base_name)[0]
    retDictionary=call_subprocess(PITREMOVE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'pitremove')
    if retDictionary['success'] == "False":
        return retDictionary
    retDictionary=call_subprocess(D8FLOWDIRECTIONS(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'d8flow')
    if retDictionary['success'] == "False":
        return retDictionary
    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(1))

    commands.append(os.path.join(Exe_dir,"ReachLink"))
    commands.append("-me");commands.append(Watershed_Raster)
    commands.append("-p");commands.append(os.path.join(In_Out_dir,Input_Dem+'p.tif'))
    commands.append("-tree");commands.append(treefile)
    commands.append("-coord");commands.append(coordfile)
    commands.append("-rchlink");commands.append(os.path.join(In_Out_dir, output_reachfile))
    commands.append("-nodelink");commands.append(os.path.join(In_Out_dir, output_nodefile))
    commands.append("-nc");commands.append(os.path.join(In_Out_dir, Input_Dem+"nc.tif"))
    commands.append("-dc");commands.append(os.path.join(In_Out_dir, Input_Dem+"dc.tif"))
    commands.append("-rca");commands.append(os.path.join(In_Out_dir, output_reachareafile))
    commands.append("-rcp");commands.append(os.path.join(In_Out_dir, output_rchpropertiesfile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    #return fused_command
    os.system(fused_command)
    return {'success': 'True', 'message': 'download daymetdata successful'}

def DISTANCE_DISTRIBUTION(Watershed_Raster,SaR_Raster,Dist_Raster,output_distributionfile):
    head,tail=os.path.split(str(Watershed_Raster))
    In_Out_dir=str(head)


    commands=[]
    #commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(1))

    commands.append(os.path.join(Exe_dir,"DistWetness"))
    commands.append("-me");commands.append(Watershed_Raster)
    commands.append("-twi");commands.append(SaR_Raster)
    commands.append("-dis");commands.append(Dist_Raster)
    commands.append("-dists");commands.append(os.path.join(In_Out_dir, output_distributionfile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command)
    return {'success': 'True', 'message': 'download daymetdata successful'}

# """download soil data """

def download_Soil_Data(Watershed_Raster,output_f_file,output_k_file,output_dth1_file,output_dth2_file,output_psif_file,output_sd_file,output_tran_file):
    head,tail=os.path.split(str(Watershed_Raster))
    ##headsoil,tailsoil=os.path.split(str(Soil_Raster))
   
    os.chdir(head)
    wateshed_Dir=str(head)
    watershed_raster_name=str(tail)
    cmd1="gdaltindex clipper.shp"+" "+ Watershed_Raster
    os.system(cmd1)
    soil_output_file=os.path.join(head,'Soil_mukey.tif')
    cdf="gdalwarp -cutline clipper.shp -dstnodata NA -crop_to_cutline"+" "+ Base_Data_dir_Soil  +" "+"Soil_mukey.tif"
    os.system(cdf)
    #os.chdir(head)
    # Raster_to_Polygon(tail)
    #infile_crs=[]
    #with fiona.open('temp'+'.shp') as source:
    #  projection = source.crs
    #  infile_crs.append(projection)
    #print(projection)
    # os.chdir(head)
    #polygon_dissolve('temp','final',infile_crs[0])    
    #outputBufferfn='final.shp'
    #soil_output_file=os.path.join(head,'Soil_mukey.tif')
   
    #input = fiona.open(outputBufferfn, 'r')
    #xmin=str(input.bounds[0])
    #print(xmin)
    #ymin=str(input.bounds[1])
    #xmax=str(input.bounds[2])
    #ymax=str(input.bounds[3])
    #layer_name=os.path.splitext(outputBufferfn)[0]
    #print(ymax)
    ##command_flow="gdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -dstnodata -32768.000 -cutline " +  outputBufferfn + " -cl "+ layer_name + " " + Soil_Raster + " " + soil_output_file
    #cdf="gdalwarp -cutline final.shp -dstnodata NA -crop_to_cutline"+" "+ Base_Data_dir_Soil  +" "+'Soil_mukey.tif'
    #os.system(cdf)
   

    Soil_script = os.path.join(R_Code_Path,'Extract_Soil_Data.r')
    heads,tails=os.path.split(str(soil_output_file))
    commands=[]
    commands.append("Rscript");commands.append(Soil_script);commands.append(str(wateshed_Dir))
    commands.append(str(tails));commands.append(str(output_f_file))
    commands.append(str(output_k_file));commands.append(str(output_dth1_file))
    commands.append(str(output_dth2_file));commands.append(str(output_psif_file))
    commands.append(str(output_sd_file));commands.append(str(output_tran_file))

    fused_command = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command)
    return {'success': 'True', 'message': 'download daymetdata successful'}

def daymet_download(Watershed_Raster,Start_Year,End_Year,output_rainfile,output_temperaturefile,output_cliparfile,output_gagefile):
    head,tail=os.path.split(str(Watershed_Raster))
    watershed_dir=str(head)
    wateshed_name=str(tail)
    daymet_download_script= os.path.join(R_Code_Path,'daymet_download.r')
    commands=[]
    commands.append("Rscript");commands.append(daymet_download_script);commands.append(str(watershed_dir))
    commands.append(str(wateshed_name));commands.append(str(Start_Year));commands.append(str(End_Year))
    commands.append(str(output_gagefile))
    fused_command1 = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command1)
    raindat_script= os.path.join(R_Code_Path,'create_rain.R')
    commands=[]
    commands.append("Rscript");commands.append(raindat_script)
    commands.append(str(watershed_dir));commands.append(str(Start_Year));commands.append(str(End_Year));
    commands.append(str(output_rainfile))
    fused_command2 = ''.join(['"%s" ' % c for c in commands])

    os.system(fused_command2)

    tmaxtmin_script= os.path.join(R_Code_Path,'create_tmaxtmintdew.r')
    commands=[]
    commands.append("Rscript");commands.append(tmaxtmin_script)
    commands.append(str(watershed_dir));commands.append(str(Start_Year));commands.append(str(End_Year))
    commands.append(str(output_temperaturefile))
    fused_command3 = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command3)

    clipar_script= os.path.join(R_Code_Path,'create_clipar.R')
    commands=[]
    commands.append("Rscript");commands.append(clipar_script)
    commands.append(str(watershed_dir));commands.append(str(Start_Year));commands.append(str(End_Year))
    commands.append(str(wateshed_name));commands.append(str(output_cliparfile));
    fused_command4 = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command4)
    return {'success': 'True', 'message': 'download daymetdata successful'}



def getprismdata(Watershed_Raster,output_raster):
    prism_Raster=(Base_Data_dir_prism)
    head,tail=os.path.split(str(Watershed_Raster))
    subset_raster_to_referenceRaster(prism_Raster,Watershed_Raster,output_raster)
    return {'success': 'True', 'message': 'download LULC data  successful'}
## under consideration

def Create_Parspcfile(Watershed_Raster,output_parspcfile):
    head,tail=os.path.split(str(Watershed_Raster))
    watershed_dir=str(head)
    watershed_base=os.path.basename(Watershed_Raster)
    wateshed_name=os.path.splitext(str(watershed_base))[0]
    parspc_script= os.path.join(R_Code_Path,'create_parspc_file.R')
    commands=[]
    commands.append("Rscript");commands.append(parspc_script)
    commands.append(str(watershed_dir));commands.append(str(wateshed_name));commands.append(str(output_parspcfile));
    fused_command = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command)
    return {'success': 'True', 'message': 'download LULC data  successful'}

def create_latlonfromxy(Watershed_Raster,output_latlonfromxyfile):
    head,tail=os.path.split(str(Watershed_Raster))
    watershed_dir=str(head)
    wateshed_name=str(tail)
    latlonxy_script= os.path.join(R_Code_Path,'latlon_from_xy.R')
    commands=[]
    commands.append("Rscript");commands.append(latlonxy_script)
    commands.append(str(watershed_dir));commands.append(str(wateshed_name))
    commands.append(str(output_latlonfromxyfile))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command)
    return {'success': 'True', 'message': 'download LULC data  successful'}


def Create_rain_weight(Watershed_Raster,Rain_gauge_shapefile,annual_rainfile,nodelink_file,output_rainweightfile):
    head,tail=os.path.split(str(Watershed_Raster))
    watershed_dir=str(head)
    wateshed_name=str(tail)
    head_rg,tail_rg=os.path.split(str(Rain_gauge_shapefile))
    head_nd,tail_nd=os.path.split(str(nodelink_file))
    head_an,tail_an=os.path.split(str(annual_rainfile))
    Rain_GaugeDir=str(head_rg)

    #subset_raster_to_referenceRaster(Base_Data_dir_prism,os.path.join(watershed_dir,'annrain.tif'),Watershed_Raster)
   # prism_script= os.path.join(R_Code_Path,'annrain_prism.r')

   

    commands=[]
    commands.append(os.path.join(Exe_dir,"RainWeight"))
    commands.append("-w");commands.append(os.path.join(watershed_dir, wateshed_name))
    commands.append("-rg");commands.append(os.path.join(Rain_GaugeDir,tail_rg))
    commands.append("-ar");commands.append(os.path.join(watershed_dir,tail_an))
    commands.append("-tri");commands.append(os.path.join(watershed_dir,"triout.tif"))
    commands.append("-wt");commands.append(os.path.join(watershed_dir,"weights.txt"))
    fused_command1 = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command1)

    format_rainweight_script= os.path.join(R_Code_Path,'format_rainweight.R')
    commands=[]
    commands.append("Rscript");commands.append(format_rainweight_script)
    commands.append(str(watershed_dir)); commands.append(str(tail_nd))
    commands.append(str(output_rainweightfile))
    fused_command2 = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command2)
    return {'success': 'True', 'message': 'Creating rainweight file successful'}


def download_streamflow(USGS_gage, Start_Year, End_Year, output_streamflow):
    start=str(Start_Year)+"-01-01"
    end=str(End_Year)+"-12-31"
    Output_Dir = os.path.dirname(output_streamflow)
    #R_EXE_Path='/usr/bin/'
    R_Code_Path = '/home/ahmet/ciwater/usu_data_service/topnet_data_service/TOPNET_Function/RCODE'
    streamflow_script= os.path.join(R_Code_Path,'get_USGS_streamflow.r')
    commands=[]
    commands.append("Rscript")
    commands.append(streamflow_script)
    #commands.append(os.path.join(R_EXE_Path, "Rscript"));commands.append(streamflow_script)
    commands.append(str(USGS_gage));commands.append(str(start));commands.append(str(end))
    commands.append(str(Output_Dir)); commands.append(str(output_streamflow))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    os.system(fused_command)
    return {'success': 'True', 'message': 'download streamflow successful'}

def Raster_to_Polygon2(input_file,output_file):
    gdal.UseExceptions()
    src_ds = gdal.Open(input_file)
    if src_ds is None:
        #print 'Unable to open %s' % src_filename
        sys.exit(1)
    try:
        srcband = src_ds.GetRasterBand(1)
        srd=srcband.GetMaskBand()
    except RuntimeError as e:
        # for example, try GetRasterBand(10)
        #print 'Band ( %i ) not found' % band_num
        #print e
        sys.exit(1)
    dst_layername = output_file
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
    dst_layer = dst_ds.CreateLayer(dst_layername, srs = None )
    gdal.Polygonize( srcband,srd, dst_layer, -1, [], callback=None )



def findGDALCoordinates(path):
    if not os.path.isfile(path):
       return []
    data = gdal.Open(path,0)
    if data is None:
       return []
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1]*data.RasterXSize
    miny = maxy + geoTransform[5]*data.RasterYSize
    return [minx,miny,maxx,maxy]


def Raster_to_Polygon(input_file):

   gdal.UseExceptions()
   src_ds = gdal.Open(input_file,GA_ReadOnly)
   print(input_file)
   #target = osr.SpatialReference()
   wkt =src_ds.GetProjection()
   print(wkt)
   src =osr.SpatialReference()
   print(src)
   ds=src.ImportFromWkt(wkt)
   #srcband = src_ds.GetRasterBand(1)
   myarray =(src_ds.GetRasterBand(1).ReadAsArray())
   #print(myarray)
   T0 = Affine.from_gdal(*src_ds.GetGeoTransform())
   tx=[T0[0], T0[1], T0[2], T0[3],T0[4], T0[5]]
   print(tx)
   epsg_code=[]
   #if (src.IsProjected()):
      #  ds=epsg_code.append(int(src.GetAuthorityCode("PROJCS")))
       # print(ds)
 
  # else:
     #  epsg_code.append(int(src.GetAuthorityCode("GEOGCS")))
   target = osr.SpatialReference()
   target.ImportFromEPSG(102003)
   if src_ds is None:
     #print 'Unable to open %s' % src_filename
     sys.exit(1)
   try:
      srcband = src_ds.GetRasterBand(1)
      srd=srcband.GetMaskBand()

   except RuntimeError as e:
        # for example, try GetRasterBand(10)
        #print 'Band ( %i ) not found' % band_num
        #print e
        sys.exit(1)

  

   drv = ogr.GetDriverByName("ESRI Shapefile")
   if os.path.exists('temp.shp'):
     drv.DeleteDataSource('temp.shp')

   dst_layername ='temp'
   dst_ds = drv.CreateDataSource('temp'+ ".shp" )  
   print(dst_ds)
   dst_layer = dst_ds.CreateLayer(dst_layername, srs=target)
   gdal.Polygonize( srcband,srd, dst_layer, -1, [], callback=None)
   src_ds=None

   
def dissolve_polygon(input_raster,output_file,dir):
    #os.chdir(dir)
    ds = gdal.Open(input_raster)
    print(ds)
    print(input_raster)
    if os.path.exists(output_file):
      drv.DeleteDataSource(output_file)
    grid_code=[]
   
    band =  ds.GetRasterBand(1)

    myarray =(ds.GetRasterBand(1).ReadAsArray())
    #print(myarray)
    T0 = Affine.from_gdal(*ds.GetGeoTransform())
    tx=[T0[0], T0[1], T0[2], T0[3],T0[4], T0[5]]
    drv = ogr.GetDriverByName("ESRI Shapefile")

    for shp, val in rasterio.features.shapes(myarray,transform=tx):
    # print('%s: %s' % (val, shape(shp)))
     if(val>=0):
       grid_code.append(float(val))
    #add_filed_existing_shapefile('temp1.shp',np.asarray(grid_code))
    pj=[]
    with fiona.open('temp.shp') as input:
     meta = input.meta
    with fiona.open('temp.shp', 'r') as source:

    # Copy the source schema and add two new properties.
      sink_schema = source.schema.copy()
      sink_schema['properties']['ID'] = 'float'
   

    # Create a sink for processed features with the same format and
    # coordinate reference system as the source.
      with fiona.open(
            'temp2.shp', 'w',
            crs=source.crs,
            driver=source.driver,
            schema=sink_schema,
            ) as sink:
        i=0
        for f in source:
                #print(f)
           
                
                # Add the signed area of the polygon and a timestamp
                # to the feature properties map.
                f['properties'].update(
                    ID=grid_code[i],
                   )
                i+=1
                sink.write(f)



      pj=[]
      with fiona.open('temp2.shp') as input:
       meta = input.meta
       print('srt')
       with fiona.open('final.shp', 'w',**meta) as output:
        # groupby clusters consecutive elements of an iterable which have the same key so you must first sort the features by the 'STATEFP' field
         e = sorted(input, key=lambda k: k['properties']['ID'])
         print(e)
         # group by the 'STATEFP' field
         for key, group in itertools.groupby(e, key=lambda x:x['properties']['ID']):
            properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
            # write the feature, computing the unary_union of the elements in the group with the properties of the first element in the group
            output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})


def create_basin_param(watershed_shapefile,lancover_raster,lutluc,lutkc,paramfile,nodelinkfile,output_basinfile):

  import pandas as pd


  input_datalist=pd.read_csv(paramfile,header=None,error_bad_lines=False)
  data_length=len(input_datalist.index)
  print(data_length)
  #print input_datalist[0][1]
  lulc_table=pd.read_csv(lutluc,delim_whitespace=True,header=None,skiprows=1)
  lukc_table=pd.read_csv(lutkc,delim_whitespace=True,header=None,skiprows=1)
  #print lulc_table[1]
  watershed_shapefile=watershed_shapefile
  head,tail=os.path.split(str(lancover_raster))
  print(tail)
  from osgeo import gdal
  import numpy as np
  ds = gdal.Open(str(tail))
  band =  ds.GetRasterBand(1)
  myarray = (band.ReadAsArray())
  unique_values = np.unique(myarray)

  features = fiona.open(watershed_shapefile)
  grid_code=[]
  for feat in features:
     grid_code.append(feat['properties']['ID'])
  basin_num=len(grid_code)
  #this function need for calculating land use land cover with look up table
  def reclassify_and_stats_raster(input_raster,lookup_table_in,lookup_table_out,watershed_shapefile):
    input_raster= input_raster
    ds = gdal.Open(input_raster)
    band = ds.GetRasterBand(1)
    classification_values =lookup_table_in
    classification_output_values = lookup_table_out
#

    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    xsize = band.XSize
    ysize = band.YSize

    max_value = band.GetMaximum()
    min_value = band.GetMinimum()

    if max_value == None or min_value == None:
      stats = band.GetStatistics(0, 1)
      max_value = stats[1]
      min_value = stats[0]

    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    dst_ds = driver.Create("temp.tif", xsize, ysize, 1, gdal.GDT_Float64 )
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(ds.GetProjection())

    for i in range(0, ysize, y_block_size):
      if i + y_block_size < ysize:
        rows = y_block_size
      else:
        rows = ysize - i
      for j in range(0, xsize, x_block_size):
        if j + x_block_size < xsize:
            cols = x_block_size
        else:
            cols = xsize - j

        data = band.ReadAsArray(j, i, cols, rows)
        r = zeros((rows, cols), numpy.uint8)

        for k in range(len(classification_values) - 1):
            if classification_values[k] <= max_value and (classification_values[k + 1] > min_value ):
                r = r + classification_output_values[k] * logical_and(data >= classification_values[k], data < classification_values[k + 1])
        if classification_values[k + 1] < max_value:
            r = r + classification_output_values[k+1] * (data >= classification_values[k + 1])

        dst_ds.GetRasterBand(1).WriteArray(r,j,i)

    dst_ds = None
    stats2 = zonal_stats(watershed_shapefile, "temp.tif",stats=['mean'])
    mean_val=([d['mean'] for d in stats2])
    result = pd.DataFrame(mean_val)
    return(result)

  #nodfile_data=pd.read_csv(nodelinkfile,header=None)
  df = pd.DataFrame(grid_code,columns=[str('DrainId')])
  for i in range(0,data_length):
    soil_pro_file=input_datalist[1][i]
    print(soil_pro_file)
    if(soil_pro_file==0):
        print (input_datalist[2][i])
        stats = zonal_stats(watershed_shapefile, str(input_datalist[2][i]),stats=['mean'])
        
        mean_val=([d['mean'] for d in stats])
        df1 = pd.DataFrame(mean_val)
        df[str(input_datalist[0][i])]=df1
    elif(soil_pro_file==2):
         col_ind=int(input_datalist[4][i])
         df2=pd.DataFrame(reclassify_and_stats_raster(str(input_datalist[2][i]),unique_values,np.array(lulc_table[col_ind]),watershed_shapefile))

         df[str(input_datalist[0][i])]=df2
    elif(soil_pro_file==1):
         col_ind=int(input_datalist[4][i])
         df3=pd.DataFrame(reclassify_and_stats_raster(str(input_datalist[2][i]),unique_values,np.array(lukc_table[col_ind]),watershed_shapefile))
         df[str(input_datalist[0][i])]=df3

    else:
        val=[input_datalist[2][i]]*basin_num
        df4 = pd.DataFrame(val,dtype=np.float32)
        df[str(input_datalist[0][i])]=df4

  #print(df)
  nodfile_data=pd.read_csv(nodelinkfile, dtype= {'NodeId':np.int,'DownNodeId':np.int,'DrainId':np.int,'ProjNodeId':np.int,'DOutFlag':np.int,'ReachId':np.int,'Area':np.float64,'AreaTotal':np.float64,'X':np.float64,'Y':np.float64})
  nd_df = pd.DataFrame(nodfile_data)
  nd_df.columns = ['NodeId', 'DownNodeId' , 'DrainId' , 'ProjNodeId',  'DOutFlag', 'ReachId','Area','AreaTotal', 'X','Y']
  nd_df['Area']=nd_df['Area']*1000000
  #print (nd_df)
 # CatchID,DownCatchID,DrainID,NodeId,Reach_number,Outlet_X,Outlet_Y,direct_area,

  df.columns = ['DrainId', 'f', 'ko','dth1','dth2','soildepth','c','psif','chv','cc','cr','albedo','LapseRate','AverageElevation','ImperviousFraction','TileDrainedFraction','DitchDrainedFraction',
               'TileCoeff','DitchCoef','IrrigatedFraction','SprinklerFractionofIrrigation','IrrigationEfficiency','D_Thres','Z_Max','D_Goal',
                'kc_1','kc_2','kc_3','kc_4','kc_5','kc_6','kc_7','kc_8','kc_9','kc_10','kc_11','kc_12','Transmissivity','FractionForest']
  nd_df.columns = ['NodeId', 'DownNodeId' , 'DrainId' , 'ProjNodeId',  'DOutFlag', 'ReachId','Area','AreaTotal', 'X','Y']

  result = pd.merge(df,nd_df,
         left_on=['DrainId'],
         right_on=['DrainId'],
         how='inner')
  result.sort_index(by=['NodeId'], ascending=[True],inplace=True)
  dd=result.ix[:,1:(data_length+1)]
  print(dd)
  node_df=nd_df[['NodeId', 'DownNodeId','DrainId','ProjNodeId','X','Y' ,'ReachId','Area']]
  result2 = pd.concat([node_df,dd], axis=1)
  #result2['Area']=result2['Area']*float(1000000)
  result2.to_csv(output_basinfile, header=True, index=None, sep=',', mode='w')



##example:



def BASIN_PARAM(DEM_Raster,Watershed_Raster,f_raster,k_raster,dth1_raster,dth2_raster,sd_raster,psif_raster,tran_raster,lulc_raster,
                lutlc,lutkc,parameter_specficationfile,nodelinksfile,output_basinfile):

    head0,tail0=os.path.split(str(DEM_Raster))
    head1,tail2=os.path.split(str(f_raster))
    head2,tail2=os.path.split(str(k_raster))
    head3,tail3=os.path.split(str(dth1_raster))
    head4,tail4=os.path.split(str(dth2_raster))
    head5,tail5=os.path.split(str(sd_raster))
    head6,tail6=os.path.split(str(tran_raster))
    head7,tail7=os.path.split(str(psif_raster))
    head8,tail8=os.path.split(str(lulc_raster))
    head9,tail9=os.path.split(str(lutlc))
    head10,tail10=os.path.split(str(lutkc))
    head,tail=os.path.split(str(Watershed_Raster))
    In_Out_dir=str(head)




    In_Out_dir=str(head0)
    base_name=os.path.basename(DEM_Raster)
    Input_Dem=os.path.splitext(base_name)[0]
    retDictionary=call_subprocess(PITREMOVE(MPI_dir,np,TauDEM_dir,In_Out_dir,Input_Dem),'pitremove')
    if retDictionary['success'] == "False":
        return retDictionary
    #head,tail=os.path.split(str(Watershed_Raster))
    # #head_ps,tail_ps=os.path.split(str(parameterfile))
    Dem_dir=str(head0)

    #Dem_base=os.path.basename(Watershed_Raster)
    #Dem_name=os.path.splitext(str(Dem_base))[0]
    #commands=[]
    ##commands.append(os.path.join(MPI_dir,"mpirun"));commands.append("-np");commands.append(str(1))
   # commands.append(os.path.join(Exe_dir,"BasinParammeter"))
    #commands.append("-me");commands.append(Watershed_Raster)
    #commands.append("-parspec");commands.append(parameter_specficationfile)
   # commands.append("-node");commands.append(nodelinksfile)
    #commands.append("-mpar");commands.append( output_basinfile)
   # fused_command = ''.join(['"%s" ' % c for c in commands])
    #os.chdir( In_Out_dir)
    # print (fused_command)
    #os.system(fused_command)
    #print(head)
    os.chdir(head)
    Raster_to_Polygon(tail)
    #print('test1done')
    #os.chdir(head)
    dissolve_polygon(tail,'final.shp',head)
    #print('test2done')
    create_basin_param('final.shp',lulc_raster,lutlc,lutkc,parameter_specficationfile,nodelinksfile,output_basinfile)

   # os.system(fused_command)

    return {'success': 'True', 'message': 'download LULC data  successful'}



##example:

#Raster_to_Polygon('WhLA10WS.tif')
#dissolve_polygon('WhLA10WS.tif','final.shp')
#create_basin_param('final.shp','lulcmmef.tif','lutluc.txt','lutkc.txt','demC22param.txt','nodelinks.txt','basin.txt')












