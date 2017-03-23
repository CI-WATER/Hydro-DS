import os,stat
import json
import zipfile
import shutil
import subprocess
from datetime import datetime
import functools

from django.contrib.auth.models import User
from time import sleep


from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic
from usu_data_service.utils import generate_uuid_file_path, delete_working_uuid_directory
from usu_data_service.servicefunctions.model_parameter_list import *
from usu_data_service.models import Job
from usu_data_service.servicefunctions.run_job import run_service, run_service_done


from usu_data_service.servicefunctions.terrainFunctions import get_raster_subset, project_shapefile_EPSG, \
    delineate_Watershed_atShapeFile, rasterToNetCDF, computeRasterAspect,computeRasterSlope
from usu_data_service.servicefunctions.watershedFunctions import project_and_resample_Raster_EPSG, \
    create_OutletShape_Wrapper, resample_Raster
from usu_data_service.servicefunctions.netcdfFunctions import netCDF_rename_variable, subset_netCDF_to_reference_raster, \
    concatenate_netCDF, get_netCDF_subset_TimeDim, project_subset_and_resample_netcdf_to_reference_netcdf, convert_netcdf_units
from usu_data_service.servicefunctions.canopyFunctions import project_and_clip_raster, get_canopy_variable
from usu_data_service.servicefunctions.gdal_calc import Calc   # remember to add this file
from usu_data_service.servicefunctions.epsg_list import EPSG_List  # remember to add this file


def run_create_ueb_input_job(request, **kwargs):

    job = None

    try:
        job = Job.objects.create(user=request.user,
                                 job_description="create ueb model input",
                                 status="Started",
                                 is_success=False,
                                 message='Job has been submitted for processing and not completed yet.',
                                 extra_data='HydroShare: ' + kwargs.get('hs_username') if kwargs.get('hs_username') else None)

        future = run_service(create_ueb_input, **kwargs)
        partial_run_service_done = functools.partial(run_service_done, job=job)
        future.add_done_callback(partial_run_service_done)

        return {'success': 'True',
                'message': 'The job has been submitted with job ID as {}'.format(job.id)
                }

    except Exception as e:
        if isinstance(job, Job):
            job.delete()

        return {'success': 'False',
                'error': ['The job submission is failed. Please try to submit the job again.']}


def create_ueb_input(hs_username=None, hs_password=None, hs_client_id=None,hs_client_secret=None, token=None,
                     topY=None, bottomY=None, leftX=None, rightX=None,
                     lat_outlet=None, lon_outlet=None, streamThreshold=1000, watershedName=None,
                     usic=None, wsic=None, tic=None, wcic=None, ts_last=None,
                     epsgCode=None, startDateTime=None, endDateTime=None, dx=None, dy=None,
                      dxRes=None, dyRes=None, res_title=None, res_keywords=None,
                      **kwargs):
     #TODO: remember to change the workspace folder in hydrods with access right chmod -R 0777 /workspace
    # TODO: write validation function for the parameter input: date, bounding box, site initial, dx, dy, epsg

    # create tmp folder for new request
    uuid_file_path = generate_uuid_file_path()

    # prepare watershed DEM data
    try:

        # Bounding box DEM
        input_static_DEM  = '/home/ahmet/hydosdata/subsetsource/nedWesternUS.tif'
        subsetDEM_file_path = os.path.join(uuid_file_path, 'DEM84.tif')
        subsetDEM_request = get_raster_subset(input_raster=input_static_DEM,
                                              output_raster=subsetDEM_file_path,
                                              xmin=leftX, ymax=topY, xmax=rightX, ymin=bottomY)

        # Options for projection with epsg full list at: http://spatialreference.org/ref/epsg/
        watershedDEM_file_path = os.path.join(uuid_file_path, 'DEM84_proj_resample.tif')
        WatershedDEM = project_and_resample_Raster_EPSG(input_raster=subsetDEM_file_path,
                                                        output_raster=watershedDEM_file_path,
                                                        dx=dx, dy=dy, epsg_code=epsgCode,
                                                        resample='near')  #TODO failed to make resapmle as parameter

        # Watershed delineation
        if lon_outlet and lat_outlet:
            outlet_shape_file_path = os.path.join(uuid_file_path, 'Outlet.shp')
            outlet_shape_file_result = create_OutletShape_Wrapper(outletPointX=lon_outlet,
                                                                   outletPointY=lat_outlet,
                                                                   output_shape_file_name=outlet_shape_file_path)

            project_shapefile_file_path = os.path.join(uuid_file_path, 'OutletProj.shp')
            project_shapefile_result = project_shapefile_EPSG(input_shape_file=os.path.join(uuid_file_path, 'Outlet'),
                                                              output_shape_file=project_shapefile_file_path,
                                                              epsg_code=epsgCode)

            # Delineate watershed  TODO remember to make the root call taudem function with full path
            watershed_hires_dem_file_path = os.path.join(uuid_file_path, 'watershed.tif')
            watershed_hires_outlet_file_path = os.path.join(uuid_file_path, 'movOutlet.shp')
            Watershed_hires = delineate_Watershed_atShapeFile(input_DEM_raster=watershedDEM_file_path,
                                                               input_outlet_shapefile=project_shapefile_file_path,
                                                               output_raster=watershed_hires_dem_file_path,
                                                               output_outlet_shapefile=watershed_hires_outlet_file_path,
                                                               stream_threshold=streamThreshold)
        else:
            watershed_hires_dem_file_path = os.path.join(uuid_file_path, 'watershed.tif')
            Watershed_hires = Calc(calc='(A<0)*-1001+1', A=watershedDEM_file_path, outfile=watershed_hires_dem_file_path,
                                   NoDataValue=-1000, type='Int16')  # remember to keep only two values in the netcdf file, 1 or no data value!

        # Resample watershed grid to coarser grid # TODO when outlet point is optional make the watershed.nc only include integers
        if dxRes == dx and dyRes == dy:
            Watershed_file_path = watershed_hires_dem_file_path
        else:

            Watershed_file_path = os.path.join(uuid_file_path, 'watershed1.tif')
            Watershed = resample_Raster(input_raster=watershed_hires_dem_file_path, output_raster=Watershed_file_path,
                                        dx=dxRes, dy=dyRes, resample='near')

        # ##  Convert to netCDF for UEB input
        Watershed_temp_nc = os.path.join(uuid_file_path, 'watershed_tmp.nc')
        Watershed_temp = rasterToNetCDF(input_raster=Watershed_file_path, output_netcdf=Watershed_temp_nc)

        # In the netCDF file rename the generic variable "Band1" to "watershed"
        Watershed_NC_file_path = os.path.join(uuid_file_path, 'watershed.nc')
        Watershed_NC = netCDF_rename_variable(input_netcdf=Watershed_temp_nc, output_netcdf=Watershed_NC_file_path,
                                              input_varname='Band1', output_varname='watershed')

    except Exception as e:

        if os.path.isdir(uuid_file_path):
            delete_working_uuid_directory(uuid_file_path)

        return {'success': 'False',
                'message': 'Failed to prepare the watershed DEM data'}

    # prepare the terrain variables
    try:
        # aspect
        aspect_hires_file_path = os.path.join(uuid_file_path, 'Aspect.tif')
        aspect_hires = computeRasterAspect(input_raster=watershedDEM_file_path, output_raster=aspect_hires_file_path)

        if dx == dxRes and dy == dyRes:
            aspect = aspect_hires_file_path
        else:
            aspect = os.path.join(uuid_file_path, 'Aspect1.tif')
            aspect_resample = resample_Raster(input_raster=aspect_hires_file_path, output_raster=aspect,
                                              dx=dxRes, dy=dyRes, resample='near')

        aspect_temp_nc_file_path = os.path.join(uuid_file_path, 'aspect_tmp.nc')
        aspect_temp = rasterToNetCDF(input_raster=aspect, output_netcdf=aspect_temp_nc_file_path)
        aspect_nc_file_path = os.path.join(uuid_file_path, 'aspect.nc')
        aspect_nc = netCDF_rename_variable(input_netcdf=aspect_temp_nc_file_path, output_netcdf=aspect_nc_file_path,
                               input_varname='Band1', output_varname='aspect')

        # slope
        slop_hires_file_path = os.path.join(uuid_file_path, 'Slope.tif')
        slope_hires = computeRasterSlope(input_raster=watershedDEM_file_path, output_raster=slop_hires_file_path)

        if dx == dxRes and dy == dyRes:
            slope = slop_hires_file_path
        else:
            slope = os.path.join(uuid_file_path, 'Slope1.tif')
            slope_resample = resample_Raster(input_raster=slop_hires_file_path, output_raster=slope,
                                              dx=dxRes, dy=dyRes, resample='near')
        slope_temp_nc_file_path = os.path.join(uuid_file_path, 'slope_tmp.nc')
        slope_temp = rasterToNetCDF(input_raster=slope, output_netcdf=slope_temp_nc_file_path)
        slope_nc_file_path = os.path.join(uuid_file_path, 'slope.nc')
        slope_nc = netCDF_rename_variable(input_netcdf=slope_temp_nc_file_path,
                                    output_netcdf=slope_nc_file_path, input_varname='Band1', output_varname='slope')

        # Land cover variables
        nlcd_raster_resource = '/home/ahmet/hydosdata/nlcd2011CONUS/nlcd2011CONUS.tif'
        subset_NLCD_result_file_path = os.path.join(uuid_file_path, 'nlcdProj.tif')
        subset_NLCD_result = project_and_clip_raster(input_raster=nlcd_raster_resource, reference_raster=Watershed_file_path, output_raster=subset_NLCD_result_file_path)

        #cc
        nlcd_variable_result_tmp = os.path.join(uuid_file_path,'cc_tmp.nc')
        nlcd_variable_result = get_canopy_variable(in_NLCDraster=subset_NLCD_result_file_path,
                                                   output_netcdf=nlcd_variable_result_tmp, variable_name='cc')
        cc_nc_file_path = os.path.join(uuid_file_path, 'cc.nc')
        cc_nc = netCDF_rename_variable(input_netcdf=nlcd_variable_result_tmp, output_netcdf=cc_nc_file_path,
                                       input_varname='Band1', output_varname='cc')

        #hcan
        nlcd_variable_result_tmp = os.path.join(uuid_file_path, 'hcan_tmp.nc')
        nlcd_variable_result = get_canopy_variable(in_NLCDraster=subset_NLCD_result_file_path,
                                                   output_netcdf=nlcd_variable_result_tmp, variable_name='hcan')
        hcan_nc_file_path = os.path.join(uuid_file_path, 'hcan.nc')
        hcan_nc = netCDF_rename_variable(input_netcdf=nlcd_variable_result_tmp, output_netcdf=hcan_nc_file_path,
                                         input_varname='Band1', output_varname='hcan')

        #lai
        nlcd_variable_result_tmp = os.path.join(uuid_file_path, 'lai_tmp.nc')
        nlcd_variable_result = get_canopy_variable(in_NLCDraster=subset_NLCD_result_file_path,
                                                   output_netcdf=nlcd_variable_result_tmp, variable_name='lai')
        lai_nc_file_path = os.path.join(uuid_file_path, 'lai.nc')
        lai_nc = netCDF_rename_variable(input_netcdf=nlcd_variable_result_tmp, output_netcdf=lai_nc_file_path,
                                        input_varname='Band1', output_varname='lai')

    except Exception as e:
        if os.path.isdir(uuid_file_path):
            delete_working_uuid_directory(uuid_file_path)

        return {'success': 'False',
                'message': 'Failed to prepare the terrian variables data'}

    # prepare the climate variables
    try:
        climate_files_path = []
        startYear = datetime.strptime(startDateTime,"%Y/%m/%d").year
        endYear = datetime.strptime(endDateTime,"%Y/%m/%d").year
        # we are using data from Daymet; so data are daily
        start_date_value = datetime.strptime(startDateTime, "%Y/%m/%d")
        end_date_value = datetime.strptime(endDateTime, "%Y/%m/%d")
        start_time_index = start_date_value.day-1
        end_time_index = start_date_value.day + (end_date_value - start_date_value).days -1

        climate_Vars = ['vp', 'tmin', 'tmax', 'srad', 'prcp']
        #iterate through climate variables
        for var in climate_Vars:
            for year in range(startYear, endYear + 1):
                climatestaticFile1 = os.path.join('/home/ahmet/hydosdata/DaymetClimate', var + "_" + str(year) + ".nc4")
                climateFile1 = os.path.join(uuid_file_path, var + "_" + str(year) + ".nc")

                Year1sub_request = subset_netCDF_to_reference_raster(input_netcdf=climatestaticFile1,
                                                                     reference_raster=Watershed_file_path,
                                                                     output_netcdf=climateFile1)

                concatFile = os.path.join(uuid_file_path, "conc_" + var + "_" + str(year) + ".nc")
                if year == startYear:
                    concatFile1_url = climateFile1
                else:
                    concatFile2_url = climateFile1
                    concateNC_request = concatenate_netCDF(input_netcdf1=concatFile1_url,
                                                           input_netcdf2=concatFile2_url,
                                                           output_netcdf=concatFile)
                    concatFile1_url = concatFile

            timesubFile = os.path.join(uuid_file_path, "tSub_" + var + "_" + str(year) + ".nc")

            subset_NC_by_time_result = get_netCDF_subset_TimeDim(input_netcdf=concatFile1_url,
                                                                  output_netcdf=timesubFile,
                                                                  time_dim_name='time',
                                                                  start_time_index=start_time_index,
                                                                  end_time_index=end_time_index)
            subset_NC_by_time_file_url = timesubFile

            if var == 'prcp':
                proj_resample_file = os.path.join(uuid_file_path, var + "_0.nc")
            else:
                proj_resample_file = os.path.join(uuid_file_path, var + "0.nc")

            ncProj_resample_result = project_subset_and_resample_netcdf_to_reference_netcdf(input_netcdf=subset_NC_by_time_file_url,
                                                                                            reference_netcdf=Watershed_NC_file_path,
                                                                                            variable_name=var,
                                                                                            output_netcdf=proj_resample_file)

            os.remove(os.path.join(uuid_file_path, 'temp_1.nc'))  # remember to remove the temp files when do the resample
            os.remove(os.path.join(uuid_file_path, 'temp_2.nc'))

            ncProj_resample_file_url = proj_resample_file

            # Do unit conversion for precipitation (mm/day --> m/hr)
            if var == 'prcp':
                prcp_proj_resample_file = os.path.join(uuid_file_path, var + "0.nc")
                ncProj_resample_result = convert_netcdf_units(input_netcdf=ncProj_resample_file_url,
                                                              output_netcdf=prcp_proj_resample_file,
                                                              variable_name=var,
                                                              variable_new_units="m/hr",
                                                              multiplier_factor=0.00004167,
                                                              offset=0.0)
                ncProj_resample_file_url = prcp_proj_resample_file

            climate_files_path.append(ncProj_resample_file_url)

    except Exception as e:
        if os.path.isdir(uuid_file_path):
            delete_working_uuid_directory(uuid_file_path)

        return {'success': 'False',
                'message': 'Failed to prepare the climate variables data'}

    # prepare the parameter files
    try:
        parameter_file_path = []
        # update the control.dat content
        start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
        end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
        start_str = datetime.strftime(start_obj, '%Y %M %d') + ' 0.0'
        end_str = datetime.strftime(end_obj, '%Y %M %d') + ' 0.0'
        file_contents_dict['control.dat'][8] = start_str
        file_contents_dict['control.dat'][9] = end_str

        # update the siteinitial.dat content
        lat = 0.5 * (topY+bottomY)/2.0
        lon = 0.5 * (rightX+leftX)
        file_contents_dict['siteinitial.dat'][45] = str(lat)
        file_contents_dict['siteinitial.dat'][96] = str(lon)

        site_variables_dict = {3: usic, 6: wsic, 9: tic, 12: wcic, 93: ts_last}
        for line, var_name in site_variables_dict.items():
            if var_name:
                file_contents_dict['siteinitial.dat'][line] = str(var_name)

        # write list in parameter files
        for file_name, file_content in file_contents_dict.items():
            file_path = os.path.join(uuid_file_path, file_name)
            with open(file_path, 'w') as para_file:
                para_file.write('\r\n'.join(file_content))  # the line separator is \r\n
            parameter_file_path.append(file_path)

    except Exception as e:
        parameter_file_path = []
        pass

    # share result to HydroShare
    try:
        # zip model input files
        ueb_input_files_path = ['watershed.nc', 'aspect.nc', 'slope.nc', 'cc.nc', 'hcan.nc', 'lai.nc',
                                 'vp0.nc', 'srad0.nc', 'tmin0.nc', 'tmax0.nc', 'prcp0.nc']

        ueb_input_files_path = [Watershed_NC_file_path, aspect_nc_file_path, slope_nc_file_path, cc_nc_file_path,
                                hcan_nc_file_path, lai_nc_file_path]+climate_files_path

        zip_file_path = os.path.join(uuid_file_path, watershedName + '_input.zip' if watershedName else 'ueb_model_input.zip')
        zf = zipfile.ZipFile(zip_file_path, 'w')
        for file_path in ueb_input_files_path+parameter_file_path:
            zf.write(file_path, os.path.basename(file_path))
        zf.close()

        # create resource metadata list
        if parameter_file_path:
            hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
                          'The model inputs data files include: {}. The model parameter files include: {}. This model instance resource is complete for model simulation. ' \
                          .format(', '.join([os.path.basename(file_path) for file_path in ueb_input_files_path]),
                                  ', '.join(file_contents_dict.keys()))
        else:
            hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
                          'The prepared files include: {}. This model instance resource still needs model parameter files {}'\
                           .format(', '.join([os.path.basename(file_path) for file_path in ueb_input_files_path]),
                                   ', '.join(file_contents_dict.keys()))

        metadata = []
        metadata.append({"coverage": {"type": "box",
                                      "value": {"northlimit": str(topY),
                                                "southlimit": str(bottomY),
                                                "eastlimit": str(rightX),
                                                "westlimit": str(leftX),
                                                "units": "Decimal degrees",
                                                "projection": "WGS 84 EPSG:4326"
                                                }
                                      }
                         })

        start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
        end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
        metadata.append({"coverage": {"type": "period",
                                      "value": {"start": datetime.strftime(start_obj, '%M/%d/%Y'),
                                                "end": datetime.strftime(end_obj, '%M/%d/%Y'),
                                                }
                                      }
                         })

        # metadata.append({'contributor': {'name': 'John Smith', 'email': 'jsmith@gmail.com'}})
        # metadata.append({'relation': {'type': 'cites', 'value': 'http'}})
        epsgCode_name = [item[0] for item in EPSG_List if item[1] == epsgCode].pop()

        variable_dict = { 'EPSG code for data': epsgCode_name,
                          'Stream Threshold': streamThreshold,
                          'Outlet Latitude': lat_outlet,
                          'Outlet Longitude': lon_outlet,
                          'Modeling Resolution dx (m)': dxRes,
                          'Modeling Resolution dy (m)': dyRes
                        }

        extra_metadata = {}
        for name, value in variable_dict.items():
            if value:
                extra_metadata[name] = str(value)

        # create resource
        if hs_username and hs_password:
            auth = HydroShareAuthBasic(hs_username, hs_password)
        elif hs_client_id and hs_client_secret and token:
            token = json.loads(token)
            auth = HydroShareAuthOAuth2(hs_client_id, hs_client_secret, token=token)
        else:
            return {'success': "False",
                    'message': "Authentication to HydroShare is failed. Please provide HydroShare User information"}

        hs = HydroShare(auth=auth)

        res_info = hs.createResource('ModelInstanceResource',
                                     title=res_title if res_title else 'UEB model input package',
                                     resource_file=zip_file_path,
                                     keywords=json.loads(res_keywords) if res_keywords else ['UEB', 'snowmelt modeling'],
                                     abstract=hs_abstract,
                                     metadata=json.dumps(metadata),
                                     extra_metadata=json.dumps(extra_metadata)
                                     )
    except Exception as e:
        if os.path.isdir(uuid_file_path):
            delete_working_uuid_directory(uuid_file_path)

        return {'success': 'False',
                'message': 'Failed to share the model input package to HydroShare'}

    delete_working_uuid_directory(uuid_file_path)

    return {'success': 'True',
            'message': 'A model instance resource with name {} has been created. Please check resource http://www.hydroshare.org/resource/{}'.format(res_title, res_info)}