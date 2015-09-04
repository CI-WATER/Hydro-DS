__author__ = 'pkdash'

import collections


def get_capabilites():
    capabilities = []
    capabilities.append(_get_capability_dict(service_name='subsetrastertobbox',
                                             description='subset raster to bounding box'))

    capabilities.append(_get_capability_dict(service_name='subsetrastertoreference',
                                             description='subset raster to a reference raster'))

    capabilities.append(_get_capability_dict(service_name='subsetnetcdftoreference',
                                             description='subset NetCDF data to a reference raster'))

    capabilities.append(_get_capability_dict(service_name='subsetnetcdfbytime',
                                             description='subset NetCDF data by time dimension'))

    capabilities.append(_get_capability_dict(service_name='delineatewatershedatxy',
                                             description='delineate watershed at the outlet point (X, Y)'))

    capabilities.append(_get_capability_dict(service_name='delineatewatershedatshape',
                                             description='delineate watershed at the outlet shape'))

    capabilities.append(_get_capability_dict(service_name='createoutletshapefile',
                                             description='create an outlet shapefile from a given outlet point'))

    capabilities.append(_get_capability_dict(service_name='projectshapefileutm',
                                             description='project a shapefile based on UTM zone'))

    capabilities.append(_get_capability_dict(service_name='projectshapefileepsg',
                                             description='project a shapefile based on EPSG code'))

    capabilities.append(_get_capability_dict(service_name='projectraster',
                                             description='project a raster based on UTM zone'))

    capabilities.append(_get_capability_dict(service_name='projectandcliprastertoreference',
                                             description='project and clip a raster based on a reference raster'))


    capabilities.append(_get_capability_dict(service_name='projectresamplerasterutm',
                                             description='project and resample a raster based on UTM zone and cell size'))

    capabilities.append(_get_capability_dict(service_name='projectresamplerasterepsg',
                                             description='project and resample a raster based on EPSG code and cell size'))

    capabilities.append(_get_capability_dict(service_name='projectnetcdf',
                                             description='project NetCDF data based on UTM zone'))

    capabilities.append(_get_capability_dict(service_name='computerasteraspect',
                                             description='creates a raster with aspect data'))

    capabilities.append(_get_capability_dict(service_name='computerasterslope',
                                             description='creates a raster with slope data'))

    capabilities.append(_get_capability_dict(service_name='rastertonetcdfrenamevariable',
                                             description='creates data in NetCDF format from raster data with variable renaming of the NetCDF data'))

    capabilities.append(_get_capability_dict(service_name='rastertonetcdf',
                                             description='creates data in NetCDF format from raster data'))

    capabilities.append(_get_capability_dict(service_name='combinerasters',
                                             description='combines two raster datasets'))

    capabilities.append(_get_capability_dict(service_name='resampleraster',
                                             description='resample raster data to the specified grid cell size'))

    capabilities.append(_get_capability_dict(service_name='resamplenetcdftoreferencenetcdf',
                                             description='resample NetCDF dataset based on a reference NetCDF dataset'))

    capabilities.append(_get_capability_dict(service_name='reversenetcdfyaxisandrenamevariable',
                                             description='reverse NetCDF dataset for the Y-axix and rename dataset variable'))

    capabilities.append(_get_capability_dict(service_name='projectsubsetresamplenetcdftoreferencenetcdf',
                                             description='project, subset and resample NetCDF dataset based on a reference NetCDF dataset'))

    capabilities.append(_get_capability_dict(service_name='subsetprojectresamplerasterutm',
                                             description='subset, project and resample raster dataset based on UTM zone'))

    capabilities.append(_get_capability_dict(service_name='subsetprojectresamplerasterepsg',
                                             description='subset, project and resample raster dataset based on EPSG code'))

    capabilities.append(_get_capability_dict(service_name='concatenatenetcdf',
                                             description='join two sets of NetCDF data'))

    capabilities.append(_get_capability_dict(service_name='getcanopyvariable',
                                             description='get canopy variable specific data in NetCDF format'))

    capabilities.append(_get_capability_dict(service_name='convertnetcdfunits',
                                             description='convert NetCDF data units'))

    capabilities.append(_get_capability_dict(service_name='netcdfrenamevariable',
                                             description='rename NetCDF data variable'))

    capabilities.append(_get_capability_dict(service_name='createhydroshareresource',
                                             description='create a resource in HydroShare'))

    capabilities.append(_get_capability_dict(service_name='listsupporteddatasources',
                                             description='list data supported by HydroDS'))

    capabilities.append(_get_capability_dict(service_name='uploadfile',
                                             description='uploads a file to HydroDS as a user file'))

    capabilities.append(_get_capability_dict(service_name='listfiles',
                                             description='list all files the user have on HydroDS'))

    capabilities.append(_get_capability_dict(service_name='deletefile',
                                             description="delete a user file from HydroDS"))

    capabilities.append(_get_capability_dict(service_name='zipfiles',
                                             description="zip a set of user files on HydroDS"))
    return capabilities


def get_service_info(service_name):
    #supported_services = ['subsetrastertobbox', 'subsetrastertoreference', 'subsetnetcdftoreference']

    services_info_dict = {}
    #service_info_helper_obj = ServiceInfoHelper()

    # for service in supported_services:
    #     services_info_dict[service] = getattr(service_info_helper_obj, 'get_%s_info' % service)



    services_info_dict['subsetrastertobbox'] = _get_susbsetrastertobbox_info
    services_info_dict['subsetrastertoreference'] = _get_subsetrastertoreference_info
    services_info_dict['subsetnetcdftoreference'] = _get_subsetnetcdftoreference_info
    services_info_dict['subsetnetcdfbytime'] = _get_subsetnetcdfbytime_info
    services_info_dict['delineatewatershedatxy'] = _get_delineatewatershedatxy_info
    services_info_dict['delineatewatershedatshape'] = _get_delineatewatershedatshape_info
    services_info_dict['createoutletshapefile'] = _get_createoutletshapefile_info
    services_info_dict['projectshapefileutm'] = _get_projectshapefileutm_info
    services_info_dict['projectshapefileepsg'] = _get_projectshapefileepsg_info
    services_info_dict['projectraster'] = _get_projectraster_info
    services_info_dict['projectandcliprastertoreference'] = _get_projectandcliprastertoreference_info
    services_info_dict['projectresamplerasterutm'] = _get_projectresamplerasterutm_info
    services_info_dict['projectresamplerasterepsg'] =_get_projectresamplerasterepsg_info
    services_info_dict['projectnetcdf'] = _get_projectnetcdf_info
    services_info_dict['computerasteraspect'] = _get_computerasteraspect_info
    services_info_dict['computerasterslope'] = _get_computerasterslope_info
    services_info_dict['rastertonetcdfrenamevariable'] = _get_rastertonetcdfrenamevariable_info
    services_info_dict['rastertonetcdf'] = _get_rastertonetcdf_info
    services_info_dict['combinerasters'] = _get_combinerasters_info
    services_info_dict['resampleraster'] = _get_resampleraster_info
    services_info_dict['resamplenetcdftoreferencenetcdf'] = _get_resamplenetcdftoreferencenetcdf_info
    services_info_dict['reversenetcdfyaxisandrenamevariable'] = _get_reversenetcdfyaxisandrenamevariable_info
    services_info_dict['projectsubsetresamplenetcdftoreferencenetcdf'] = _get_projectsubsetresamplenetcdftoreferencenetcdf_info
    services_info_dict['subsetprojectresamplerasterutm'] = _get_subsetprojectresamplerasterutm_info
    services_info_dict['subsetprojectresamplerasterepsg'] = _get_subsetprojectresamplerasterepsg_info
    services_info_dict['concatenatenetcdf'] = _get_concatenatenetcdf_info
    services_info_dict['getcanopyvariable'] = _get_getcanopyvariable_info
    services_info_dict['convertnetcdfunits']= _get_convertnetcdfunits_info
    services_info_dict['netcdfrenamevariable'] = _get_netcdfrenamevariable_info
    services_info_dict['createhydroshareresource']= _get_createhydroshareresource_info
    services_info_dict['listsupporteddatasources'] = _get_listsupporteddatasources_info
    services_info_dict['uploadfile'] = _get_uploadfile_info
    services_info_dict['listfiles'] = _get_listfiles_info
    services_info_dict['deletefile'] = _get_deletefile_info
    services_info_dict['zipfiles'] = _get_zipfiles_info

    if service_name in services_info_dict:
        return services_info_dict[service_name]()
    else:
        return None


def _get_param_dict(name, description, required, type):
    ordered_dict = collections.OrderedDict()
    ordered_dict['name'] = name
    ordered_dict['description'] = description
    ordered_dict['type'] = type
    ordered_dict['required'] = required
    return ordered_dict


def _get_json_response_format(data_dict):
    return {'response_JSON_data_format': {'success': True, 'data': data_dict, 'error': []}}


def _get_service_info_url(service_name):
    return "http://hydro-ds.uwrl.usu.edu/api/dataservice/info/{service_name}".format(service_name=service_name)

def _get_end_point(url_sub_path):
    return "http://hydro-ds.uwrl.usu.edu/api/dataservice/{url_sub_path}".format(url_sub_path=url_sub_path)

def _get_capability_dict(service_name, description):
    return {'service_name': service_name, 'description': description,
            'service_info_url': _get_service_info_url(service_name)}


def _get_susbsetrastertobbox_info():
    service_name = 'subsetrastertobbox'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                           _get_param_dict(name='xmin',
                                                           description='X-coordinate of the left-top corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='xmax',
                                                           description='X-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymin',
                                                           description='Y-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymax',
                                                           description='Y-coordinate of the left-top corner of the bounding box',
                                                           required=True,
                                                           type='float')
                                         ]
                           },
                          _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
           }


def _get_subsetrastertoreference_info():
    service_name = 'subsetrastertoreference'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file to be subsetted',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_raster',
                                                            description='HydroDS url file path for a user owned raster file to be used as a reference for subsetting',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                        },
                        _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

            }


def _get_subsetnetcdftoreference_info():
    service_name = 'subsetnetcdftoreference'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for a user owned NetCDF file or file name of a HydroDS supported NetCDF data resource that needs to be subsetted',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_raster',
                                                            description='HydroDS url file path for a user owned raster file to be used as a reference for subsetting',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                        },
                        _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
            }


def _get_subsetnetcdfbytime_info():
    service_name = 'subsetnetcdfbytime'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for a user owned NetCDF file that needs to be subsetted',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='time_dim_name',
                                                            description='name of the time dimension in the input NetCDF file',
                                                            required=True,
                                                            type='string'),
                                            _get_param_dict(name='start_time_index',
                                                            description='day of data start year',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='end_time_index',
                                                            description='day of data end year',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')

                                        ]
                        },
                        _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
            }


def _get_delineatewatershedatxy_info():
    service_name = 'delineatewatershedatxy'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_DEM_raster',
                                                            description='HydroDS url file path for a user owned raster file that needs to be delineated',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='epsg_code',
                                                            description='EPSG code to use for projection',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='stream_threshold',
                                                            description='stream threshold to use for delineation',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='outlet_point_x',
                                                            description='X-coordinate of the outlet point',
                                                            required=True,
                                                            type='float'),

                                            _get_param_dict(name='outlet_point_y',
                                                            description='Y-coordinate of the outlet point',
                                                            required=True,
                                                            type='float'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output watershed raster',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_outlet_shapefile',
                                                            description='name for the output outlet shapefile (generated output shapefile will be saved as a zip file)',
                                                            required=True,
                                                            type='string')

                                        ]
                        },
                        _get_json_response_format(data_dict={'output_raster': 'url of the output raster file', 'output_outlet_shapefile': 'url of the output outlet shapefile'})]
            }


def _get_delineatewatershedatshape_info():
    service_name = 'delineatewatershedatshape'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_DEM_raster',
                                                            description='HydroDS url file path for a user owned raster file that needs to be delineated',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='stream_threshold',
                                                            description='stream threshold to use for delineation',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='input_outlet_shapefile',
                                                            description='HydroDS url file path for a user owned shapefile for the outlet',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output watershed raster',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_outlet_shapefile',
                                                            description='name for the output outlet shapefile (generated output shapefile will be saved as a zip file)',
                                                            required=True,
                                                            type='string')

                                        ]
                        },
                        _get_json_response_format(data_dict={'output_raster': 'url of the output raster file', 'output_outlet_shapefile': 'url of the output outlet shapefile'})]
          }


def _get_createoutletshapefile_info():
    service_name = 'createoutletshapefile'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='outletPointX',
                                                            description='X-coordinate of the outlet point',
                                                            required=True,
                                                            type='float'),

                                            _get_param_dict(name='outletPointY',
                                                            description='Y-coordinate of the outlet point',
                                                            required=True,
                                                            type='float'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output watershed raster',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_shapefile_name',
                                                            description='name for the output outlet shapefile (generated output shapefile will be saved as a zip file)',
                                                            required=True,
                                                            type='string')

                                        ]
                        },
                        _get_json_response_format(data_dict={'output_shapefile_name': 'url of the output outlet shapefile'})]
         }


def _get_projectshapefileutm_info():
    service_name = 'projectshapefileutm'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_shape_file',
                                                            description='HydroDS url file path for a user owned shapefile file that needs to be projected',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='utm_zone',
                                                            description='UTM zone value to use in projection',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='output_shape_file',
                                                            description='name for the output shapefile (generated output shapefile will be saved as a zip file)',
                                                            required=True,
                                                            type='string')

                                          ]
                            },
                            _get_json_response_format(data_dict={'output_shape_file':'url of the output shapefile'})]
          }


def _get_projectshapefileepsg_info():
    service_name = 'projectshapefileepsg'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_shape_file',
                                                            description='HydroDS url file path for a user owned shapefile file that needs to be projected',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='epsg_code',
                                                            description='EPSG code to use in projection',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='output_shape_file',
                                                            description='name for the output shapefile (generated output shapefile will be saved as a zip file)',
                                                            required=True,
                                                            type='string')

                                          ]
                            },
                            _get_json_response_format(data_dict={'output_shape_file':'url of the output shapefile'})]
          }


def _get_projectraster_info():
    service_name = 'projectraster'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file to be projected',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='utm_zone',
                                                            description='UTM zone value to use in projection',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

          }


def _get_projectandcliprastertoreference_info():
    service_name = 'projectandcliprastertoreference'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file to be projected/clipped',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_raster',
                                                            description='HydroDS url file path for a user owned raster file to be used as a reference for projecting/clipping',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                        },
                        _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

            }


def _get_projectresamplerasterutm_info():
    service_name = 'projectresamplerasterutm'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                           _get_param_dict(name='input_raster',
                                                           description='HydroDS url file path for a user owned raster file to be projected/resampled',
                                                           required=True,
                                                           type='string'),

                                           _get_param_dict(name='utm_zone',
                                                           description='UTM zone value to use in projection',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dx',
                                                           description='grid cell width',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dy',
                                                           description='grid cell height',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='resample',
                                                           description="resample method (e.g., near, bilinear) (default is 'near')",
                                                           required=False,
                                                           type='string'),

                                           _get_param_dict(name='output_raster',
                                                           description='name for the output raster',
                                                           required=True,
                                                           type='string')

                                         ]
                           },
                          _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
            }


def _get_projectresamplerasterepsg_info():
    service_name = 'projectresamplerasterepsg'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                           _get_param_dict(name='input_raster',
                                                           description='HydroDS url file path for a user owned raster file to be projected/resampled',
                                                           required=True,
                                                           type='string'),

                                           _get_param_dict(name='epsg_code',
                                                           description='EPSG code to use in projection',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dx',
                                                           description='grid cell width',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dy',
                                                           description='grid cell height',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='resample',
                                                           description="resample method (e.g., near, bilinear) (default is 'near')",
                                                           required=False,
                                                           type='string'),

                                           _get_param_dict(name='output_raster',
                                                           description='name for the output raster',
                                                           required=True,
                                                           type='string')

                                         ]
                           },
                          _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
            }


def _get_projectnetcdf_info():
    service_name = 'projectnetcdf'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for a user owned NetCDF file to be projected',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='utm_zone',
                                                            description='UTM zone value to use in projection',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='variable_name',
                                                            description="name of the data variable for which data to be projected",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]

          }


def _get_computerasteraspect_info():
    service_name = 'computerasteraspect'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file from which aspect data to be computed',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

            }


def _get_computerasterslope_info():
    service_name = 'computerasterslope'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file from which slope data to be computed',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

         }


def _get_rastertonetcdfrenamevariable_info():
    service_name = 'rastertonetcdfrenamevariable'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file from which data to be generated in NetCDF format',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_varname',
                                                            description="name for the output NetCDF data variable (default is 'Band1')",
                                                            required=False,
                                                            type='string'),

                                            _get_param_dict(name='increasing_x',
                                                            description="output NetCDf data to be ordered in the direction of increasing X-coordinate (default is False)",
                                                            required=False,
                                                            type='bool'),

                                            _get_param_dict(name='increasing_y',
                                                            description="output NetCDf data to be ordered in the direction of increasing Y-coordinate (default is False)",
                                                            required=False,
                                                            type='bool'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]

         }


def _get_rastertonetcdf_info():
    service_name = 'rastertonetcdf'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file from which data to be generated in NetCDF format',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]

          }


def _get_resampleraster_info():
    service_name = 'resampleraster'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster',
                                                            description='HydroDS url file path for a user owned raster file to be resampled',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='dx',
                                                            description='grid cell width',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='dy',
                                                            description='grid cell height',
                                                            required=True,
                                                            type='integer'),

                                            _get_param_dict(name='resample',
                                                            description="resample method (e.g., near, bilinear) (default is 'near')",
                                                            required=False,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]

          }


def _get_combinerasters_info():
    service_name = 'combinerasters'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_raster1',
                                                            description='HydroDS url file path for the first user owned raster file to be joined',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='input_raster2',
                                                            description='HydroDS url file path for the second user owned raster file to be joined',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_raster',
                                                            description='name for the output raster file',
                                                            required=True,
                                                            type='string')
                                        ]
                            },
                             _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
          }


def _get_resamplenetcdftoreferencenetcdf_info():
    service_name = 'resamplenetcdftoreferencenetcdf'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to be resampled',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to be used as a reference for resampling',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='variable_name',
                                                            description="name of the data variable for which data to be resampled",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                            },
                            _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_reversenetcdfyaxisandrenamevariable_info():
    service_name = 'reversenetcdfyaxisandrenamevariable'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for the NetCDF file for which data ordering to be reversed',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to be used as a reference for resampling',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='input_varname',
                                                            description="name of the data variable for which data to be reversed",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_varname',
                                                            description="variable name for the output data",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                            },
                            _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_projectsubsetresamplenetcdftoreferencenetcdf_info():
    service_name = 'projectsubsetresamplenetcdftoreferencenetcdf'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to be projected, subsetted and resampled',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='reference_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to be used as a reference for projecting, subsetting and resampling',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='variable_name',
                                                            description="name of the data variable for which data to be projected, subsetted and resampled",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                            },
                            _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_subsetprojectresamplerasterutm_info():
    service_name = 'subsetprojectresamplerasterutm'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                           _get_param_dict(name='input_raster',
                                                           description='HydroDS url file path for a user owned raster file to be projected/resampled',
                                                           required=True,
                                                           type='string'),

                                           _get_param_dict(name='utm_zone',
                                                           description='UTM zone value to use in projection',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='xmax',
                                                           description='X-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymin',
                                                           description='Y-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymax',
                                                           description='Y-coordinate of the left-top corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='dx',
                                                           description='grid cell width',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dy',
                                                           description='grid cell height',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='resample',
                                                           description="resample method (e.g., near, bilinear) (default is 'near')",
                                                           required=False,
                                                           type='string'),

                                           _get_param_dict(name='output_raster',
                                                           description='name for the output raster',
                                                           required=True,
                                                           type='string')

                                         ]
                           },
                          _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
           }


def _get_subsetprojectresamplerasterepsg_info():
    service_name = 'subsetprojectresamplerasterepsg'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                           _get_param_dict(name='input_raster',
                                                           description='HydroDS url file path for a user owned raster file to be projected/resampled',
                                                           required=True,
                                                           type='string'),

                                           _get_param_dict(name='epsg_code',
                                                           description='EPSG code to use in projection',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='xmax',
                                                           description='X-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymin',
                                                           description='Y-coordinate of the right-bottom corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='ymax',
                                                           description='Y-coordinate of the left-top corner of the bounding box',
                                                           required=True,
                                                           type='float'),

                                           _get_param_dict(name='dx',
                                                           description='grid cell width',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='dy',
                                                           description='grid cell height',
                                                           required=True,
                                                           type='integer'),

                                           _get_param_dict(name='resample',
                                                           description="resample method (e.g., near, bilinear) (default is 'near')",
                                                           required=False,
                                                           type='string'),

                                           _get_param_dict(name='output_raster',
                                                           description='name for the output raster',
                                                           required=True,
                                                           type='string')

                                         ]
                                       },
                                      _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
           }


def _get_concatenatenetcdf_info():
    service_name = 'concatenatenetcdf'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf1',
                                                            description='HydroDS url file path for the first user owned NetCDF file to be joined',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='input_netcdf2',
                                                            description='HydroDS url file path for the second user owned NetCDF file to be joined',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_getcanopyvariable_info():
    service_name = 'getcanopyvariable'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='in_NLCDraster',
                                                            description='HydroDS url file path for the NLCD raster dataset from which canopy variable specific data to be generated in NetCDF format',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='variable_name',
                                                            description="name of the canopy variable for which data to be generated",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_convertnetcdfunits_info():
    service_name = 'convertnetcdfunits'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for the NetCDF file to for which data units to be converted',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='variable_name',
                                                            description="name of the data variable for which data units to be converted",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='variable_new_units',
                                                            description='data units name for the converted data',
                                                            required=False,
                                                            type='string'),

                                            _get_param_dict(name='multiplier_factor',
                                                            description='data units conversion factor (default is 1)',
                                                            required=False,
                                                            type='float'),

                                            _get_param_dict(name='offset',
                                                            description='additive factor (default is 0)',
                                                            required=False,
                                                            type='float'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                                    },
                                    _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_netcdfrenamevariable_info():
    service_name = 'netcdfrenamevariable'
    return {service_name: [{'end_point': _get_end_point(service_name), 'http_method': 'GET',
                            'parameters': [
                                            _get_param_dict(name='input_netcdf',
                                                            description='HydroDS url file path for the NetCDF file for which data variable to be renamed',
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='input_varname',
                                                            description="name of the data variable to be renamed",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_varname',
                                                            description="new name for the data variable",
                                                            required=True,
                                                            type='string'),

                                            _get_param_dict(name='output_netcdf',
                                                            description='name for the output NetCDF file',
                                                            required=True,
                                                            type='string')
                                        ]
                            },
                            _get_json_response_format(data_dict={'output_netcdf': 'url of the output NetCDF file'})]
          }


def _get_createhydroshareresource_info():
    return {'createhydroshareresource': [{'end_point': _get_end_point('hydroshare/createresource'), 'http_method': 'GET',
                                          'parameters': [
                                                        _get_param_dict(name='hs_username',
                                                                        description='username for HydroShare',
                                                                        required=True,
                                                                        type='string'),

                                                        _get_param_dict(name='hs_password',
                                                                        description="password for HydroShare",
                                                                        required=True,
                                                                        type='string'),

                                                        _get_param_dict(name='file_name',
                                                                        description='HydroDS user owned file name for the file to be uploaded to HydroShare for creating a resource',
                                                                        required=True,
                                                                        type='string'),

                                                        _get_param_dict(name='resource_type',
                                                                        description='HydroShare resource type name',
                                                                        required=True,
                                                                        type='string'),

                                                        _get_param_dict(name='title',
                                                                        description='title for the HydroShare resource',
                                                                        required=False,
                                                                        type='string'),

                                                        _get_param_dict(name='abstract',
                                                                        description='abstract for the HydroShare resource',
                                                                        required=False,
                                                                        type='string'),

                                                        _get_param_dict(name='keywords',
                                                                        description='list of keywords for the HydroShare resource',
                                                                        required=False,
                                                                        type='string')

                                                    ]
                                        },

                                        _get_json_response_format(data_dict={'resource_d': 'HydroShare resource id', 'resource_type': 'HydroShare resource type'})]
          }


def _get_listsupporteddatasources_info():
    return {'listsupporteddatasources': [{'parameters': [], 'end_point': _get_end_point('showstaticdata/info'), 'http_method': 'GET'
                                        },
                                        _get_json_response_format(data_dict=[{'variables': [{'name': 'name of the data variable', 'description': 'description of the variable', 'unit': 'unit name'},
                                                                                            {'name': 'name of the data variable', 'description': 'description of the variable', 'unit': 'unit name'},
                                                                                            {'...'}],

                                                                             'time_period': 'data time period', 'spatial_extent': 'data region', 'data_source': 'source of data',
                                                                             'data_format': 'format of the data', 'file_name': 'name of the file as stored in HydroDS'
                                                                             }]
                                                                  )]
          }


def _get_uploadfile_info():
    return {'uploadfile': [{'parameters': [], 'end_point': _get_end_point('myfiles/upload'), 'http_method': 'POST'
                                        },
                                        _get_json_response_format(data_dict='url of the uploaded file'
                                                                  )]
          }


def _get_listfiles_info():
    return {'listfiles': [{'parameters': [], 'end_point': _get_end_point('myfiles/list'), 'http_method': 'GET'
                                        },
                                        _get_json_response_format(data_dict='list of file urls'
                                                                  )]
          }


def _get_deletefile_info():
    return {'deletefile': [{'parameters': [{'filename': 'name of the file to delete '}], 'end_point': _get_end_point('myfiles/delete'), 'http_method': 'DELETE'
                                        },
                                        _get_json_response_format(data_dict='name of the deleted file'
                                                                  )]
          }


def _get_zipfiles_info():
    return {'zipfiles': [{'parameters': [{'file_names': 'list of comma separated file names for files to zip',
                                          'zip_file_name': 'name of the zipped file'}],
                          'end_point': _get_end_point('myfiles/zip'),
                          'http_method': 'GET'
                                        },
                                        _get_json_response_format(data_dict={'zip_file_name': 'url of the zipped file'}
                                                                  )]
          }