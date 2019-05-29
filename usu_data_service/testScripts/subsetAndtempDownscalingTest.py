__author__ = 'tsega'
#from hydrods_python_client import HydroDS
from hydrods_python_client_unified import HydroDS
import settings
from datetime import datetime, timedelta
"""*********** Input settings for watershed of interest *****************"""
workingDir = "G:/workDir/HydroDSTest/" #"/Projects/rdhmUEB/green2009/"

# Green River near Daniel at Warren Bridge
#leftX, topY, rightX, bottomY =  -110.415, 43.593, -109.492, 42.871
#Logan River above First Dam
#leftX, topY, rightX, bottomY = -111.8037, 42.1248, -111.4255, 41.6946
leftX, topY, rightX, bottomY = -111.91, 42.14, -111.27, 41.70

#Green River near Daniel at Warren Bridge
# Logan outlet at First dam
lat_outlet, lon_outlet = 41.7436,  -111.7838        #Logan

# Grid projection
#utmZone = int((180 + 0.5*(xmin+xmax))/6) + 1
epsgCode = 26912        #4326     #    #26912                 #26912 utm 12
dx,dy  = 30, 30  #  Grid cell sizes (m) for reprojection
# Set parameters for watershed delineation
streamThreshold = 1000
watershedName = 'Logan'
# Cell spacing for subsampled UEB model (m)
dxRes, dyRes = 800, 800
#### model start and end dates
startDateTime = "2008/10/01 0"
endDateTime = "2009/10/01 0"

inTime = 'time'
"""*************************************************************************"""
HDS = HydroDS(username=settings.USER_NAME, password=settings.PASSWORD)

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

input_netcdf='http://hydro-ds.uwrl.usu.edu/files/data/user_5/Logantmax0.nc'
target_raster='http://hydro-ds.uwrl.usu.edu/files/data/user_5/LoganNEDDEM.tif'

#### Subset DEM and Delineate Watershed
input_static_DEM  = 'daymetdemwgs84.tif'
subsetDEM_request = HDS.subset_raster(input_raster=input_static_DEM, left=leftX, top=topY, right=rightX,
                                      bottom=bottomY,output_raster=watershedName + 'DaymetDemWGS84.tif')

resProj_raster = HDS.project_resample_raster(input_raster_url_path=subsetDEM_request['output_raster'],
                                                      cell_size_dx=dxRes, cell_size_dy=dyRes, epsg_code=epsgCode,
                                                      output_raster=watershedName + 'DaymetDEM800mProjN.tif', resample='near')

input_raster = HDS.subset_raster_to_reference(input_raster_url_path=resProj_raster['output_raster'],
                                ref_raster_url_path=target_raster,
                                output_raster=watershedName + 'DaymetDEM800mN.tif')

#using general function for temp, prec, vp
wsRequest = HDS.adjust_for_elevation_Forcing(input_netcdf=input_netcdf,output_netcdf='LogantmaxDownscaled000.nc',varName='tmax',
                                                  input_raster=input_raster['output_raster'], target_raster=target_raster, varCode='temp')

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

print('Done')




