__author__ = 'pkdash'


def get_capabilites():
    capabilities = []
    raster_subset_bbox_capability = {'service_name': 'subsetrastertobbox', 'description': 'subset raster to bounding box'}
    capabilities.append(raster_subset_bbox_capability)

    raster_subset_ref_capability = {'service_name': 'subsetrastertoreference', 'description': 'subset raster to reference raster'}
    capabilities.append(raster_subset_ref_capability)
    return capabilities


def get_service_info(service_name):
    supported_services = []
    raster_subset_box_info = {'subsetrastertobbox': [{'parameters': [
                                                               _get_param_dict(name='xmin',
                                                                               description='x-coordinate of the left-top corner of the bounding box',
                                                                               required=True,
                                                                               type='float'),

                                                               _get_param_dict(name='xmax',
                                                                               description='x-coordinate of the right-bottom corner of the bounding box',
                                                                               required=True,
                                                                               type='float'),

                                                               _get_param_dict(name='ymin',
                                                                               description='y-coordinate of the right-bottom corner of the bounding box',
                                                                               required=True,
                                                                               type='float'),

                                                               _get_param_dict(name='ymax',
                                                                               description='y-coordinate of the left-top corner of the bounding box',
                                                                               required=True,
                                                                               type='float')
                                                             ]
                                               },
                                              _get_json_response_format(data_dict={'output_raster': 'url of the output raster file'})]
                            }

    supported_services.append(raster_subset_box_info)

    raster_subset_ref_info = {'subsetrastertoreference': [{'parameters': [
                                                                            _get_param_dict(name='input_netcdf',
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
    supported_services.append(raster_subset_ref_info)


    subset_netcdf_ref_info = {'subsetnetcdftoreference': [{'parameters': [
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

    supported_services.append(subset_netcdf_ref_info)

    subset_netcdf_by_time_info = {'subsetnetcdfbytime': [{'parameters': [
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

    supported_services.append(subset_netcdf_by_time_info)

    for dict_item in supported_services:
        if service_name in dict_item:
            return dict_item

    return None

def _get_param_dict(name, description, required, type):
    return {'name': name, 'description': description, 'required': required, 'type': type}


def _get_json_response_format(data_dict):
    return {'response_JSON_data_format': {'success': True, 'data': data_dict, 'error': []}}