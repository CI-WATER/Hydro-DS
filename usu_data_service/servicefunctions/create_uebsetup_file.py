"""
This is used to create hydrogate.py and ueb_setup.py files

"""

from usu_data_service.servicefunctions.ueb_setup_temp_list import ueb_input_template_list
from usu_data_service.servicefunctions.hydrogate_temp_list import hydrogate_template_list
import os


def generate_ueb_input_workflow_file(uuid_file_path,
                                    topY, bottomY, leftX, rightX,
                                    lat_outlet, lon_outlet,
                                    streamThreshold, watershedName,
                                    epsgCode, startDateTime, endDateTime, dx, dy,
                                    dxRes, dyRes, usic, wsic, tic, wcic, ts_last,
                                    ueb_input_template=ueb_input_template_list,
                                    **kwargs):
    try:

        # set epsgCode
        ueb_input_template[12] = 'epsgCode = ' + str(epsgCode)

        # set grid cell sizes (m) for reprojection
        ueb_input_template[15] = 'dx = ' + str(dx)
        ueb_input_template[16] = 'dy = ' + str(dy)

        # set outlet point for watershed delineation (optional)
        ueb_input_template[19] = 'lat_outlet = ' + str(lat_outlet)
        ueb_input_template[20] = 'lon_outlet = ' + str(lon_outlet)

        # set spatial bounding box for watershed delineation
        ueb_input_template[23] = 'leftX = ' + str(leftX)
        ueb_input_template[24] = 'topY = ' + str(topY)
        ueb_input_template[25] = 'rightX = ' + str(rightX)
        ueb_input_template[26] = 'bottomY = ' + str(bottomY)

        # set stream threshold for watershed delineation
        ueb_input_template[29] = 'streamThreshold = ' + str(streamThreshold)

        # set watershed name
        ueb_input_template[32] = 'watershedName = "{}"'.format(watershedName if watershedName else 'myWatershed')

        # set cell spacing for subsampled UEB model (m)
        ueb_input_template[35] = 'dxRes = ' + str(dxRes)
        ueb_input_template[36] = 'dyRes = ' + str(dyRes)

        # set model input start date
        ueb_input_template[39] = 'startDateTime = "{} 0" '.format(startDateTime)
        ueb_input_template[40] = 'endDateTime = "{} 0"'.format(endDateTime)

        # set site initial condition
        ueb_input_template[44] = 'usic = ' + str(usic)
        ueb_input_template[46] = 'wsic = ' + str(wsic)
        ueb_input_template[48] = 'tic = ' + str(tic)
        ueb_input_template[50] = 'wcic = ' + str(wcic)
        ueb_input_template[52] = 'ts_last = ' + str(ts_last)

        # write as a new file as ueb_input_setup.py
        setup_file_name = 'ueb_setup.py'
        setup_file_path = os.path.join(uuid_file_path, setup_file_name)

        with open(setup_file_path, 'w') as setup_file:
            setup_file.write("\n".join(ueb_input_template))

        # write as a new file as hydrogate.py
        hydrogate_file_path = os.path.join(uuid_file_path, 'hydrogate.py')
        with open(hydrogate_file_path, 'w') as hydrogate_file:
            hydrogate_file.write("\n".join(hydrogate_template_list))

        result = [setup_file_path, hydrogate_file_path]

    except Exception as e:
        result = []

    return result



# example
# result = generate_ueb_input_workflow_file(uuid_file_path=os.getcwd(),
#                                     topY=42.1107, bottomY=41.6642, leftX=-111.817, rightX=-111.457,
#                                     lat_outlet=41.7436, lon_outlet=-111.7838,
#                                     streamThreshold=1000, watershedName='logan',
#                                     epsgCode=26912, startDateTime='2009/12/01', endDateTime='2010/02/01',
#                                     dx=30, dy=30,
#                                     dxRes=100, dyRes=100, usic=1,wsic=2,tic=3,wcic=4,ts_last=5)