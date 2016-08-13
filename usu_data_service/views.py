import logging
import json
import requests

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRF_ValidationError
from rest_framework.exceptions import NotAuthenticated

from usu_data_service.servicefunctions.terrainFunctions import *
from usu_data_service.servicefunctions.watershedFunctions import *
from usu_data_service.servicefunctions.netcdfFunctions import *
from usu_data_service.servicefunctions.canopyFunctions import *
from usu_data_service.servicefunctions.static_data import *
from usu_data_service.topnet_data_service.TOPNET_Function import CommonLib
from usu_data_service.serializers import *
from usu_data_service.models import *
from usu_data_service.utils import *
from usu_data_service.local_settings import *
from usu_data_service.capabilities import *

WESTERN_US_DEM = os.path.join(STATIC_DATA_ROOT_PATH, 'subsetsource/nedWesternUS.tif')

logger = logging.getLogger(__name__)

funcs = {
          'subsetrastertobbox':
                {
                    'function_to_execute': get_raster_subset,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'subset.tif'}],
                    'user_file_inputs': ['input_raster'],
                    'user_inputs': ['xmin', 'ymax', 'xmax', 'ymin'],
                    'validator': SubsetDEMRequestValidator
                },

          'subsetUSGSNEDDEM':
                {
                    'function_to_execute': subset_USGS_NED_DEM,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'subset_usgs_ned_dem.tif'}],
                    'user_file_inputs': [],
                    'user_inputs': ['xmin', 'ymax', 'xmax', 'ymin'],
                    'validator': SubsetUSGSNEDDEMRequestValidator
                },

          'subsetprojectresamplerasterutm':
                {
                    'function_to_execute': subset_project_and_resample_Raster_UTM_NAD83,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'subset_proj_resample.tif'}],
                    'user_file_inputs': ['input_raster'],
                    'user_inputs': ['xmin', 'ymax', 'xmax', 'ymin', 'dx', 'dy', 'resample'],
                    'validator': SubsetProjectResampleRasterRequestValidator
                },

          'subsetprojectresamplerasterepsg':
                {
                    'function_to_execute': subset_project_and_resample_Raster_EPSG,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'subset_proj_resample.tif'}],
                    'user_file_inputs': ['input_raster'],
                    'user_inputs': ['xmin', 'ymax', 'xmax', 'ymin', 'dx', 'dy', 'resample', 'epsg_code'],
                    'validator': SubsetProjectResampleRasterEPSGRequestValidator
                },


          'rastertonetcdfrenamevariable':
                {
                    'function_to_execute': rasterToNetCDF_rename_variable,
                    'file_inputs': [],
                    'file_outputs': [{'output_netcdf': 'output.nc'}],
                    'user_inputs': ['increasing_x', 'increasing_y', 'output_varname'],
                    'user_file_inputs': ['input_raster'],
                    'validator': RasterToNetCDFVariableRequestValidator
                  },

          'rastertonetcdf':
                {
                    'function_to_execute': rasterToNetCDF,
                    'file_inputs': [],
                    'file_outputs': [{'output_netcdf': 'output.nc'}],
                    'user_inputs': [],
                    'user_file_inputs': ['input_raster'],
                    'validator': RasterToNetCDFRequestValidator
                  },

          'delineatewatershedatxy':
                {
                    'function_to_execute': delineate_Watershed_TauDEM,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'watershed.tif'}, {'output_outlet_shapefile': 'moveout.shp'}],
                    'user_inputs': ['epsg_code', 'stream_threshold', 'outlet_point_x', 'outlet_point_y'],
                    'user_file_inputs': ['input_DEM_raster'],
                    'validator': DelineateWatershedAtXYRequestValidator
                },

          'delineatewatershedatshape':
                {
                    'function_to_execute': delineate_Watershed_atShapeFile,
                    'file_inputs': [],
                    'file_outputs': [{'output_raster': 'watershed.tif'}, {'output_outlet_shapefile': 'moveout.shp'}],
                    'user_inputs': ['stream_threshold'],
                    'user_file_inputs': ['input_DEM_raster', 'input_outlet_shapefile'],
                    'validator': DelineateWatershedAtShapeFileRequestValidator
                },

          'createoutletshapefile':
                {
                    'function_to_execute': create_OutletShape_Wrapper,
                    'file_inputs': [],
                    'file_outputs': [{'output_shape_file_name': 'outlet.shp'}],
                    'user_inputs': ['outletPointX', 'outletPointY'],
                    'user_file_inputs': [],
                    'validator': CreateOutletShapeRequestValidator
                },

          'projectshapefileutm':
               {
                    'function_to_execute': project_shapefile_UTM_NAD83,
                    'file_inputs': [],
                    'file_outputs': [{'output_shape_file': 'shape_proj.shp'}],
                    'user_inputs': ['utm_zone'],
                    'user_file_inputs': ['input_shape_file'],
                    'validator': ProjectShapeFileUTMRequestValidator
               },

          'projectshapefileepsg':
               {
                    'function_to_execute': project_shapefile_EPSG,
                    'file_inputs': [],
                    'file_outputs': [{'output_shape_file': 'shape_proj.shp'}],
                    'user_inputs': ['epsg_code'],
                    'user_file_inputs': ['input_shape_file'],
                    'validator': ProjectShapeFileEPSGRequestValidator
               },

          'computerasteraspect':
                {
                   'function_to_execute': computeRasterAspect,
                   'file_inputs': [],
                    'file_outputs': [{'output_raster': 'aspect.tif'}],
                    'user_inputs': [],
                    'user_file_inputs': ['input_raster'],
                    'validator': ComputeRasterAspectRequestValidator
                },

          'computerasterslope':
                {
                   'function_to_execute': computeRasterSlope,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'slope.tif'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_raster'],
                   'validator': ComputeRasterSlopeRequestValidator
                },

          'combinerasters':
                {
                   'function_to_execute': combineRasters,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'combined.tif'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_raster1', 'input_raster2'],
                   'validator': CombineRastersRequestValidator
                },

          'projectraster':
                {
                   'function_to_execute': project_raster_UTM_NAD83,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'projected.tif'}],
                   'user_inputs': ['utmZone'],
                   'user_file_inputs': ['input_raster'],
                   'validator': ProjectRasterRequestValidator
                },

          'resampleraster':
                {
                   'function_to_execute': resample_Raster,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'resample.tif'}],
                   'user_inputs': ['dx', 'dy', 'resample'],
                   'user_file_inputs': ['input_raster'],
                   'validator': ResampleRasterRequestValidator
                },

          'projectresamplerasterutm':
                {
                   'function_to_execute': project_and_resample_Raster_UTM_NAD83,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'projected_resampled.tif'}],
                   'user_inputs': ['utm_zone', 'dx', 'dy', 'resample'],
                   'user_file_inputs': ['input_raster'],
                   'validator': ProjectResampleRasterUTMRequestValidator
                },

          'projectresamplerasterepsg':
                {
                   'function_to_execute': project_and_resample_Raster_EPSG,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'projected_resampled.tif'}],
                   'user_inputs': ['epsg_code', 'dx', 'dy', 'resample'],
                   'user_file_inputs': ['input_raster'],
                   'validator': ProjectResampleRasterEPSGRequestValidator
                },

          'subsetrastertoreference':
                {
                   'function_to_execute': subset_raster_to_referenceRaster,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'subset_ref.tif'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_raster', 'reference_raster'],
                   'validator': SubsetRasterToReferenceRequestValidator
                },

          'reversenetcdfyaxis':
                {
                   'function_to_execute': reverse_netCDF_yaxis,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'reverse_yaxis.nc'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': ReverseNetCDFYaxisRequestValidator
                },

          'reversenetcdfyaxisandrenamevariable':
                {
                   'function_to_execute': reverse_netCDF_yaxis_and_rename_variable,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'reverse_yaxis.nc'}],
                   'user_inputs': ['input_varname', 'output_varname'],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': ReverseNetCDFYaxisAndRenameVariableRequestValidator
                },

          'netcdfrenamevariable':
                {
                   'function_to_execute': netCDF_rename_variable,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'rename_varname.nc'}],
                   'user_inputs': ['input_varname', 'output_varname'],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': NetCDFRenameVariableRequestValidator
                },

          'subsetnetcdftoreference':
                {
                   'function_to_execute': subset_netCDF_to_reference_raster,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'subset.nc'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_netcdf', 'reference_raster'],
                   'validator': SubsetNetCDFToReferenceRequestValidator
                },

          'projectnetcdf':
                {
                   'function_to_execute': project_netCDF_UTM_NAD83,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'projected.nc'}],
                   'user_inputs': ['utm_zone', 'variable_name'],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': ProjectNetCDFRequestValidator
                },

          'subsetnetcdfbytime':
                {
                   'function_to_execute': get_netCDF_subset_TimeDim,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'subset_time_based.nc'}],
                   'user_inputs': ['time_dim_name', 'start_time_index', 'end_time_index'],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': SubsetNetCDFByTimeDimensionRequestValidator
                },

          'resamplenetcdftoreferencenetcdf':
                {
                   'function_to_execute': resample_netcdf_to_reference_netcdf,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'resample.nc'}],
                   'user_inputs': ['variable_name'],
                   'user_file_inputs': ['input_netcdf', 'reference_netcdf'],
                   'validator': ResampleNetCDFRequestValidator
                },

          'concatenatenetcdf':
                {
                   'function_to_execute': concatenate_netCDF,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'concatenated.nc'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_netcdf1', 'input_netcdf2'],
                   'validator': ConcatenateNetCDFRequestValidator
                },

          'projectsubsetresamplenetcdftoreferencenetcdf':
                {
                   'function_to_execute': project_subset_and_resample_netcdf_to_reference_netcdf,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'proj_subset_resample.nc'}],
                   'user_inputs': ['variable_name'],
                   'user_file_inputs': ['input_netcdf', 'reference_netcdf'],
                   'validator': ProjectSubsetResampleNetCDFRequestValidator
                },

          'projectandcliprastertoreference':
                {
                   'function_to_execute': project_and_clip_raster,
                   'file_inputs': [],
                   'file_outputs': [{'output_raster': 'project_clip.tif'}],
                   'user_inputs': [],
                   'user_file_inputs': ['input_raster', 'reference_raster'],
                   'validator': ProjectClipRasterRequestValidator
                },

          'getcanopyvariables':
                {
                   'function_to_execute': get_canopy_variables,
                   'file_inputs': [],
                   'file_outputs': [{'out_ccNetCDF': 'canopy_cc.nc'}, {'out_hcanNetCDF': 'canopy_hcan.nc'},
                                    {'out_laiNetCDF': 'canopy_lai.nc'}],
                   'user_inputs': [],
                   'user_file_inputs': ['in_NLCDraster'],
                   'validator': GetCanopyVariablesRequestValidator
                },

          'getcanopyvariable':
                {
                   'function_to_execute': get_canopy_variable,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'canopy.nc'}],
                   'user_inputs': ['variable_name'],
                   'user_file_inputs': ['in_NLCDraster'],
                   'validator': GetCanopyVariableRequestValidator
                },

          'convertnetcdfunits':
                {
                   'function_to_execute': convert_netcdf_units,
                   'file_inputs': [],
                   'file_outputs': [{'output_netcdf': 'converted_units.nc'}],
                   'user_inputs': ['variable_name', 'variable_new_units', 'multiplier_factor', 'offset'],
                   'user_file_inputs': ['input_netcdf'],
                   'validator': ConvertNetCDFUnitsRequestValidator
                },

          # sample TOPNET service testing
          'downloadstreamflow':
                {
                   'function_to_execute': CommonLib.download_streamflow,
                   'file_inputs': [],
                   'file_outputs': [{'output_streamflow': 'streamflow_calibration.dat'}],
                   'user_inputs': ['USGS_gage', 'Start_Year', 'End_Year'],
                   'user_file_inputs': [],
                   'validator': DownloadStreamflowRequestValidator
                },

         }


class RunService(APIView):
    """
    Executes the specified service/function

    URL: /api/dataservice/{func}
    HTTP method: GET

    :param func: name of the function to execute

    The function specific parameter values needs to be passed as part of the query string

    :raises
    ValidationError: json response format: {'parameter_1': [parameter_1_error], 'parameter_2': [parameter_2_error], ..}
    """
    allowed_methods = ('GET',)

    def get(self, request, func, format=None):

        if not request.user.is_authenticated():
            raise NotAuthenticated()

        logger.info('Executing python data service function:' + func)
        params = funcs.get(func, None)

        if not params:
            return Response({'success': False, 'error': 'No such function {function_name} is '
                                                        'supported.'.format(function_name=func)})

        validator = params['validator']

        request_validator = validator(data=self.request.query_params)
        if not request_validator.is_valid():
            raise DRF_ValidationError(detail=request_validator.errors)

        subprocparams = {}
        for param_dict_item in params['file_inputs']:
            for param_name in param_dict_item:
                subprocparams[param_name] = param_dict_item[param_name]

        # generate uuid file name for each parameter in file_outputs dict
        uuid_file_path = generate_uuid_file_path()
        logger.debug('temporary uuid working directory for function ({function_name}):{w_dir}'.format(
                     function_name=func, w_dir=uuid_file_path))

        output_files = {}
        for param_dict_item in params['file_outputs']:
            for param_name in param_dict_item:
                output_file_name = request_validator.validated_data.get(param_name, param_dict_item[param_name])
                subprocparams[param_name] = os.path.join(uuid_file_path, output_file_name)
                output_files[param_name] = subprocparams[param_name]

        for p in params['user_inputs']:
            subprocparams[p] = request_validator.validated_data[p]

        # user input file can come as a url file path or just a file name
        # comes in url format for files that are stored for the user in django, copy the file to uuid temp folder
        # and then pass the uuid file path to the executing function
        # comes as a file name for static data file on the server, get the static data file path from the file name
        # and pass that file path to the executing function
        for p in params['user_file_inputs']:
            input_file = request_validator.validated_data[p]
            if is_input_file_url_path(input_file):
                uuid_input_file_path = copy_input_file_to_uuid_working_directory(uuid_file_path,
                                                                                 request_validator.validated_data[p])
                if uuid_input_file_path.endswith('.zip'):
                    unzip_shape_file(uuid_input_file_path)
                    uuid_input_file_path = uuid_input_file_path.replace('zip', 'shp')

                subprocparams[p] = uuid_input_file_path
                logger.debug('input_uuid_file_path_from_url_path:' + uuid_input_file_path)
            else:
                static_data_file_path = get_static_data_file_path(input_file)
                subprocparams[p] = static_data_file_path
                logger.debug('input_static_file_path:' + static_data_file_path)

        # execute the function
        result = params['function_to_execute'](**subprocparams)
        logger.debug('result from function ({function_name}):{result}'.format(function_name=func, result=result))

        # process function output results
        data = []
        if result['success'] == 'True':
            user = request.user if request.user.is_authenticated() else None
            data = _save_output_files_in_django(output_files, user=user)
            response_data = {'success': True, 'data': data, 'error': []}
        else:
            response_data = {'success': False, 'data': data, 'error': result['message']}

        delete_working_uuid_directory(uuid_file_path)

        return Response(data=response_data)


@api_view(['GET'])
def show_capabilities(request):
    data = get_capabilites()
    response_data = {'success': True, 'data': data, 'error': []}
    return Response(data=response_data)


@api_view(['GET'])
def show_service_info(request, func):
    data = get_service_info(service_name=func)
    if data is None:
        raise DRF_ValidationError("%s is not a supported service name" % func)
    response_data = {'success': True, 'data': data, 'error': []}
    return Response(data=response_data)

@api_view(['GET'])
def show_static_data_info(request):
    data = get_static_data_files_info()
    response_data = {'success': True, 'data': data, 'error': []}
    return Response(data=response_data)

@api_view(['POST'])
def upload_file(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    number_of_files = len(request.FILES)

    if number_of_files == 0:
        error_msg = {'file': 'No file was found to upload.'}
        raise DRF_ValidationError(detail=error_msg)
    elif number_of_files > 1:
        error_msg = {'file': 'More than one file was found. Only one file can be uploaded at a time.'}
        raise DRF_ValidationError(detail=error_msg)

    posted_file = request.FILES['file']
    user_file = UserFile(file=posted_file)
    user_file.user = request.user
    user_file.save()

    file_url = current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
    response_data = {'success': True, 'data': file_url, 'error': []}
    return Response(data=response_data)

@api_view(['GET'])
def get_hydrogate_result_file(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    request_validator = GetHydrogateResultFileRequestValidator(data=request.query_params)
    if not request_validator.is_valid():
            raise DRF_ValidationError(detail=request_validator.errors)

    hydrogate_result_file_name = request_validator.validated_data['result_file_name']
    save_as_file_name = request_validator.validated_data['save_as_file_name']
    hg_download_file_url_path = 'http://129.123.41.158:20198/{file_name}'.format(file_name=hydrogate_result_file_name)
    uuid_file_path = generate_uuid_file_path()
    save_as = os.path.join(uuid_file_path, save_as_file_name)
    with open(save_as, 'wb') as file_obj:
        response = requests.get(hg_download_file_url_path, stream=True)
        if not response.ok:
            # Something went wrong
            error_msg = 'Hydrogate error. ' + response.reason + " " + response.content
            response_data = {'success': False, 'data': [], 'error': [error_msg]}
            return Response(data=response_data)

        for block in response.iter_content(1024):
            if not block:
                break
            file_obj.write(block)

    delete_user_file(request.user, save_as_file_name)
    user_file = UserFile(file=File(open(save_as, 'rb')), user=request.user)
    user_file.save()
    file_url = current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
    response_data = {'success': True, 'data': file_url, 'error': []}
    logger.debug('django file url for the hydrogate result file:' + user_file.file.url)
    delete_working_uuid_directory(uuid_file_path)
    return Response(data=response_data)


@api_view(['GET'])
def show_my_files(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    user_files = []
    for user_file in UserFile.objects.filter(user=request.user).all():
        if user_file.file:
            user_file_url = current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
            user_files.append(user_file_url)

    response_data = {'success': True, 'data': user_files, 'error': []}

    return Response(data=response_data)


@api_view(['DELETE'])
def delete_my_file(request, filename):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    for user_file in UserFile.objects.filter(user=request.user).all():
        if user_file.file.name.split('/')[2] == filename:
            user_file.file.delete()
            user_file.delete()
            logger.debug("{file_name} file deleted by user:{user_id}".format(file_name=filename,
                                                                             user_id=request.user.id))
            break

    else:
        raise NotFound()

    response_data = {'success': True, 'data': filename, 'error': []}
    return Response(data=response_data)

@api_view(['GET'])
def create_hydroshare_resource(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    request_validator = HydroShareCreateResourceRequestValidator(data=request.query_params)
    if not request_validator.is_valid():
        raise DRF_ValidationError(detail=request_validator.errors)

    hs_username = request_validator.validated_data['hs_username']
    hs_password = request_validator.validated_data['hs_password']
    hydroshare_auth = (hs_username, hs_password)
    file_name = request_validator.validated_data['file_name']
    resource_type = request_validator.validated_data['resource_type']
    title = request_validator.validated_data.get('title', None)
    abstract = request_validator.validated_data.get('abstract', None)
    keywords = request_validator.validated_data.get('keywords', None)
    metadata = request_validator.validated_data.get('metadata', None)

    for user_file in UserFile.objects.filter(user=request.user).all():
        if user_file.file.name.split('/')[2] == file_name:
            break
    else:
        raise NotFound()

    hs_url = 'https://www.hydroshare.org/hsapi/resource'
    payload = {'resource_type': resource_type}

    if title:
        payload['title'] = title

    if abstract:
        payload['abstract'] = abstract

    if keywords:
        for (i, kw) in enumerate(keywords):
                key = "keywords[{index}]".format(index=i)
                payload[key] = kw

    if metadata:
        payload['metadata'] = metadata

    user_folder = 'user_%s' % request.user.id
    source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
    files = {'file': open(source_file_path, 'rb')}

    # create a resource in HydroShare
    response = requests.post(hs_url+'/?format=json', data=payload, files=files, auth=hydroshare_auth)

    if response.ok:
        response_content_dict = json.loads(response.content.decode('utf-8'))
        response_data = {'success': True, 'data': response_content_dict, 'error': []}
    else:
        err_msg = "Failed to create a resource in HydroShare.{reason}".format(reason=response.reason)
        response_data = {'success': False, 'data': [], 'error': err_msg}

    return Response(data=response_data)


@api_view(['GET'])
def zip_my_files(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    request_validator = ZipMyFilesRequestValidator(data=request.query_params)
    if not request_validator.is_valid():
        raise DRF_ValidationError(detail=request_validator.errors)

    files_to_zip = request_validator.validated_data['file_names']
    zip_file_name = request_validator.validated_data['zip_file_name']
    zip_file_url = zip_user_files(user=request.user, file_name_list=files_to_zip, zip_file_name=zip_file_name)

    response_data = {'success': True, 'data': {'zip_file_name': zip_file_url}, 'error': []}
    return Response(data=response_data)


def _save_output_files_in_django(output_files, user=None):
    output_files_in_django = {}

    # first delete if any of these output files already exist for the user
    for key, value in output_files.items():
        if user:
            file_to_delete = os.path.basename(value)
            # check if the output file is a shape file then we need to delete a matching zip file
            # as shapefiles are saved as zip files
            if file_to_delete.endswith('.shp'):
                file_to_delete = file_to_delete[:-4] + '.zip'
            delete_user_file(user, file_to_delete)

    for key, value in output_files.items():
        # check if it is a shape file
        ext = os.path.splitext(value)[1]
        if ext == '.shp':
            logger.debug('creating zip for shape files')
            value = create_shape_zip_file(value)

        user_file = UserFile(file=File(open(value, 'rb')))
        if user:
            user_file.user = user

        user_file.save()
        output_files_in_django[key] = current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
        logger.debug('django file url for the output file:' + user_file.file.url)

    return output_files_in_django



