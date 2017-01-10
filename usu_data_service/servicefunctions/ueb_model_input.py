import os,stat
import json
import zipfile
import shutil
import subprocess
import datetime

from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic
from usu_data_service.utils import generate_uuid_file_path, delete_working_uuid_directory
from usu_data_service.servicefunctions.model_parameter_list import site_initial_variable_codes, input_vairable_codes

from usu_data_service.servicefunctions.terrainFunctions import get_raster_subset, project_shapefile_EPSG, \
    delineate_Watershed_atShapeFile, rasterToNetCDF, computeRasterAspect,computeRasterSlope
from usu_data_service.servicefunctions.watershedFunctions import project_and_resample_Raster_EPSG, \
    create_OutletShape_Wrapper, resample_Raster
from usu_data_service.servicefunctions.netcdfFunctions import netCDF_rename_variable
from usu_data_service.servicefunctions.canopyFunctions import project_and_clip_raster, get_canopy_variable


def create_ueb_input(hs_username=None, hs_password=None, hs_client_id=None,hs_client_secret=None, token=None,
                     topY=None, bottomY=None, leftX=None, rightX=None,
                     lat_outlet=None, lon_outlet=None, streamThreshold=1000, watershedName=None,
                     epsgCode=None, startDateTime=None, endDateTime=None, dx=None, dy=None,
                      dxRes=None, dyRes=None, res_title=None, res_keywords=None,
                      **kwargs):
    #TODO: remember to change the workspace folder in hydrods with access right chmod -R 0777 /workspace

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

        # Watershed outlet shape file
        outlet_shape_file_path = os.path.join(uuid_file_path, 'Outlet.shp')
        outlet_shape_file_result = create_OutletShape_Wrapper(outletPointX=lon_outlet,
                                                               outletPointY=lat_outlet,
                                                               output_shape_file_name=outlet_shape_file_path)

        project_shapefile_file_path = os.path.join(uuid_file_path, 'OutletProj.shp')
        project_shapefile_result = project_shapefile_EPSG(input_shape_file=os.path.join(uuid_file_path, 'Outlet'),
                                                          output_shape_file=project_shapefile_file_path,
                                                          epsg_code=epsgCode)

        # Delineate watershed # remember to make the root call taudem function with full path
        watershed_hires_dem_file_path = os.path.join(uuid_file_path, 'watershed.tif')
        watershed_hires_outlet_file_path = os.path.join(uuid_file_path, 'movOutlet.shp')
        Wathershed_hires = delineate_Watershed_atShapeFile(input_DEM_raster=watershedDEM_file_path,
                                                           input_outlet_shapefile=project_shapefile_file_path,
                                                           output_raster=watershed_hires_dem_file_path,
                                                           output_outlet_shapefile=watershed_hires_outlet_file_path,
                                                           stream_threshold=streamThreshold)

        #Resample watershed grid to coarser grid # TODO change when delineation works
        if dxRes == dx and dyRes == dy:
            Watershed_file_path = watershed_hires_dem_file_path
        else:

            Watershed_file_path = os.path.join(uuid_file_path, 'watershed1.tif')
            Watershed = resample_Raster(input_raster=watershedDEM_file_path, output_raster=Watershed_file_path,
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
    #
    #
    # # prepare the climate variables
    # try:
    #     startYear = datetime.strptime(startDateTime,"%Y/%m/%d").year
    #     endYear = datetime.strptime(endDateTime,"%Y/%m/%d").year
    #     #### we are using data from Daymet; so data are daily
    #     startDate = datetime.strptime(startDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')
    #     endDate = datetime.strptime(endDateTime, "%Y/%m/%d").date().strftime('%m/%d/%Y')
    #
    #     climate_Vars = ['vp', 'tmin', 'tmax', 'srad', 'prcp']
    #     ####iterate through climate variables
    #     for var in climate_Vars:
    #         for year in range(startYear, endYear + 1):
    #             climatestaticFile1 = var + "_" + str(year) + ".nc4"
    #             climateFile1 = watershedName + '_' + var + "_" + str(year) + ".nc"
    #             Year1sub_request = HDS.subset_netcdf(input_netcdf=climatestaticFile1,
    #                                                  ref_raster_url_path=Watershed['output_raster'],
    #                                                  output_netcdf=climateFile1)
    #             concatFile = "conc_" + climateFile1
    #             if year == startYear:
    #                 concatFile1_url = Year1sub_request['output_netcdf']
    #             else:
    #                 concatFile2_url = Year1sub_request['output_netcdf']
    #                 concateNC_request = HDS.concatenate_netcdf(input_netcdf1_url_path=concatFile1_url,
    #                                                            input_netcdf2_url_path=concatFile2_url,
    #                                                            output_netcdf=concatFile)
    #                 concatFile1_url = concateNC_request['output_netcdf']
    #
    #         timesubFile = "tSub_" + climateFile1
    #         subset_NC_by_time_result = HDS.subset_netcdf_by_time(input_netcdf_url_path=concatFile1_url,
    #                                                              time_dimension_name='time', start_date=startDate,
    #                                                              end_date=endDate, output_netcdf=timesubFile)
    #         subset_NC_by_time_file_url = subset_NC_by_time_result['output_netcdf']
    #         if var == 'prcp':
    #             proj_resample_file = var + "_0.nc"
    #         else:
    #             proj_resample_file = var + "0.nc"
    #         ncProj_resample_result = HDS.project_subset_resample_netcdf(
    #             input_netcdf_url_path=subset_NC_by_time_file_url,
    #             ref_netcdf_url_path=Watershed_NC['output_netcdf'],
    #             variable_name=var, output_netcdf=proj_resample_file)
    #         ncProj_resample_file_url = ncProj_resample_result['output_netcdf']
    #
    #         #### Do unit conversion for precipitation (mm/day --> m/hr)
    #         if var == 'prcp':
    #             proj_resample_file = var + "0.nc"
    #             ncProj_resample_result = HDS.convert_netcdf_units(input_netcdf_url_path=ncProj_resample_file_url,
    #                                                             output_netcdf=proj_resample_file,
    #                                                             variable_name=var, variable_new_units='m/hr',
    #                                                             multiplier_factor=0.00004167, offset=0.0)
    #             # ncProj_resample_file_url = ncProj_resample_result['output_netcdf']
    #
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to prepare the climate variables.' + e.message
    #     # TODO clean up the space
    #     return service_response
    #
    #
    # # prepare the parameter files
    # try:
    #     # create temp parameter files
    #     temp_dir = tempfile.mkdtemp()
    #
    #     # update the control.dat content
    #     start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
    #     end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
    #     start_str = datetime.strftime(start_obj, '%Y %M %d') + ' 0.0'
    #     end_str = datetime.strftime(end_obj, '%Y %M %d') + ' 0.0'
    #     file_contents_dict['control.dat'][8] = start_str
    #     file_contents_dict['control.dat'][9] = end_str
    #
    #     # update the siteinitial.dat content
    #     lat = 0.5 * (topY+bottomY)
    #     lon = 0.5 * (rightX+leftX)
    #     file_contents_dict['siteinitial.dat'][45] = str(lat)
    #     file_contents_dict['siteinitial.dat'][96] = str(lon)
    #
    #     # write list in parameter files
    #     for file_name, file_content in file_contents_dict.items():
    #         file_path = os.path.join(temp_dir, file_name)
    #         with open(file_path, 'w') as para_file:
    #             para_file.write('\r\n'.join(file_content))  # the line separator is \r\n
    #
    #     # upload files to Hydro-DS
    #     for file_name in file_contents_dict.keys():
    #         HDS.upload_file(file_to_upload=os.path.join(temp_dir, file_name))
    #
    #     # clean up tempdir
    #     parameter_file_names = file_contents_dict.keys()
    #     shutil.rmtree(temp_dir)
    #
    # except Exception as e:
    #     parameter_file_names = []
    #     shutil.rmtree(temp_dir)
    #
    #     # # TODO remove the lines below
    #     # service_response['status'] = 'Error'
    #     # service_response['result'] = 'Failed to prepare the parameter files.' + e.message
    #     # return service_response
    #
    #
    # # share result to HydroShare
    # try:
    #     #upload ueb input package to hydroshare
    #     ueb_inputPackage_dict = ['watershed.nc', 'aspect.nc', 'slope.nc', 'cc.nc', 'hcan.nc', 'lai.nc',
    #                              'vp0.nc', 'srad0.nc', 'tmin0.nc', 'tmax0.nc', 'prcp0.nc']
    #     HDS.zip_files(files_to_zip=ueb_inputPackage_dict+parameter_file_names, zip_file_name=watershedName+'_input.zip')
    #
    #     # create resource metadata list
    #     # TODO create the metadata for ueb model instance: box, time, resolution, watershed name, streamthreshold,epsg code, outlet poi
    #     hs_title = res_title
    #
    #     if parameter_file_names:
    #         hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
    #                       'The model inputs data files include: {}. The model parameter files include: {}. This model instance resource is complete for model simulation. ' \
    #                       .format(', '.join(ueb_inputPackage_dict), ', '.join(file_contents_dict.keys()))
    #     else:
    #         hs_abstract = 'It was created using HydroShare UEB model inputs preparation application which utilized the HydroDS modeling web services. ' \
    #                       'The prepared files include: {}. This model instance resource still needs model parameter files {}'\
    #                        .format(', '.join(ueb_inputPackage_dict), ', '.join(file_contents_dict.keys()))
    #
    #     hs_keywords = res_keywords.split(',')
    #
    #     metadata = []
    #     metadata.append({"coverage": {"type": "box",
    #                                   "value": {"northlimit": str(topY),
    #                                             "southlimit": str(bottomY),
    #                                             "eastlimit": str(rightX),
    #                                             "westlimit": str(leftX),
    #                                             "units": "Decimal degrees",
    #                                             "projection": "WGS 84 EPSG:4326"
    #                                             }
    #                                   }
    #                      })
    #
    #     start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
    #     end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
    #     metadata.append({"coverage": {"type": "period",
    #                                   "value": {"start": datetime.strftime(start_obj, '%M/%d/%Y'),
    #                                             "end": datetime.strftime(end_obj, '%M/%d/%Y'),
    #                                             }
    #                                   }
    #                      })
    #     # metadata.append({'contributor': {'name': 'John Smith', 'email': 'jsmith@gmail.com'}})
    #     # metadata.append({'relation': {'type': 'cites', 'value': 'http'}})
    #
    #     # create resource
    #     HDS.set_hydroshare_account(hs_name, hs_password)
    #     res_info = HDS.create_hydroshare_resource(file_name=watershedName+'_input.zip', resource_type='ModelInstanceResource', title=hs_title,
    #                                abstract=hs_abstract, keywords=hs_keywords, metadata=metadata)
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to share the results to HydroShare.' + e.message
    #     # TODO clean up the space
    #     return service_response
    #
    # service_response['result'] = "A model instance resource with name '{}' has been created with link https://www.hydroshare.org/resoruce/{}".format(
    #                                 res_title, res_info['resource_id'])

    return {'success': 'True',
            'message': 'Please check resource http://www.hydroshare.org/resource/{}'+uuid_file_path}