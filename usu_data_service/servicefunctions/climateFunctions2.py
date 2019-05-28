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
import numpy
import netCDF4
import math
from datetime import datetime, timedelta

from . watershedFunctions import create_OutletShape
from . netcdfFunctions import reverse_netCDF_yaxis_and_rename_variable
from usu_data_service.utils import *
from .utils import *

import logging
#import shlex
#import subprocess
logger = logging.getLogger(__name__)


def get_raster_Difference(input_raster, reference_raster, output_raster):
    """This re-grids a raster to target/reference resolution
    Input coordinates are time, y, x
    Warning: Works only if the target boundary is within the input boundary & the coordinates directions are
    the same, i.e. y increasing / decreasing """
    # epsg=4326
    # Read input geo information
    srs_data = gdal.Open(input_raster, GA_ReadOnly)
    # srs_data = gdal.Open('NetCDF:"'+input_netcdf+'":'+inout_varName)
    srs_band = srs_data.GetRasterBand(1)
    varin = srs_band.ReadAsArray()

    # srs_projt = srs_proj.ExportToWkt()

    ref_data = gdal.Open(reference_raster, GA_ReadOnly)
    ref_proj = ref_data.GetProjection()
    ref_geotrs = ref_data.GetGeoTransform()
    Ncols = ref_data.RasterXSize
    Nrows = ref_data.RasterYSize
    ref_band = ref_data.GetRasterBand(1)
    varref = ref_band.ReadAsArray()
    ref_data = None

    out_data = gdal.GetDriverByName('GTiff').Create(output_raster, Ncols, Nrows, 1, gdal.GDT_Float32)
    out_data.SetGeoTransform(ref_geotrs)
    out_data.SetProjection(ref_proj)
    outband = out_data.GetRasterBand(1)
    out_array = varref - varin
    outband.WriteArray(out_array)
    outband.FlushCache()

    srs_data = None
    out_data = None

    retDictionary = {'success': "True", 'message': "get difference of raster was successful"}
    # print()
    return retDictionary

def adjust_for_elevation_Forcing(input_netcdf, output_netcdf, varName, input_raster, target_raster,
                                 time_var_name='time', baseDateTime='2008/10/01 0', timeUnits='hours', varCode= 'temp'):
    """
    adjusts for elevation based on specified var name
    :param input_netcdf: input
    :param output_netcdf: output
    :param varName: name of variable of interest
    :param input_raster: raster containing the DEM values used when generating the original climate data (in input_netcdf)
    :param target_raster: temperature values adjusted to this DEM
    :return:
    """
    if(varCode == 'temp'):
        retDictionary = adjust_for_elevation_Temperature(input_netcdf=input_netcdf, output_netcdf=output_netcdf, varName=varName,
                                         input_raster=input_raster, target_raster=target_raster, time_var_name=time_var_name,
                                         baseDateTime=baseDateTime, timeUnits=timeUnits)
    elif(varCode == 'prec'):
            retDictionary = adjust_for_elevation_Precipitation(input_netcdf=input_netcdf, output_netcdf=output_netcdf, varName=varName,
                                             input_raster=input_raster, target_raster=target_raster,
                                             time_var_name=time_var_name,
                                             baseDateTime=baseDateTime, timeUnits=timeUnits)
    elif(varCode == 'vp'):
            retDictionary = adjust_for_elevation_VaporPressure(input_netcdf=input_netcdf, output_netcdf=output_netcdf, varName=varName,
                                             input_raster=input_raster, target_raster=target_raster,
                                             time_var_name=time_var_name,
                                             baseDateTime=baseDateTime, timeUnits=timeUnits)
    else:
        logger.info("Error elevation adjustment; wrong variable specier; must be 'temp', 'prec', or 'vp' ")
        retDictionary = {'success': "False", 'message': " Error elevation adjustment; wrong variable specier; must be 'temp', 'prec', or 'vp' "}


    return retDictionary


def adjust_for_elevation_Temperature(input_netcdf, output_netcdf, varName, input_raster, target_raster, time_var_name='time', baseDateTime='1980/01/01 0', timeUnits='days'):
    """
    ajusts temerature values with lapse rate based on elevaton
    :param input_netcdf: input
    :param output_netcdf: output
    :param varName: name of variable of interest
    :param input_raster: raster containing the DEM values used when generating the original climate data (in input_netcdf)
    :param target_raster: temperature values adjusted to this DEM
    :return:
    """
    # lapse rates, monthly   ToDo: check values
    lapserateT = [0.0044,0.0059,0.0071,0.0078,0.0081,0.0082,0.0081,0.0081,0.0077,0.0068,0.0055,0.0047]

    #copy variables and attriutes to output netcdf
    cmdString = "nccopy -k 3 "+input_netcdf+" "+output_netcdf
    retDictionary = call_subprocess(cmdString, 'copy netcdf')
    if retDictionary['success'] == "False":
        return retDictionary

    #create elevation difference dem raster
    dzDEM = os.path.join(os.path.dirname(output_netcdf),'dzDEM_temp.tif')
    #cmdString = "python gdal_calc.py -A " + input_raster + " -B " + target_raster + " --outfile=" + dzDEM + " --calc=B-A"
    #retDictionary = call_subprocess(cmdString, "compute elevation difference")\
    retDictionary = get_raster_Difference(input_raster, target_raster, dzDEM)
    if retDictionary['success'] == "False":
        return retDictionary

    #get value of dzDEM array
    ref_data = gdal.Open(dzDEM, GA_ReadOnly)
    inband = ref_data.GetRasterBand(1)
    #nodata = inband.GetNoDataValue()
    dzDEMArray = inband.ReadAsArray()
    dzDEMArrayout = dzDEMArray[::-1]         # 8.12.15 gdal and netcdf4 have arrays in opposite directions
    #dType = inband.DataType
    ref_data = None

    #Open file to write re-gridded data
    ncOut = netCDF4.Dataset(output_netcdf,"r+") #, format='NETCDF4')
    xout = ncOut.variables['x'][:]
    yout = ncOut.variables['y'][:]
    vardataType = ncOut.variables[varName].datatype
    varin = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    varout = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    timeLen = len(ncOut.dimensions['time'])
    tArray = ncOut.variables[time_var_name][:]
    yLen = len(yout)
    xLen = len(xout)
    for tk in range(timeLen):
        varin[:,:] = ncOut.variables[varName][tk,:,:]
        if timeUnits == 'days':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(days=int(tArray[tk]))
        elif timeUnits == 'hours':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(hours=int(tArray[tk]))
        else:
            logger.info("Erroneous time unit")
            retDictionary = {'success': "False", 'message': "Erroneous time unit"}
            #print()
            return retDictionary
        monthtk = int(dateTimetk.month - 1)
        #for yi in range(yLen):
        #    for xj in range(xLen):
        #       varout[yi,xj] = varin[yi,xj] - (dzDEMArrayout[yi,xj] * lapserateT[monthtk])  # bilinear_interpolation(yout[yi],xout[xj],points)
        varout = varin - (dzDEMArrayout* lapserateT[monthtk])  # bilinear_interpolation(yout[yi],xout[xj],points)
        ncOut.variables[varName][tk,:,:] = varout[:,:]

    ncOut.close()

    logger.info("Success elevation adjustment Temperature")
    retDictionary = {'success': "True", 'message': " Done temperature elevation adjustment"}

    return retDictionary


def adjust_for_elevation_Precipitation(input_netcdf, output_netcdf, varName, input_raster, target_raster, time_var_name='time', baseDateTime='2008/10/01 0', timeUnits='hours'):
    """
    ajusts temerature values with lapse rate based on elevaton
    :param input_netcdf: input
    :param output_netcdf: output
    :param varName: name of variable of interest
    :param input_raster: raster containing the DEM values used when generating the original climate data (in input_netcdf)
    :param target_raster: temperature values adjusted to this DEM
    :return:
    """
    # precipitaiton adjustment factor, monthly, from Listen and Eleder 2006   ToDo: check values
    Xp = [0.00035,0.00035,0.00035,0.0003,0.00025,0.0002,0.0002,0.0002,0.0002,0.00025,0.0003,0.00035]

    #copy variables and attriutes to output netcdf
    cmdString = "nccopy -k 3 "+input_netcdf+" "+output_netcdf
    callSubprocess(cmdString, 'copy netcdf')

    #create elevation difference dem raster
    dzDEM = os.path.join(os.path.dirname(output_netcdf),'dzDEM_temp.tif')
    #cmdString = "python gdal_calc.py -A " + input_raster + " -B " + target_raster + " --outfile=" + dzDEM + " --calc=B-A"
    #retDictionary = call_subprocess(cmdString, "compute elevation difference")\
    retDictionary = get_raster_Difference(input_raster, target_raster, dzDEM)
    if retDictionary['success'] == "False":
        return retDictionary


    #get value of dzDEM array
    ref_data = gdal.Open(dzDEM, GA_ReadOnly)
    inband = ref_data.GetRasterBand(1)
    #nodata = inband.GetNoDataValue()
    dzDEMArray = inband.ReadAsArray()
    dzDEMArrayout = dzDEMArray[::-1]         # 8.12.15 gdal and netcdf4 have arrays in opposite directions
    #dType = inband.DataType
    ref_data = None

    #Open file to write re-gridded data
    ncOut = netCDF4.Dataset(output_netcdf,"r+") #, format='NETCDF4')
    xout = ncOut.variables['x'][:]
    yout = ncOut.variables['y'][:]
    vardataType = ncOut.variables[varName].datatype
    varin = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    varout = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    timeLen = len(ncOut.dimensions['time'])
    tArray = ncOut.variables[time_var_name][:]
    yLen = len(yout)
    xLen = len(xout)
    for tk in range(timeLen):
        varin[:,:] = ncOut.variables[varName][tk,:,:]
        if timeUnits == 'days':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(days=int(tArray[tk]))
        elif timeUnits == 'hours':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(hours=int(tArray[tk]))
        else:
            logger.info("Erroneous time unit")
            retDictionary = {'success': "False", 'message': "Erroneous time unit"}
            #print()
            return retDictionary
        monthtk = int(dateTimetk.month - 1)

        varout = varin*(1 + Xp[monthtk]*dzDEMArrayout)/(1 - Xp[monthtk]*dzDEMArray)  # bilinear_interpolation(yout[yi],xout[xj],points)
        ncOut.variables[varName][tk,:,:] = varout[:,:]

    ncOut.close()

    logger.info("Success elevation adjustment Precipitation")
    retDictionary = {'success': "True", 'message': " Done precipitation elevation adjustment"}

    return retDictionary


def adjust_for_elevation_VaporPressure(input_netcdf, output_netcdf, varName, input_raster, target_raster, time_var_name='time', baseDateTime='2008/10/01 0', timeUnits='hours'):
    """
    adjusts values with lapse rate based on elevaton
    :param input_netcdf: input
    :param output_netcdf: output
    :param varName: name of variable of interest
    :param input_raster: raster containing the DEM values used when generating the original climate data (in input_netcdf)
    :param target_raster: temperature values adjusted to this DEM
    :return:
    """
    # lapse rates, monthly ToDo: check values
    lapserateTd = [0.00041,0.00042,0.00040,0.00039,0.00038,0.00036,0.00033,0.00033,0.00036,0.00037,0.00040,0.00040]
    a=611.21
    b=22.452
    c=240.97

    #copy variables and attriutes to output netcdf
    cmdString = "ncea -4 -h -O "+input_netcdf+" "+output_netcdf
    callSubprocess(cmdString, 'copy netcdf')

    #create elevation difference dem raster
    dzDEM = os.path.join(os.path.dirname(output_netcdf),'dzDEM_temp.tif')
    #cmdString = "python gdal_calc.py -A " + input_raster + " -B " + target_raster + " --outfile=" + dzDEM + " --calc=B-A"
    #retDictionary = call_subprocess(cmdString, "compute elevation difference")\
    retDictionary = get_raster_Difference(input_raster, target_raster, dzDEM)
    if retDictionary['success'] == "False":
        return retDictionary

    #get value of dzDEM array
    ref_data = gdal.Open(dzDEM, GA_ReadOnly)
    inband = ref_data.GetRasterBand(1)
    #nodata = inband.GetNoDataValue()
    dzDEMArray = inband.ReadAsArray()
    dzDEMArrayout = dzDEMArray[::-1]         # 8.12.15 gdal and netcdf4 have arrays in opposite directions
    #dType = inband.DataType
    ref_data = None

    #Open file to write re-gridded data
    ncOut = netCDF4.Dataset(output_netcdf,"r+") #, format='NETCDF4')
    xout = ncOut.variables['x'][:]
    yout = ncOut.variables['y'][:]
    vardataType = ncOut.variables[varName].datatype
    varin = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    varout = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    timeLen = len(ncOut.dimensions['time'])
    tArray = ncOut.variables[time_var_name][:]
    yLen = len(yout)
    xLen = len(xout)
    counterErr = 0
    for tk in range(timeLen):
        varin[:,:] = ncOut.variables[varName][tk,:,:]
        if timeUnits == 'days':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(days=int(tArray[tk]))
        elif timeUnits == 'hours':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(hours=int(tArray[tk]))
        else:
            logger.info("Erroneous time unit")
            retDictionary = {'success': "False", 'message': "Erroneous time unit"}
            #print()
            return retDictionary
        monthtk = int(dateTimetk.month - 1)
        for yi in range(yLen):
            for xj in range(xLen):
                if varin[yi,xj] <= 0:
                    Tdold = -40                       # assume the lowest possible temp -40 # ToDO: may be it is better to use missing-value?
                    counterErr =+1
                    print(" 0 or negative VP at time step %d ,cell %d %d  ,value = %f"%(tk, yi, xj, varin[yi,xj]))
                else:
                    Tdold = (c * math.log(varin[yi,xj]/a)) / ( b - math.log(varin[yi,xj]/a) )
                Tdnew  = Tdold - ((c * dzDEMArrayout[yi,xj] * lapserateTd[monthtk]) / b )
                varout[yi,xj] = a * math.exp((b * Tdnew)/(c + Tdnew))
        ncOut.variables[varName][tk,:,:] = varout[:,:]

    ncOut.close()

    # print("0 or negative VP occured %d times" %counterErr)
    logger.info("Success elevation adjustment Vapor pressure, 0 or negative VP occured %d times" %counterErr)
    retDictionary = {'success': "True", 'message': " Done vapor pressure elevation adjustment"}
    return retDictionary


#This uses P = P0*((T0 + lambda*dz)/T0)^(-g/lambda*R)
def adjust_for_elevation_SurfaceAirPressure(input_netcdfP,  varNameP, input_netcdfT,  varNameT, output_netcdf, input_raster, target_raster, time_var_name='time', baseDateTime='1980/01/01 0', timeUnits='days'):
    """
    ajusts temerature values with lapse rate based on elevaton
    :param input_netcdf: input
    :param output_netcdf: output
    :param varName: name of variable of interest
    :param input_raster: raster containing the DEM values used when generating the original climate data (in input_netcdf)
    :param target_raster: temperature values adjusted to this DEM
    :return:
    """
    # lapse rates, monthly   ToDo: check values
    lapserateT = [0.0044,0.0059,0.0071,0.0078,0.0081,0.0082,0.0081,0.0081,0.0077,0.0068,0.0055,0.0047]
    grav = 9.81        # m/s^2
    Rgas = 287.04      # J/kg-k

    #copy variables and attriutes to output netcdf
    cmdString = "nccopy -k 3 "+input_netcdfP+" "+output_netcdf
    callSubprocess(cmdString, 'copy netcdf')

    #create elevation difference dem raster
    dzDEM = os.path.join(os.path.dirname(output_netcdf),'dzDEM_temp.tif')
    #cmdString = "python gdal_calc.py -A " + input_raster + " -B " + target_raster + " --outfile=" + dzDEM + " --calc=B-A"
    #retDictionary = call_subprocess(cmdString, "compute elevation difference")\
    retDictionary = get_raster_Difference(input_raster, target_raster, dzDEM)
    if retDictionary['success'] == "False":
        return retDictionary

    #get value of dzDEM array
    ref_data = gdal.Open(dzDEM, GA_ReadOnly)
    inband = ref_data.GetRasterBand(1)
    #nodata = inband.GetNoDataValue()
    dzDEMArray = inband.ReadAsArray()
    dzDEMArrayout = dzDEMArray[::-1]         # 8.12.15 gdal and netcdf4 have arrays in opposite directions
    #dType = inband.DataType
    ref_data = None

    #Open file to write re-gridded data
    ncOut = netCDF4.Dataset(output_netcdf,"r+") #, format='NETCDF4')
    xout = ncOut.variables['x'][:]
    yout = ncOut.variables['y'][:]
    vardataType = ncOut.variables[varNameP].datatype
    varin = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    varout = numpy.zeros((len(yout),len(xout)),dtype=vardataType)
    timeLen = len(ncOut.dimensions['time'])
    tArray = ncOut.variables[time_var_name][:]
    yLen = len(yout)
    xLen = len(xout)

    ncInT = netCDF4.Dataset(input_netcdfT,"r") # format='NETCDF4')
    for tk in range(timeLen):
        varin[:,:] = ncOut.variables[varNameP][tk,:,:]
        varinT = ncInT.variables[varNameT][tk,:,:]
        if timeUnits == 'days':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(days=int(tArray[tk]))
        elif timeUnits == 'hours':
            dateTimetk = datetime.strptime(baseDateTime,"%Y/%m/%d %H") + timedelta(hours=int(tArray[tk]))
        else:
            logger.info("Erroneous time unit")
            retDictionary = {'success': "False", 'message': "Erroneous time unit"}
            #print()
            return retDictionary
        monthtk = int(dateTimetk.month - 1)
        #for yi in range(yLen):
        #    for xj in range(xLen):
        #       varout[yi,xj] = varin[yi,xj] - (dzDEMArrayout[yi,xj] * lapserateT[monthtk])  # bilinear_interpolation(yout[yi],xout[xj],points)
        varout = varin* math.pow((((varinT+273.16) + dzDEMArrayout*-1*lapserateT[monthtk])/(varinT+273.16)),(-1*grav/(Rgas*-1*lapserateT[monthtk])))     #T in oC and lapserrate +ve
        ncOut.variables[varNameP][tk,:,:] = varout[:,:]

    ncOut.close()

    logger.info("Success elevation adjustment Surface pressure")
    retDictionary = {'success': "True", 'message': " Done surface pressure elevation adjustment"}
    return retDictionary


