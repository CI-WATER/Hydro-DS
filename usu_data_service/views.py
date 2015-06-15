from django.core.files import File

from rest_framework import permissions
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
from usu_data_service.serializers import *
from usu_data_service.models import *
from usu_data_service.utils import *
from usu_data_service.local_settings import *

WESTERN_US_DEM = os.path.join(STATIC_DATA_ROOT_PATH, 'subsetsource/nedWesternUS.tif')

funcs = {
          'rastersubset':
                {
                    'function_to_execute': get_raster_subset,
                    'file_inputs': [],  #{'input_raster': WESTERN_US_DEM}
                    'file_outputs': [{'output_raster': 'subset.tif'}],
                    'user_file_inputs': ['input_raster'],
                    'user_inputs': ['xmin', 'ymax', 'xmax', 'ymin'],
                    'validator': SubsetDEMRequestValidator
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

          'delineatewatershed':
                {
                    'function_to_execute': delineate_Watershed_TauDEM,
                    'file_inputs': [],
                    'file_outputs': [{'output_WS_raster': 'watershed.tif'}, {'output_Outlet_shpFile': 'moveout.shp'}],
                    'user_inputs': ['utmZone', 'streamThreshold', 'outletPointX', 'outletPointY'],
                    'user_file_inputs': ['input_DEM_raster'],
                    'validator': DelineateWatershedRequestValidator
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

          'projectshapefile':
               {
                    'function_to_execute': project_shapefile_UTM_NAD83,
                    'file_inputs': [],
                    'file_outputs': [{'output_shape_file': 'shape_proj.shp'}],
                    'user_inputs': ['utm_zone'],
                    'user_file_inputs': ['input_shape_file'],
                    'validator': ProjectShapeFileRequestValidator
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

        print('Executing python data service function:' + func)
        params = funcs.get(func, None)

        if not params:
            return Response({'failure': True, 'message': 'No such function {} is supported.'.format(func)})

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
                print('input_uuid_file_path_from_url_path:' + uuid_input_file_path)
            else:
                static_data_file_path = get_static_data_file_path(input_file)
                subprocparams[p] = static_data_file_path
                print('input_static_file_path:' + static_data_file_path)

        # execute the function
        result = params['function_to_execute'](**subprocparams)

        print(result)

        # process function output results
        data = []
        if result['success'] == 'True':
            user = request.user if request.user.is_authenticated() else None
            data = _save_output_files_in_django(output_files, user=user)
            response_data = {'success': True, 'data': data, 'error': []}
        else:
            response_data = {'success': False, 'data': data, 'error': result['message']}

        _delete_working_uuid_directory(uuid_file_path)

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

    file_url = _current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
    response_data = {'success': True, 'data': file_url, 'error': []}
    return Response(data=response_data)


@api_view(['GET'])
def show_my_files(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    user_files = []
    for user_file in UserFile.objects.filter(user=request.user).all():
        user_file_url = _current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
        user_files.append(user_file_url)

    response_data = {'success': True, 'data': user_files, 'error': []}
    return Response(data=response_data)


@api_view(['DELETE'])
def delete_my_file(request, filename):
    if not request.user.is_authenticated():
        raise NotAuthenticated()

    for user_file in UserFile.objects.filter(user=request.user).all():
        if user_file.file.name.split('/')[2] == filename:
            user_file.delete()
            print ("file deleted:" + filename)
            break

    else:
        raise NotFound()

    response_data = {'success': True, 'data': filename, 'error': []}
    return Response(data=response_data)

def _save_output_files_in_django(output_files, user=None):
    output_files_in_django = {}
    for key, value in output_files.items():
        # check if it is a shape file
        ext = os.path.splitext(value)[1]
        print("output_file_path:" + value)
        print("extension:" + ext)
        if ext == '.shp':
            print('creating zip for shape files')
            value = create_shape_zip_file(value)

        if user:
            file_to_delete = os.path.basename(value)
            delete_user_file(user, file_to_delete)

        user_file = UserFile(file=File(open(value, 'rb')))
        if user:
            user_file.user = user

        user_file.save()
        output_files_in_django[key] = _current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
        print ('file url:' + user_file.file.url)
    return output_files_in_django


def _delete_working_uuid_directory(dir_to_delete):
    import usu_data_service
    usu_data_service_root_path = os.path.dirname(usu_data_service.__file__)
    data_service_working_directory = os.path.join(usu_data_service_root_path, 'workspace')
    # make sure we are deleting the uid folder under the path "/...../workspace/"
    if dir_to_delete.startswith(data_service_working_directory):
        if not dir_to_delete.endswith(data_service_working_directory):
            shutil.rmtree(dir_to_delete)

    print ('cleanup working dir name:' + dir_to_delete)


def _current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    #from django.contrib.sites.models import Site
    current_site = 'hydro-ds.uwrl.usu.edu'
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port = getattr(settings, 'MY_SITE_PORT', '20199')
    url = '%s://%s' % (protocol, current_site)
    if port:
        url += ':%s' % port
    return url


