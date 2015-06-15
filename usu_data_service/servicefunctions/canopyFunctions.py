try:
    from osgeo import gdal, osr,ogr
except:
    import gdal, osr, ogr
from gdalconst import *
import shlex
import subprocess
import os
import numpy

def project_and_clip_raster(input_raster, reference_raster, output_raster):    # resample='near'):
    """
    :param input_raster:
    :param reference_raster:
    :param output_raster:
    :return:
    For images leave the default nearest neighbor interpolation; else pass the method required
    """
    srs_data = gdal.Open(input_raster, GA_ReadOnly)
    srs_proj = srs_data.GetProjection() #osr.SpatialReference(wkt
    srs_geotrans = srs_data.GetGeoTransform()

    ref_data = gdal.Open(reference_raster, GA_ReadOnly)
    ref_proj = ref_data.GetProjection()
    ref_geotrs = ref_data.GetGeoTransform()
    Ncols = ref_data.RasterXSize
    Nrows = ref_data.RasterYSize

    out_data = gdal.GetDriverByName('GTiff').Create(output_raster, Ncols, Nrows, 1, GDT_Byte)
    out_data.SetGeoTransform(ref_geotrs)
    out_data.SetProjection(ref_proj)

    gdal.ReprojectImage(srs_data,out_data,srs_proj,ref_proj, GRA_NearestNeighbour)
    del out_data
    response_dict = {'success': 'True', 'message': 'Raster projection/clipping was successful'}
    return response_dict


def projectAndClipRaster2(input_raster, reference_raster, output_raster, resample='near'):
    """
    :param input_raster:
    :param reference_raster:
    :param output_raster:
    :return:
    For images leave the default nearest neighbor interpolation; else pass the method required

    The target extent parameters -te xmin ymin xmax ymax  may be needed to provide a
    region where the destination projection is valid
    projecting a large dataset (e.g. CONUS) into local projections (e.g. NAD 12N) may fail
    because gdal checks the validity of the projection method for the entire region
    """
    data_set = gdal.Open(input_raster)
    target_srs = data_set.GetProjection() #osr.SpatialReference(wkt
    #target_srs.ImportFromWkt(data_set.GetPrjectionRef())
    data_set = None
    srsprjFile = 'srsprj.prf'
    prjFilep = open(srsprjFile,'w')
    prjFilep.write(target_srs)
    prjFilep.close()

    data_set = gdal.Open(reference_raster)
    target_srs = data_set.GetProjection() #osr.SpatialReference(wkt
    geo_transform = data_set.GetGeoTransform()
    dx = geo_transform[1]
    dy = geo_transform[5]
    xmin = geo_transform[0]
    ymax = geo_transform[3]
    xmax = xmin + dx * data_set.RasterXSize
    ymin = ymax + dy* data_set.RasterYSize
    data_set = None
    tprjFile = 'destprj.prf'
    prjFilep = open(tprjFile,'w')
    prjFilep.write(target_srs)
    prjFilep.close()

    cmdString = "gdalwarp -s_srs "+srsprjFile+" -t_srs "+tprjFile+" -te "\
                +str(xmin)+" "+str(ymin)+" "+str(xmax)+" "+str(ymax)+" -tr "\
                +str(dx)+" "+str(-1*dy)+" -r "+resample+" -overwrite "+input_raster+" "+output_raster
    callSubprocess(cmdString, "project and clip Raster")


def get_canopy_variables(in_NLCDraster, out_ccNetCDF, out_hcanNetCDF, out_laiNetCDF):

    srs_data = gdal.Open(in_NLCDraster, GA_ReadOnly)
    srs_proj = srs_data.GetProjection()
    srs_geotrans = srs_data.GetGeoTransform()
    Ncols = srs_data.RasterXSize
    Nrows = srs_data.RasterYSize
    in_band1 = srs_data.GetRasterBand(1)
    tempArray = in_band1.ReadAsArray()
    #formats 'GTiff' 'NetCDF', ..
    out_data1 = gdal.GetDriverByName('NetCDF').Create(out_ccNetCDF, Ncols, Nrows, 1, GDT_Float32)
    out_data1.SetGeoTransform(srs_geotrans)
    out_data1.SetProjection(srs_proj)
    out_data2 = gdal.GetDriverByName('NetCDF').Create(out_hcanNetCDF, Ncols, Nrows, 1, GDT_Float32)
    out_data2.SetGeoTransform(srs_geotrans)
    out_data2.SetProjection(srs_proj)
    out_data3 = gdal.GetDriverByName('NetCDF').Create(out_laiNetCDF, Ncols, Nrows, 1, GDT_Float32)
    out_data3.SetGeoTransform(srs_geotrans)
    out_data3.SetProjection(srs_proj)

    outArray1 = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    outArray2 = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    outArray3 = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    #outArray[tempArray!=41 and tempArray!=42 and tempArray !=43 and tempArray !=52 and tempArray != 90] = 0
    #-> The following is bit slow; need to find a way to change values at specific index locations
    for i in range(len(tempArray)):
        for j in range(len(tempArray[i])):
            val = tempArray[i][j]
            if val == 41 or val == 90:
                outArray1[i][j] = 0.5
                outArray2[i][j] = 8.0
                outArray3[i][j] = 1.0
            elif val == 42:
                outArray1[i][j] = 0.7
                outArray2[i][j] = 15.0
                outArray3[i][j] = 4.5
            elif val == 43:
                outArray1[i][j] = 0.8
                outArray2[i][j] = 10.0
                outArray3[i][j] = 4.0
            elif val == 52:
                outArray1[i][j] = 0.5
                outArray2[i][j] = 3.0
                outArray3[i][j] = 1.0
            else:
                outArray1[i][j] = 0.0
                outArray2[i][j] = 0.0
                outArray3[i][j] = 0.0

    out_band1 = out_data1.GetRasterBand(1)
    out_band1.WriteArray(outArray1)
    out_band1.FlushCache()
    out_band2 = out_data2.GetRasterBand(1)
    out_band2.WriteArray(outArray2)
    out_band2.FlushCache()
    out_band3 = out_data3.GetRasterBand(1)
    out_band3.WriteArray(outArray3)
    out_band3.FlushCache()

    response_dict = {'success': 'True', 'message': 'Generated netCDF files with data for canopy variables'}
    return response_dict

def get_canopy_variable(in_NLCDraster, output_netcdf, variable_name):

    if variable_name not in ('cc', 'hcan', 'lai'):
        response_dict = {'success': 'False', 'message': 'Invalid canopy variable name:%s' % variable_name}
        return response_dict

    srs_data = gdal.Open(in_NLCDraster, GA_ReadOnly)
    srs_proj = srs_data.GetProjection()
    srs_geotrans = srs_data.GetGeoTransform()
    Ncols = srs_data.RasterXSize
    Nrows = srs_data.RasterYSize
    in_band1 = srs_data.GetRasterBand(1)
    tempArray = in_band1.ReadAsArray()
    #formats 'GTiff' 'NetCDF', ..
    out_data = gdal.GetDriverByName('NetCDF').Create(output_netcdf, Ncols, Nrows, 1, GDT_Float32)
    out_data.SetGeoTransform(srs_geotrans)
    out_data.SetProjection(srs_proj)
    # out_data2 = gdal.GetDriverByName('NetCDF').Create(out_hcanNetCDF, Ncols, Nrows, 1, GDT_Float32)
    # out_data2.SetGeoTransform(srs_geotrans)
    # out_data2.SetProjection(srs_proj)
    # out_data3 = gdal.GetDriverByName('NetCDF').Create(out_laiNetCDF, Ncols, Nrows, 1, GDT_Float32)
    # out_data3.SetGeoTransform(srs_geotrans)
    # out_data3.SetProjection(srs_proj)

    outArray = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    # outArray2 = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    # outArray3 = numpy.array([([0.0]* len(tempArray[0])) for i in range(len(tempArray))])
    #outArray[tempArray!=41 and tempArray!=42 and tempArray !=43 and tempArray !=52 and tempArray != 90] = 0
    #-> The following is bit slow; need to find a way to change values at specific index locations
    for i in range(len(tempArray)):
        for j in range(len(tempArray[i])):
            val = tempArray[i][j]
            if val == 41 or val == 90:
                if variable_name == 'cc':
                    outArray[i][j] = 0.5
                elif variable_name == 'hcan':
                    outArray[i][j] = 8.0
                else:
                    outArray[i][j] = 1.0
            elif val == 42:
                if variable_name == 'cc':
                    outArray[i][j] = 0.7
                elif variable_name == 'hcan':
                    outArray[i][j] = 15.0
                else:
                    outArray[i][j] = 4.5
            elif val == 43:
                if variable_name == 'cc':
                    outArray[i][j] = 0.8
                elif variable_name == 'hcan':
                    outArray[i][j] = 10.0
                else:
                    outArray[i][j] = 4.0
            elif val == 52:
                if variable_name == 'cc':
                    outArray[i][j] = 0.5
                elif variable_name == 'hcan':
                    outArray[i][j] = 3.0
                else:
                    outArray[i][j] = 1.0
            else:
                outArray[i][j] = 0.0
                # outArray2[i][j] = 0.0
                # outArray3[i][j] = 0.0

    out_band = out_data.GetRasterBand(1)
    out_band.WriteArray(outArray)
    out_band.FlushCache()
    # out_band2 = out_data2.GetRasterBand(1)
    # out_band2.WriteArray(outArray2)
    # out_band2.FlushCache()
    # out_band3 = out_data3.GetRasterBand(1)
    # out_band3.WriteArray(outArray3)
    # out_band3.FlushCache()

    response_dict = {'success': 'True', 'message': 'Generated netCDF files with data for canopy variable:%s' % variable_name}
    return response_dict

def getCanopyLAI(input_NLCDF_raster, input_watershed_raster, output_lai_netcdf):
    pass


def getCanopyHeight(input_NLCD_raster, input_watershed_raster, output_hcan_netcdf):
    pass


def rasterInfo(raster_src):
    raster_src = os.path.abspath(os.path.join(os.getcwd(), raster_src))
    data_set = gdal.Open(raster_src, GA_ReadOnly)
    geo_transform = data_set.GetGeoTransform()
    # use ulx uly lrx lry
    xmin = geo_transform[0]
    ymax = geo_transform[3]
    dx = geo_transform[1]
    dy = geo_transform[5]
    xmax = xmin + dx * data_set.RasterXSize
    ymin = ymax + dy* data_set.RasterYSize
    print ('number of columns: ', data_set.RasterXSize)
    print ('number of rows: ', data_set.RasterYSize)
    print ('xmin: ', xmin)
    print ('ymax: ', ymax)
    print ('dx: ', dx)
    print ('dy: ', dy)
    print ('xmax: ', xmax)
    print ('ymin: ', ymin)
    print ('')
    data_set = None


def getRasterSubset(input_raster, output_raster, xmin, ymax, xmax, ymin):
    #parameters are ulx uly lrx lry
    """ To Do: Boundary check-> check if the bounding box of subset raster is
               within the input_raster's boundary

    Note: upper left (ul) considered origin, i.e. xmin, ymax
    parameters passed as ulx uly lrx lry
    """
    cmdString = "gdal_translate"+" "+"-projwin"+" "+xmin+" "+ymax+" "\
               +xmax+" "+ymin+" "+input_raster+" "+output_raster
    callSubprocess(cmdString)



# def getRasterSubset(input_raster, output_raster, reference_Raster):
#     """ To Do: Boundary check-> check if the bounding box of subset raster is
#                within the input_raster's boundary
#
#     Boundary parameters extracted from reference_Raster
#     """
#     data_set = gdal.Open(reference_Raster, GA_ReadOnly)
#     geo_transform = data_set.GetGeoTransform()
#     # use ulx uly lrx lry
#     xmin = geo_transform[0]
#     ymax = geo_transform[3]
#     dx = geo_transform[1]
#     dy = geo_transform[5]
#     xmax = xmin + dx * data_set.RasterXSize
#     ymin = ymax + dy* data_set.RasterYSize          # dy is -ve
#
#     cmdString = "gdal_translate"+" "+"-projwin"+" "+xmin+" "+ymax+" "\
#                +xmax+" "+ymin+" "+input_raster+" "+output_raster
#     callSubprocess(cmdString)
#
#     data_set = None


def callSubprocess(cmdString, debugString):
    cmdargs = shlex.split(cmdString)
    debFile = open('debug_file.txt', 'w')
    debFile.write('Starting %s \n' % debugString)
    retValue = subprocess.call(cmdargs,stdout=debFile)
    if (retValue==0):
        debFile.write('%s Successful\n' % debugString)
        debFile.close()
    else:
        debFile.write('There was error in %s\n' % debugString)
        debFile.close()

# def rasterToNetCDF(input_raster, output_netcdf):
#     cmdString = "gdal_translate -of netCDF "+input_raster+" "+output_netcdf
#     callSubprocess(cmdString, 'raster to netcdf')


# def combineRasters(input_raster1, input_raster2, output_raster):
#     """To  Do: may need to specify output no-data value
#     """
#     cmdString = "gdalwarp "+input_raster1+" "+input_raster2+" "+output_raster
#     callSubprocess(cmdString, 'join (stitch) two raster files')


# def uncompressRaster(input_raster, output_raster):
#     """TauDEM doesn't take compressed file; uncompress file
#         ToDO:  Check compression first"""
#     cmdString = "gdal_translate -co COMPRESS=NONE"+" "\
#                +input_raster+" "+output_raster
#     callSubprocess(cmdString, 'uncompress raster')
