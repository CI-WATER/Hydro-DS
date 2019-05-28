__author__ = 'tsega'
#from hydrods_python_client import HydroDS
from hydrods_python_client_unified import HydroDS
import settings
from datetime import datetime, timedelta
"""*********** Input settings for watershed of interest *****************"""
workingDir = "G:/workDir/HydroDSTest/"

# Green River near Daniel at Warren Bridge
#leftX, topY, rightX, bottomY =  -110.415, 43.593, -109.492, 42.871
#Logan River above First Dam
leftX, topY, rightX, bottomY = -111.8037, 42.1248, -111.4255, 41.6946

#Green River near Daniel at Warren Bridge
#lat_outlet, lon_outlet = 4763468.844081, 572625.265184
#lat_outlet, lon_outlet = 43.019338, -110.118234
# Logan outlet at First dam
lat_outlet, lon_outlet = 41.7436,  -111.7838        #Logan

# Grid projection
#utmZone = int((180 + 0.5*(xmin+xmax))/6) + 1
epsgCode = 26912        #4326     #    #26912                 #26912 utm 12
dx,dy  = 30, 30  #  Grid cell sizes (m) for reprojection
# Set parameters for watershed delineation
streamThreshold = 1000
watershedName = 'GreenT'
# Cell spacing for subsampled UEB model (m)
dxRes, dyRes = 800, 800
#### model start and end dates

#startDateTime = "2010/10/01 0"
#endDateTime = "2011/10/01 0"
startDateTime = "2008/10/01 0"
endDateTime = "2009/10/01 0"

inTime = 'time'
"""*************************************************************************"""
HDS = HydroDS(username=settings.USER_NAME, password=settings.PASSWORD)

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

#usgs download subset
#leftX, topY, rightX, bottomY = -111.0, 41.0, -111.0, 41.0
downRequest = HDS.subset_usgs_ned_dem(left=leftX, top=topY, right=rightX, bottom=bottomY, output_raster="LoganUSGSDEM.tif")

MyFiles = HDS.list_my_files()
for item in MyFiles:
    print(item)

print('Done')




