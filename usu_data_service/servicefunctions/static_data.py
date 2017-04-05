__author__ = 'pkdash'

import os
from collections import namedtuple
from usu_data_service.local_settings import *

DAYMET_ROOT_FILE_PATH = os.path.join(STATIC_DATA_ROOT_PATH, 'DaymetClimate')
NLDAS_ROOT_FILE_PATH = os.path.join(STATIC_DATA_ROOT_PATH, 'NLDASClimate')


startYear = 2005
endYear = 2015
#
# NLDAS Variable names and description
#APCPsfc_110_SFC_acc1h : hourly total precipitation (Kg/m^2 = mm/hr)
#TMP2m_110_HTGL : 2 m above ground temperature (K)
#PRESsfc_110_SFC : Surface pressure (Pa)
#UGRD10m_110_HTGL : 10 m above ground zonal wind speed (m/s)
#VGRD10m_110_HTGL : 10 m above ground meridional wind speed (m/s)
#SPFH2m_110_HTGL : 2 m above ground specific humidity (Kg/Kg)
#DLWRFsfc_110_SFC : LW Radiation flux downwards at surface (W/m^2)
#DSWRFsfc_110_SFC : SW Radiation flux downwards at surface (W/m^2)
"""monthly data--not used currently
#NLDASyear= ['NLDAS_FORA0125_H.A_Monthly_'+str(year) for year in range(startYear, endYear+1)]
#for year in NLDASyear:
#    NLDASlist += [year + month + '.nc' for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']]
"""

NLDASVars = ['APCPsfc_110_SFC_acc1h', 'TMP2m_110_HTGL', 'PRESsfc_110_SFC', 'UGRD10m_110_HTGL', 'VGRD10m_110_HTGL', 'SPFH2m_110_HTGL','DLWRFsfc_110_SFC', 'DSWRFsfc_110_SFC']
NLDASlist = []
for nlvar in NLDASVars:
    NLDASlist += ['NLDAS_FORA0125_H.A_' + nlvar + "_" + str(year) + ".nc" for year in range(startYear, endYear+1)]
#daymet
Daymetlist = []
DaymetVars = ['vp', 'tmin', 'tmax', 'srad', 'prcp']
####iterate through climate variables
for var in DaymetVars:
    Daymetlist += [var+'_'+str(year)+'.nc4' for year in range(startYear, endYear+1)]


def get_static_data_file_path(file_name):

    if file_name in Daymetlist:
        return os.path.join(DAYMET_ROOT_FILE_PATH,file_name)
    elif file_name in NLDASlist:
        return os.path.join(NLDAS_ROOT_FILE_PATH, file_name)
    elif file_name == 'nedWesternUS.tif':
        return os.path.join(STATIC_DATA_ROOT_PATH, 'subsetsource', 'nedWesternUS.tif')
    elif file_name == 'nlcd2011CONUS.tif':
        return os.path.join(STATIC_DATA_ROOT_PATH, 'nlcd2011CONUS', 'nlcd2011CONUS.tif')

    return None

#
# STATIC_FILE_NAME_PATH_DICT = {
#                               'prcp_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2010.nc4'),
#                               'prcp_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2011.nc4'),
#
#                               'prcp_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2010.nc4'),
#                               'prcp_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'prcp_2011.nc4'),
#                               'vp_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'vp_2010.nc4'),
#                               'vp_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'vp_2011.nc4'),
#                               'srad_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'srad_2010.nc4'),
#                               'srad_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'srad_2011.nc4'),
#                               'tmin_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmin_2010.nc4'),
#                               'tmin_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmin_2011.nc4'),
#                               'tmax_2010.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmax_2010.nc4'),
#                               'tmax_2011.nc4': os.path.join(DAYMET_ROOT_FILE_PATH, 'tmax_2011.nc4'),
#
#                               'nedWesternUS.tif': os.path.join(STATIC_DATA_ROOT_PATH, 'subsetsource', 'nedWesternUS.tif'),
#                               'nlcd2011CONUS.tif': os.path.join(STATIC_DATA_ROOT_PATH, 'nlcd2011CONUS', 'nlcd2011CONUS.tif'),
#                               }

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




# def get_static_data_file_path(file_name):
#
#
#     if file_name in STATIC_FILE_NAME_PATH_DICT:
#         return STATIC_FILE_NAME_PATH_DICT[file_name]
#
#     return None

