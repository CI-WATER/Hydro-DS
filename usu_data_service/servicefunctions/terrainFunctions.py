try:
    from osgeo import gdal
except:
    import gdal
try:
    from osgeo import ogr
except:
    import ogr
try:
    from osgeo import osr
except:
    import osr

from gdalconst import *
#import shlex
#import subprocess
import os
from . watershedFunctions import create_OutletShape
from . netcdfFunctions import reverse_netCDF_yaxis_and_rename_variable
from usu_data_service.utils import *
from .utils import *
from usu_data_service.servicefunctions.gdal_calc import Calc   # TODO: upload to production

def get_raster_subset(input_raster=None, output_raster=None, xmin=None, ymax=None, xmax=None, ymin=None):
    #parameters are ulx uly lrx lry
    """ To Do: Boundary check-> check if the bounding box of subset raster is
               within the input_raster's boundary

    Note: upper left (ul) considered origin, i.e. xmin, ymax
    parameters passed as ulx uly lrx lry
    """
    cmdString = "gdal_translate"+" "+"-projwin"+" "+str(xmin)+" "+str(ymax)+" "\
               +str(xmax)+" "+str(ymin)+" "+input_raster+" "+output_raster

    return call_subprocess(cmdString,'get raster subset')


def rasterToNetCDF_rename_variable(input_raster=None, output_netcdf=None, increasing_x=False, increasing_y=False, output_varname='Band1'):
    if not increasing_y:
        temp_netcdf = os.path.join(os.path.dirname(input_raster), 'temp.nc')
        cmdString = "gdal_translate -of netCDF "+input_raster+" "+temp_netcdf
        retDictionary = call_subprocess(cmdString, 'raster to netcdf')
        if retDictionary['success']== "False":
            return retDictionary

        retDictionary= reverse_netCDF_yaxis_and_rename_variable(input_netcdf=temp_netcdf, output_netcdf=output_netcdf,
                                                 input_varname='Band1', output_varname=output_varname)
        if retDictionary['success'] == "False":
            return retDictionary
    else:
        cmdString = "gdal_translate -of netCDF "+input_raster+" "+output_netcdf
        retDictionary = call_subprocess(cmdString, 'raster to netcdf')
        if retDictionary['success']== "False":
            return retDictionary


    # TODO: implement later
    if not increasing_x:
        pass

    return retDictionary


def rasterToNetCDF(input_raster, output_netcdf):
    cmdString = "gdal_translate -of netCDF -co \"FORMAT=NC4\" " + input_raster + " " + output_netcdf
    return call_subprocess(cmdString, 'raster to netcdf')

def project_shapefile_UTM_NAD83(input_shape_file, output_shape_file, utm_zone):
    """ This projection tested for when the source shape file is in WGS84 Geographic
    coordinate syste (EPSG:4326), but generally gdal/ogr recognizes the input srs
    """
    cmdString = "ogr2ogr -t_srs '+proj=utm +zone=" +str(utm_zone)+ " +ellps=GRS80 +datum=NAD83 units=m' "\
              +output_shape_file+" "+input_shape_file
    return call_subprocess(cmdString, "Project shapefile")


def project_shapefile_EPSG(input_shape_file, output_shape_file, epsg_code):
    """ This projection tested for when the source shape file is in WGS84 Geographic
    coordinate syste (EPSG:4326), but generally gdal/ogr recognizes the input srs
    """
    cmdString = "ogr2ogr -t_srs EPSG:"+str(epsg_code)+" "+output_shape_file+" "+input_shape_file
    return call_subprocess(cmdString, "Project Shape File")

def delineate_Watershed_TauDEM(input_DEM_raster=None, outlet_point_x=None, outlet_point_y=None, output_raster=None,
                               output_outlet_shapefile=None, epsg_code=None, stream_threshold=None):
    """TauDEM doesn't take compressed file; uncompress file
        ToDO:  Check compression first"""

    input_Outlet_shpFile_uuid_path = generate_uuid_file_path()

    response_dict = create_OutletShape(shapefilePath=input_Outlet_shpFile_uuid_path, outletPointX=outlet_point_x,
                                       outletPointY=outlet_point_y)

    if response_dict['success'] == 'False':
        return response_dict

    input_Outlet_shpFile = os.path.join(input_Outlet_shpFile_uuid_path, 'outlet', 'outlet.shp')
    input_proj_shape_file = os.path.join(input_Outlet_shpFile_uuid_path, 'outlet', 'outlet-proj.shp')

    response_dict = project_shapefile_EPSG(input_shape_file=input_Outlet_shpFile, epsg_code=epsg_code,
                                           output_shape_file=input_proj_shape_file)
    if response_dict['success'] == 'False':
        return response_dict

    temp_raster = 'temp.tif'
    retDictionary = uncompressRaster(input_DEM_raster, temp_raster)
    if retDictionary['success'] == "False":
        return retDictionary

    input_raster = os.path.splitext(input_DEM_raster)[0]      #remove the .tif

    # pit remove
    cmdString = "pitremove -z "+temp_raster+" -fel "+input_raster+"fel.tif"
    retDictionary = call_subprocess(cmdString,'pit remove')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 flow dir
    cmdString = "d8flowdir -fel "+input_raster+"fel.tif -sd8 "+input_raster+"sd8.tif -p "\
                +input_raster+"p.tif"
    retDictionary = call_subprocess(cmdString, 'd8 flow direction')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 contributing area without outlet shape file
    cmdString = "aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -nc"         #check the effect of -nc
    #-o "\ +input_outletshp
    retDictionary = call_subprocess(cmdString, 'd8 contributing area')
    if retDictionary['success']=="False":
        return retDictionary
    #Get statistics of ad8 file to determine threshold

    #Stream definition by threshold
    cmdString = "threshold -ssa "+input_raster+"ad8.tif -src "+input_raster+"src.tif -thresh "+str(stream_threshold)
    retDictionary = call_subprocess(cmdString, 'Stream definition by threshold')
    if retDictionary['success']=="False":
        return retDictionary

    #move outlets to stream
    cmdString = "moveoutletstostrm -p "+input_raster+"p.tif -src "+input_raster+"src.tif -o "\
                +input_proj_shape_file+ " -om "+output_outlet_shapefile
    retDictionary = call_subprocess(cmdString, 'move outlet to stream')
    if retDictionary['success']=="False":
        return retDictionary
    #Add projection to moved outlet ---TauDEM excludes the projection from moved outlet; check
    #project_Shapefile_UTM_NAD83("outletMoved.shp", output_Outlet_shpFile, utmZone)
    #driver = ogr.GetDriverByName("ESRI Shapefile")
    #dataset = driver.Open(input_Outlet_shpFile)
    #layer = dataset.GetLayer()
    #srs = layer.GetSpatialRef()
    baseName = os.path.splitext(output_outlet_shapefile)[0]
    projFile = baseName+".prj"

    #srsString = "+proj=utm +zone="+str(utmZone)+" +ellps=GRS80 +datum=NAD83 +units=m"
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)

    #srs.ImportFromEPSG(4326)
    #srs.ImportFromProj4(srsString)
    srs.MorphFromESRI()
    file = open(projFile, "w")
    file.write(srs.ExportToWkt())
    file.close()
    #d8 contributing area with outlet shapefile
    cmdString = "aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -o "+output_outlet_shapefile+" -nc"
    retDictionary = call_subprocess(cmdString, 'd8 contributing area with outlet shapefile')
    if retDictionary['success']=="False":
        return retDictionary
    #watershed grid file
    cmdString = "gdal_calc.py -A "+input_raster+"ad8.tif --outfile="+output_raster+" --calc=A/A"
    retDictionary = call_subprocess(cmdString, "watershed grid computation")

    delete_working_uuid_directory(input_Outlet_shpFile_uuid_path)
    return retDictionary
    #To do: Delete temp raster
    #       Free other objects
    #       Direct TauDEM messages to file


def delineate_Watershed_atShapeFile(input_DEM_raster, input_outlet_shapefile, output_raster, output_outlet_shapefile,
                                    stream_threshold):
    """TauDEM doesn't take compressed file; uncompress file
        ToDO:  Check compression first"""

    file_folder = os.path.dirname(input_DEM_raster)
    temp_raster = os.path.join(file_folder, 'temp.tif')

    retDictionary = uncompressRaster(input_DEM_raster, temp_raster)
    if retDictionary['success']=="False":
        return retDictionary

    input_raster = os.path.splitext(input_DEM_raster)[0]      #remove the .tif
    # pit remove
    cmdString = "/home/ahmet/hydosbin/pitremove -z "+temp_raster+" -fel "+input_raster+"fel.tif"
    retDictionary = call_subprocess(cmdString,'pit remove')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 flow dir
    cmdString = "/home/ahmet/hydosbin/d8flowdir -fel "+input_raster+"fel.tif -sd8 "+input_raster+"sd8.tif -p "\
                +input_raster+"p.tif"
    retDictionary = call_subprocess(cmdString, 'd8 flow direction')
    if retDictionary['success']=="False":
        return retDictionary

    #d8 contributing area without outlet shape file
    cmdString = "/home/ahmet/hydosbin/aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -nc"         #check the effect of -nc
    #-o "\ +input_outletshp
    retDictionary = call_subprocess(cmdString, 'd8 contributing area')
    if retDictionary['success']=="False":
        return retDictionary

    #Get statistics of ad8 file to determine threshold

    #Stream definition by threshold
    cmdString = "/home/ahmet/hydosbin/threshold -ssa "+input_raster+"ad8.tif -src "+input_raster+"src.tif -thresh "+str(stream_threshold)
    retDictionary = call_subprocess(cmdString, 'Stream definition by threshold')
    if retDictionary['success']=="False":
        return retDictionary

    #move outlets to stream
    cmdString = "/home/ahmet/hydosbin/moveoutletstostrm -p "+input_raster+"p.tif -src "+input_raster+"src.tif -o "\
                +input_outlet_shapefile+ " -om "+output_outlet_shapefile
    retDictionary = call_subprocess(cmdString, 'move outlet to stream')

    if retDictionary['success'] == "False":
        return retDictionary

    #Add projection to moved outlet ---TauDEM excludes the projection from moved outlet; check
    driverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(driverName)
    dataset = driver.Open(input_outlet_shapefile)
    layer = dataset.GetLayer()
    srs = layer.GetSpatialRef()
    baseName = os.path.splitext(output_outlet_shapefile)[0]
    projFile = baseName+".prj"
    #srsString = "+proj=utm +zone="+str(utmZone)+" +ellps=GRS80 +datum=NAD83 +units=m"
    #srs = osr.SpatialReference()
    #srs.ImportFromEPSG(epsgCode)
    #srs.ImportFromProj4(srsString)
    srs.MorphFromESRI()
    file = open(projFile, "w")
    file.write(srs.ExportToWkt())
    file.close()
    #d8 contributing area with outlet shapefile
    cmdString = "/home/ahmet/hydosbin/aread8 -p "+input_raster+"p.tif -ad8 "+input_raster+"ad8.tif -o "+output_outlet_shapefile+" -nc"
    retDictionary = call_subprocess(cmdString, 'd8 contributing area with outlet shapefile')
    if retDictionary['success'] == "False":
        return retDictionary

    #watershed grid file using the threshold function
    cmdString =  "/home/ahmet/hydosbin/threshold -ssa "+input_raster+"ad8.tif -src "+output_raster+" -thresh 1"
                 ##" python \"C:/Python34/Lib/site-packages/osgeo/gdal_calc.py\" -A "+input_raster+"ad8.tif --outfile="+output_WS_raster+" --calc=A/A"
    retDictionary = call_subprocess(cmdString, "watershed grid computation")
    return retDictionary

    #To do: Delete temp raster
    #       Free other objects
    #       Direct TauDEM messages to file

def combineRasters(input_raster1=None, input_raster2=None, output_raster=None):
    """To  Do: may need to specify output no-data value
    """
    cmdString = "gdalwarp "+input_raster1+" "+input_raster2+" "+output_raster
    return call_subprocess(cmdString, 'join (stitch) two raster files')


def uncompressRaster(input_raster, output_raster):
    """TauDEM doesn't take compressed file; uncompress file
        ToDO:  Check compression first"""
    cmdString = "gdal_translate -co COMPRESS=NONE"+" "\
               +input_raster+" "+output_raster
    return call_subprocess(cmdString, 'uncompress raster')


def computeRasterAspect(input_raster=None, output_raster=None):
    cmdString = "gdaldem"+" "+"aspect"+" "+input_raster+" "+output_raster+" "+"-compute_edges"+" "+"-zero_for_flat"
    return call_subprocess(cmdString, 'compute aspect')


def computeRasterSlope(input_raster=None, output_raster=None):
    """ to run this from a different directory than the python module resides
    add path info: os.path......"""
    cmdString = "gdaldem"+" "+"slope"+" "+input_raster+" "+output_raster+" "+"-compute_edges"
    return call_subprocess(cmdString,'compute slope')


def raster_calculator(input_raster=None, function=None, outputfile=None, NoDataValue=0, type='Int32', **kwargs):
    try:
        Calc(calc=function, A=input_raster, outfile=outputfile, NoDataValue=NoDataValue, type=type)
        response_dict = {'success': 'True'}
    except:
        response_dict = {'success': 'False',
                         'message': 'Failed to convert the raster data as integer value'}
    return response_dict