try:
    from osgeo import gdal, osr, ogr
except:
    import gdal, osr, ogr
from gdalconst import *
import shlex
import subprocess
import os
from datetime import datetime
import numpy


#The following functions will download daymet mosaic or tile datasets for the years range passed
#The mosaic files are each for the entire CONUS for each year
#be aware of large files; and the process can be time consuming
# based on code at http://daymet.ornl.gov/files/daymet_mosaic-nc-retrieval_07012014.txt
# and http://daymet.ornl.gov/files/daymet_tile-nc-retrieval_07012014.txt

climate_Vars = ['vp', 'tmin', 'tmax', 'swe', 'srad', 'prcp', 'dayl']
mosaicString = "wget --limit-rate=50m http://thredds.daac.ornl.gov/thredds/fileServer/ornldaac/1219/"

def downloadDayMetMosaic(prefixpath, startYear, endYear):
    for var in climate_Vars:
        for year in range(startYear, endYear+1):
            cmdString = mosaicString+str(year)+"/"+var+"_"+str(year)+".nc4 -O " +prefixpath+var+"_"+str(year)+".nc4"
            callSubprocess(cmdString, "download Daymet Mosaic")


#If the tile number of area of interest is known this would reduce the size of file downloaded
def downloadDayMetTile(prefixpath, startYear, endYear, startTile, endTile):
    for var in climate_Vars:
        for year in range(startYear, endYear+1):
            for tile in range(startTile, endTile+1):
                cmdString = mosaicString+"tiles/"+str(year)+"/"+str(tile)+"_"+str(year)+"/"\
                            +var+".nc -O "+prefixpath+var+"_"+str(year)+"_"+str(tile)+".nc"
                callSubprocess(cmdString, "download Daymet tile")


#This concatenates netcdf files along the time dimension
def concatenateNetCDFs(input_netcdf1, input_netcdf2, output_netcdf):
    """To  Do: may need to specify output no-data value
    """
    cmdString = "ncks --mk_rec_dmn time "+input_netcdf1+" tempNetCDF1.nc"
    callSubprocess(cmdString, "intermediate netcdf with record dimension")
    cmdString = "ncks --mk_rec_dmn time "+input_netcdf2+" tempNetCDF2.nc"
    callSubprocess(cmdString, "intermediate netcdf with record dimension")
    #
    cmdString = "ncrcat tempNetCDF1.nc tempNetCDF2.nc "+output_netcdf
    callSubprocess(cmdString, "concatenate netcdf files")
    #delete intermediate files
    os.remove('tempNetCDF1.nc')
    os.remove('tempNetCDF2.nc')



def subset_NLDAS_forcing(output_netcdf, leftX, topY, rightX, bottomY,
                      startDateTime, endDateTime, dT=1, in_Xcoord = 'lon_110', in_Ycoord='lat_110',inout_timeName = 'time'):

    """
    Subsets and combines multiple netcdf files
    for nldas forcing, with multiple time steps (e.g., organized in monthly files)
    should already have time dim. for ncrcat, made record dim by ncks
    e.g.:
    Logan leftX=-112.0, topY=42.3, rightX=-111.0, bottomY=41.6, startYear=2009, endYear=2010
    for nldas data with time dim (e.g., previously concatenated in time dim)
    """
    startYear = datetime.strptime(startDateTime,"%Y/%m/%d %H").year
    endYear = datetime.strptime(endDateTime,"%Y/%m/%d %H").year
    startMonth = datetime.strptime(startDateTime,"%Y/%m/%d %H").month
    endMonth = datetime.strptime(endDateTime,"%Y/%m/%d %H").month
    startDay =  datetime.strptime(startDateTime,"%Y/%m/%d %H").timetuple().tm_yday        #start date = day of year for 2010
    endDay   =  startDay + (datetime.strptime(endDateTime,"%Y/%m/%d %H") - datetime.strptime(startDateTime,"%Y/%m/%d %H")).days          # end date = day of year for 2011 + 365

    #print(startYear)
    #print(endYear)

    file_prefix = 'NLDAS_FORA0125_H.A_Monthly'
    wsName = 'watershed'

    for year in range(startYear, endYear+1):
        for month in range(1, 13):
            if month < 10:
                monthS = '0'+str(month)
            else:
                monthS = str(month)
            cmdString = "for i in "+file_prefix+"*"+str(year)+monthS+"*.nc; do ncea -d "+in_Xcoord+","+str(leftX)+","+str(rightX)\
                    +" -d "+in_Ycoord+","+str(bottomY)+","+str(topY)+" -O $i "+wsName+"_$i; done"      #+subdir+"\/"
            callSubprocess(cmdString, 'subset nc files for year '+str(year))

    cmdString = "for i in "+wsName+"*.nc; do ncks --mk_rec_dmn "+inout_timeName+" -O $i R_$i; done"
    callSubprocess(cmdString, "intermediate netcdf with record dimension")


    cmdString = "ncrcat -4 -H -h -O  R_"+wsName+"*.nc -o concat_"+output_netcdf                     #-H don't append input file list -h don't append history
    callSubprocess(cmdString, "concatenate netcdf files")

    hD = int(24/dT)
    starttimeIndex = startDay * hD
    endtimeIndex = endDay * hD
    print(starttimeIndex)
    print(endtimeIndex)
    cmdString = "ncea -4 -H -O -d "+inout_timeName+","+str(starttimeIndex)+","+str(endtimeIndex)+" concat_"\
                 +output_netcdf+" "+output_netcdf
    callSubprocess(cmdString, 'subset netcdf in time')

    #delete intermediate files
    cmdString = "DEL "+"R_"+wsName+"*.nc"
    #callSubprocess(cmdString, "delete intermediate files")
    cmdString = "DEL "+wsName+"*.nc"
    #callSubprocess(cmdString, "delete intermediate files")
    #os.remove("R_*.nc")




#This combines (stitches) (spatially adjacent) netcdf files accross the spatial/horizontal dimensions
def combineNetCDFs(input_netcdf1, input_netcdf2, output_netcdf):
    """To  Do: may need to specify output no-data value
    """
    cmdString = "gdalwarp -of GTiff -overwrite "+input_netcdf1+" "+input_netcdf2+" tempRaster.tif"  #+output_raster
    callSubprocess(cmdString, "create intermediate raster file")
    #print 'done concatenating netcdfs'
    cmdString = "gdal_translate -of NetCDF tempRaster.tif "+output_netcdf
    callSubprocess(cmdString, "combine two netcdf files")
    #print 'done function'
    #delete intermediate file
    os.remove('tempRaster.tif')

#gets the subset of netcdf withing the reference raster
#values are resampled to the resolution of the reference raster
def projectAndClipNetCDF(input_netcdf, reference_raster, output_netcdf, resample='bilinear'):
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
    data_set = gdal.Open(input_netcdf)
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
                +str(dx)+" "+str(-1*dy)+" -r "+resample+" -overwrite "+input_netcdf+" tempraster.tif"        #+output_netcdf
    callSubprocess(cmdString, "create intermediate tiff file ")

    cmdString = "gdal_translate -of NetCDF tempraster.tif "+output_netcdf
    callSubprocess(cmdString, "project and clip NetCDF")
     #delete intermediate file
    os.remove('tempRaster.tif')


#this gives netcdf subset for reference_raster; to get the exact boundary of the
# rerence_raster, the input and reference must have same resolution
def getNetCDFSubset(input_netcdf, reference_Raster, output_netcdf):
    """ To Do: Boundary check-> check if the bounding box of subset raster is
               within the input_raster's boundary

    Boundary parameters extracted from reference_Raster
    """
    data_set = gdal.Open(reference_Raster, GA_ReadOnly)
    geo_transform = data_set.GetGeoTransform()
    # use ulx uly lrx lry
    xmin = geo_transform[0]
    ymax = geo_transform[3]
    dx = geo_transform[1]
    dy = geo_transform[5]
    xmax = xmin + dx * data_set.RasterXSize
    ymin = ymax + dy* data_set.RasterYSize          # dy is -ve

    cmdString = "ncea --flt -d y,"+str(ymin)+","+str(ymax)+" -d x,"+str(xmin)+","+str(xmax)+" "\
                 +input_netcdf+" "+output_netcdf
    callSubprocess(cmdString, 'subset netcdf')

    data_set = None


#This one works only for 2D; with 3D netcdf inputs it images of 2D, band1, band2,...
def projectAndClipNetCDF2D(input_netcdf, reference_raster, output_netcdf):    # resample='near'):
    """
    :param input_raster:
    :param reference_raster:
    :param output_raster:
    :return:
    For images leave the default nearest neighbor interpolation; else pass the method required
    """
    srs_data = gdal.Open(input_netcdf, GA_ReadOnly)
    srs_proj = srs_data.GetProjection() #osr.SpatialReference(wkt
    srs_geotrans = srs_data.GetGeoTransform()

    ref_data = gdal.Open(reference_raster, GA_ReadOnly)
    ref_proj = ref_data.GetProjection()
    ref_geotrs = ref_data.GetGeoTransform()
    Ncols = ref_data.RasterXSize
    Nrows = ref_data.RasterYSize

    out_data = gdal.GetDriverByName('NetCDF').Create(output_netcdf, Ncols, Nrows, 1, GDT_Byte)
    out_data.SetGeoTransform(ref_geotrs)
    out_data.SetProjection(ref_proj)

    gdal.ReprojectImage(srs_data,out_data,srs_proj,ref_proj, GRA_NearestNeighbour)
    del out_data


def getRasterSubset(input_raster, output_raster, reference_Raster):
    """ To Do: Boundary check-> check if the bounding box of subset raster is
               within the input_raster's boundary

    Boundary parameters extracted from reference_Raster
    """
    data_set = gdal.Open(reference_Raster, GA_ReadOnly)
    geo_transform = data_set.GetGeoTransform()
    # use ulx uly lrx lry
    xmin = geo_transform[0]
    ymax = geo_transform[3]
    dx = geo_transform[1]
    dy = geo_transform[5]
    xmax = xmin + dx * data_set.RasterXSize
    ymin = ymax + dy* data_set.RasterYSize          # dy is -ve

    cmdString = "gdal_translate"+" "+"-projwin"+" "+xmin+" "+ymax+" "\
               +xmax+" "+ymin+" "+input_raster+" "+output_raster
    callSubprocess(cmdString, 'subset raster')

    data_set = None


def combineRasters(input_raster1, input_raster2, output_raster):
    """To  Do: may need to specify output no-data value
    """
    cmdString = "gdalwarp "+input_raster1+" "+input_raster2+" "+output_raster
    callSubprocess(cmdString, 'join (stitch) two raster files')


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


def rasterToNetCDF(input_raster, output_netcdf):
    cmdString = "gdal_translate -of netCDF "+input_raster+" "+output_netcdf
    callSubprocess(cmdString, 'raster to netcdf')

