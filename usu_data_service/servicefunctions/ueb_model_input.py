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
    delineate_Watershed_atShapeFile, rasterToNetCDF
from usu_data_service.servicefunctions.watershedFunctions import project_and_resample_Raster_EPSG, \
    create_OutletShape_Wrapper, resample_Raster
from usu_data_service.servicefunctions.netcdfFunctions import netCDF_rename_variable


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

        #Options for projection with epsg full list at: http://spatialreference.org/ref/epsg/
        watershedDEM_file_path = os.path.join(uuid_file_path, 'DEM84_proj_resample.tif')
        WatershedDEM = project_and_resample_Raster_EPSG(input_raster=subsetDEM_file_path,
                                                        output_raster=watershedDEM_file_path,
                                                        dx=dx, dy=dy, epsg_code=epsgCode,
                                                        resample='near')  #TODO failed to make resapmle as parameter

        #  Watershed outlet shape file
        outlet_shape_file_path = os.path.join(uuid_file_path, 'Outlet.shp')
        outlet_shape_file_result = create_OutletShape_Wrapper(outletPointX=lon_outlet,
                                                               outletPointY=lat_outlet,
                                                               output_shape_file_name=outlet_shape_file_path)

        project_shapefile_file_path = os.path.join(uuid_file_path, 'OutletProj.shp')
        project_shapefile_result = project_shapefile_EPSG(input_shape_file=os.path.join(uuid_file_path, 'Outlet'),
                                                          output_shape_file=project_shapefile_file_path,
                                                          epsg_code=epsgCode)

        # Delineate watershed
        # #  TODO watershed delineation: Error opening file xx.tif application called MPI_Abort(MPI_COMM_WORLD, 22) - process 0
        # subprocess.Popen(['chmod', '-R', '0777', uuid_file_path]).wait()  # make sure the change the temp folder access right
        #
        # # Watershed_hires = HDS.delineate_watershed(WatershedDEM['output_raster'],
        # #                 input_outlet_shapefile_url_path=project_shapefile_result['output_shape_file'],
        # #                 threshold=streamThreshold, epsg_code=epsgCode,
        # #                 output_raster=watershedName + str(dx) + 'WS.tif',
        # #                 output_outlet_shapefile=watershedName + 'movOutlet.shp')
        #
        watershed_hires_result_dem = os.path.join(uuid_file_path, 'WS.tif')
        watershed_hires_result_outlet = os.path.join(uuid_file_path, 'movOutlet.shp')
        Wathershed_hires = delineate_Watershed_atShapeFile(input_DEM_raster=watershedDEM_file_path,
                                                           input_outlet_shapefile=project_shapefile_file_path,
                                                           output_raster=watershed_hires_result_dem,
                                                           output_outlet_shapefile=watershed_hires_result_outlet,
                                                           stream_threshold=streamThreshold)


        ####Resample watershed grid to coarser grid # TODO change when delineation works
        if dxRes == dx and dyRes == dy:
            Watershed_file_path = watershedDEM_file_path
        else:
            # Watershed = HDS.resample_raster(input_raster_url_path=watershedDEM_file_path,
            #         cell_size_dx=dxRes, cell_size_dy=dyRes, resample='near', output_raster=watershedName + str(dxRes) + 'WS.tif')

            Watershed_file_path = os.path.join(uuid_file_path, 'watershed.tif')
            Watershed = resample_Raster(input_raster=watershedDEM_file_path, output_raster=Watershed_file_path,
                                        dx=dxRes, dy=dyRes, resample='near')

        #HDS.download_file(file_url_path=Watershed['output_raster'], save_as=workingDir+watershedName+str(dxRes)+'.tif')

        # ##  Convert to netCDF for UEB input
        Watershed_temp_nc = os.path.join(uuid_file_path, 'watershed_tmp.nc')
        Watershed_temp = rasterToNetCDF(input_raster=Watershed_file_path, output_netcdf=Watershed_temp_nc)

        # In the netCDF file rename the generic variable "Band1" to "watershed"
        Watershed_NC_file_path = os.path.join(uuid_file_path, 'watershed.nc')
        Watershed_NC = netCDF_rename_variable(input_netcdf=Watershed_temp_nc, output_netcdf=Watershed_NC_file_path,
                                              input_varname='Band1', output_varname='watershed')

    except Exception as e:

        # if os.path.isdir(uuid_file_path):
        #     delete_working_uuid_directory(uuid_file_path)

        return {'success': 'False',
                'message': 'Failed to prepare the watershed DEM data'+uuid_file_path}
    #
    #
    #
    # # prepare the terrain variables
    # try:
    #     # aspect
    #     aspect_hires = HDS.create_raster_aspect(input_raster_url_path=WatershedDEM['output_raster'],
    #                                 output_raster=watershedName + 'Aspect' + str(dx)+ '.tif')
    #
    #     if dx == dxRes and dy == dyRes:
    #         aspect = aspect_hires
    #     else:
    #         aspect = HDS.resample_raster(input_raster_url_path= aspect_hires['output_raster'], cell_size_dx=dxRes,
    #                                 cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Aspect' + str(dxRes) + '.tif')
    #     aspect_temp = HDS.raster_to_netcdf(input_raster_url_path=aspect['output_raster'],output_netcdf='aspect'+str(dxRes)+'.nc')
    #     aspect_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=aspect_temp['output_netcdf'],
    #                                 output_netcdf='aspect.nc', input_variable_name='Band1', output_variable_name='aspect')
    #     # slope
    #     slope_hires = HDS.create_raster_slope(input_raster_url_path=WatershedDEM['output_raster'],
    #                                 output_raster=watershedName + 'Slope' + str(dx) + '.tif')
    #
    #     if dx == dxRes and dy == dyRes:
    #         slope = slope_hires
    #     else:
    #         slope = HDS.resample_raster(input_raster_url_path= slope_hires['output_raster'], cell_size_dx=dxRes,
    #                                 cell_size_dy=dyRes, resample='near', output_raster=watershedName + 'Slope' + str(dxRes) + '.tif')
    #     slope_temp = HDS.raster_to_netcdf(input_raster_url_path=slope['output_raster'], output_netcdf='slope'+str(dxRes)+'.nc')
    #     slope_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=slope_temp['output_netcdf'],
    #                                 output_netcdf='slope.nc', input_variable_name='Band1', output_variable_name='slope')
    #
    #     #Land cover variables
    #     nlcd_raster_resource = 'nlcd2011CONUS.tif'
    #     subset_NLCD_result = HDS.project_clip_raster(input_raster=nlcd_raster_resource,
    #                                 ref_raster_url_path=Watershed['output_raster'],
    #                                 output_raster=watershedName + 'nlcdProj' + str(dxRes) + '.tif')
    #     #cc
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='cc', output_netcdf=watershedName+str(dxRes)+'cc.nc')
    #     cc_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='cc.nc', input_variable_name='Band1', output_variable_name='cc')
    #     #hcan
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='hcan', output_netcdf=watershedName+str(dxRes)+'hcan.nc')
    #     hcan_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='hcan.nc', input_variable_name='Band1',output_variable_name='hcan')
    #     #lai
    #     nlcd_variable_result = HDS.get_canopy_variable(input_NLCD_raster_url_path=subset_NLCD_result['output_raster'],
    #                                 variable_name='lai', output_netcdf=watershedName+str(dxRes)+'lai.nc')
    #     lai_nc = HDS.netcdf_rename_variable(input_netcdf_url_path=nlcd_variable_result['output_netcdf'],
    #                                 output_netcdf='lai.nc', input_variable_name='Band1',output_variable_name='lai')
    #
    # except Exception as e:
    #     service_response['status'] = 'Error'
    #     service_response['result'] = 'Failed to prepare the terrain variables.' + e.message
    #     # TODO clean up the space
    #     return service_response
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
            'message': 'Please check resource http://www.hydroshare.org/resource/{}'+uuid_file_path+Watershed['success']}