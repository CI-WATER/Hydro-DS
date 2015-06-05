__author__ = 'pkdash'

import os
from collections import namedtuple
from usu_data_service.local_settings import *

DAYMET_ROOT_FILE_PATH = os.path.join(STATIC_DATA_ROOT_PATH, 'DaymetClimate')

STATIC_FILE_NAME_PATH_DICT = {'prcp_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2010.nc4'),
                              'prcp_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2011.nc4'),
                              'vp_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'vp_2010.nc4'),
                              'vp_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'vp_2011.nc4'),
                              'srad_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'srad_2010.nc4'),
                              'srad_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'srad_2011.nc4'),
                              'tmin_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmin_2010.nc4'),
                              'tmin_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmin_2011.nc4'),
                              'tmax_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmax_2010.nc4'),
                              'tmax_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmax_2011.nc4'),
                              'nedWesternUS.tif': os.path.join(STATIC_DATA_ROOT_PATH, 'subsetsource', 'nedWesternUS.tif'),
                              'nlcd2011CONUS.tif': os.path.join(STATIC_DATA_ROOT_PATH, 'nlcd2011CONUS', 'nlcd2011CONUS.tif'),
                              }

def get_static_data_files_info():
    static_file_info_object_list = _generate_static_data_file_info_object_list()
    static_files_info_list = []
    for info_obj in static_file_info_object_list:
        static_files_info_list.append(info_obj.__dict__)

    return static_files_info_list


def _generate_static_data_file_info_object_list():
    StaticDataFileInfo = namedtuple('StaticDataFileInfo',
                                'variables time_period spatial_extent data_source data_format file_name')

    static_file_list = []

    # DEM data file
    static_file = StaticDataFileInfo(variables=[{'name': 'DEM', 'description': 'Digital Elevation Model', 'unit': 'N/A'}],
                                     time_period='N/A',
                                     spatial_extent='Western USA',
                                     data_source='USGS',
                                     data_format='Tiff',
                                     file_name='nedWesternUS.tif')

    static_file_list.append(static_file)

    # NLCD data file
    static_file = StaticDataFileInfo(variables=[{'name': 'NLCD', 'description': 'National Land Cover Dataset', 'unit': 'N/A'}],
                                     time_period='N/A',
                                     spatial_extent='Whole USA',
                                     data_source='USGS',
                                     data_format='Tiff',
                                     file_name='nlcd2011CONUS.tif')

    static_file_list.append(static_file)

    # daymet data files
    for year in ('2010', '2011'):
        static_file = StaticDataFileInfo(variables=[{'name': 'prcp', 'description': 'Precipitation', 'unit': 'mm/day'}],
                                     time_period=int(year),
                                     spatial_extent='Whole USA',
                                     data_source='Daymet',
                                     data_format='NetCDF',
                                     file_name='prcp_{year}.nc4'.format(year=year))

        static_file_list.append(static_file)

    for year in ('2010', '2011'):
        static_file = StaticDataFileInfo(variables=[{'name': 'vp', 'description': 'Vapor pressure', 'unit': 'Pa'}],
                                     time_period=int(year),
                                     spatial_extent='Whole USA',
                                     data_source='Daymet',
                                     data_format='NetCDF',
                                     file_name='vp_{year}.nc4'.format(year=year))

        static_file_list.append(static_file)

    for year in ('2010', '2011'):
        static_file = StaticDataFileInfo(variables=[{'name': 'srad', 'description': 'Solar radiation', 'unit': 'W/m^2'}],
                                     time_period=int(year),
                                     spatial_extent='Whole USA',
                                     data_source='Daymet',
                                     data_format='NetCDF',
                                     file_name='srad_{year}.nc4'.format(year=year))

        static_file_list.append(static_file)

    for year in ('2010', '2011'):
        for var in ('tmin', 'tmax'):
            if var == 'tmin':
                var_description = 'Daily minimum temperature'
            else:
                var_description = 'Daily maximum temperature'

            static_file = StaticDataFileInfo(variables=[{'name': var, 'description': '%s' % var_description, 'unit': 'deg C'}],
                                         time_period=int(year),
                                         spatial_extent='Whole USA',
                                         data_source='Daymet',
                                         data_format='NetCDF',
                                         file_name='{variable}_{year}.nc4'.format(variable=var, year=year))

            static_file_list.append(static_file)

    return static_file_list


def get_static_data_file_path(file_name):
    if file_name in STATIC_FILE_NAME_PATH_DICT:
        return STATIC_FILE_NAME_PATH_DICT[file_name]

    return None