"""
This is used to create the model parameter files
"""
from datetime import datetime
import os
import collections

file_contents_dict = {
    'control.dat': ['Utah Energy Balance Grid Model Driver ', 'param.dat', 'siteinitial.dat', 'inputcontrol.dat', 'outputcontrol.dat', 'aggout.nc ', 'watershed.nc', 'watershed y x', '2010 10 01 12.0    ', '2011 05 30 12.0    ', '6.0', '0.0', '1', '1 1000 1000', '0 0'],
    'inputcontrol.dat': ['Input Control file', 'Prec: Precipitation  ', '1', 'prcp prcp time 1 ', 'Ta: Air temperature  ', '2', '8.0', 'Tmin: Min Air temperature ', '1', 'tmin tmin time 1', 'Tmax: Max Air temperature  ', '1', 'tmax tmax time 1', 'v: Wind speed (m/s)  ', '2', '2', 'RH: Relative Humidity   ', '-1              ', '0\t\t', 'Vp: Air vapor pressure   ', '1', 'vp vp time 1', 'AP: Air pressure   ', '2', '80700.0\t\t', 'Qsi: Incoming shortwave(kJ/m2/hr)   ', '1', 'srad srad time 1', 'Qli: Long wave radiation(kJ/m2/hr)', '2', '0\t\t', 'Qnet: Net radiation(kJ/m2/hr)   ', '2  ', '0', 'Qg: Ground heat flux   (kJ/m2/hr)        ', '2               ', '0 \t\t    ', 'Snowalb: Snow albedo (0-1).  (used if ireadalb=1) The albedo of the snow surface to be used when the internal albedo calculations are to be overridden', '2', '0.6'],
    'outputcontrol.dat': ['OUTPUT VARIABLES', '0                 // number of point details; put 0 if no point output needed ', '3                //number of netcdf outputs; put 0 if no netcdf output needed', 'SWE SWE.nc m      ', 'SWIT SWIT.nc m', 'SWISM SWISM.nc m', '3                   //number of aggregated output variables; put 0 if no aggreation output needed', 'SWE m AVE           ', 'SWIT m SUM', 'SWISM m SUM'],
    'siteinitial.dat': ['Site and Initial Condition Input Variables', 'USic:  Energy content initial condition (kg m-3)', '0', '0.0', 'WSis:  Snow water equivalent initial condition (m)', '0', '0.0', 'Tic:  Snow surface dimensionless age initial condition ', '0', '0.0', 'WCic:  Snow water equivalent of canopy conditio(m) ', '0', '0.0', 'df: Drift factor multiplier', '0                ', '1.0  ', 'apr: Average atmospheric pressure         ', '0        ', '80700.0   ', 'Aep: Albedo extinction coefficient             ', '0                ', '0.1  ', 'cc: Canopy coverage fraction         ', '1\t\t          ', 'cc.nc cc ', 'hcan: Canopy height           ', '1          ', 'hcan.nc hcan', 'lai: Leaf area index', '1          ', 'lai.nc lai\t\t\t', 'Sbar: Maximum snow load held per unit branch area        ', '0               ', '6.6', 'ycage: Forest age flag for wind speed profile parameterization            ', '0             ', '1.00  ', 'slope: A 2-D grid that contains the slope at each grid point     ', '1        ', 'slope.nc slope', 'aspect: A 2-D grid that contains the aspect at each grid point   ', '1      ', 'aspect.nc aspect', 'latitude: A 2-D grid that contains the latitude at each grid point    ', '0             ', '41.86', 'subalb: Albedo (fraction 0-1) of the substrate beneath the snow (ground, or glacier)', '0', '0.25', 'subtype: Type of beneath snow substrate encoded as (0 = Ground/Non Glacier, 1=Clean Ice/glacier, 2= Debris covered ice/glacier, 3= Glacier snow accumulation zone)', '0        ', '0.0', 'gsurf: The fraction of surface melt that runs off (e.g. from a glacier)', '0', '0.0', 'b01: Bristow-Campbell B for January (1)', '0', '6.743      ', 'b02: Bristow-Campbell B for February (2)', '0', '7.927    ', 'b03: Bristow-Campbell B for March(3)', '0', '8.055  ', 'b04: Bristow-Campbell B for April (4)', '0', '8.602 ', 'b05: Bristow-Campbell B for may (5)', '0', '8.43  ', 'b06: Bristow-Campbell B for June (6)', '0', '9.76', 'b07: Bristow-Campbell B for July (7)', '0', '0.0    ', 'b08:  Bristow-Campbell B for August (8)', '0', '0.0  ', 'b09: Bristow-Campbell B for September (9)', '0', '0.0   ', 'b10: Bristow-Campbell B for October (10)', '0', '7.4  ', 'b11: Bristow-Campbell B for November (11)', '0', '9.14    ', 'b12: Bristow-Campbell B for December (12)', '0', '6.67 ', 'ts_last:  degree celsius ', '0', '-9999', 'longitude: A 2-D grid that contains the longitude at each grid ', '0', '-111.6'],
    'param.dat': ['Model Parameters', 'irad:  Radiation control flag (0=from ta, 1= input qsi, 2= input qsi,qli 3= input qnet)', '0   ', 'ireadalb:  Albedo reading control flag (0=albedo is computed internally, 1 albedo is read)', '0', 'tr: Temperature above which all is rain (3 C)', '3   ', 'ts: Temperature below which all is snow (-1 C)', '-1        ', 'ems: Emissivity of snow (nominally 0.99)', '0.98  ', 'cg:  Ground heat capacity (nominally 2.09 KJ/kg/C)', '2.09          ', 'z: Nominal meas. heights for air temp. and humidity (2m)', '2 ', 'zo:  Surface aerodynamic roughness (m)', '0.0010     ', 'rho: Snow Density (Nominally 450 kg/m^3)', '337 ', 'rhog:  Soil Density (nominally 1700 kg/m^3)', '1700 ', 'lc: Liquid holding capacity of snow (0.05)', '0.05     ', 'ks:  Snow Saturated hydraulic conductivity (20 m/hr)', '20', 'de:  Thermally active depth of soil (0.1 m)', '0.1   ', 'avo:  Visual new snow albedo (0.95)', '0.85 ', 'anir0: NIR new snow albedo (0.65)', '0.65 ', 'lans: The thermal conductivity of fresh (dry) snow (W/m-K)', '0.278   ', 'lang: the thermal conductivity of soil (W/m-K)', '1.11  ', 'wlf:  Low frequency fluctuation in deep snow/soil layer ', '0.0654      ', 'rd1: Amplitude correction coefficient of heat conduction (1)', '1 ', 'dnews:  The threshold depth of for new snow (0.001 m)', '0.001  ', 'emc:   Emissivity of canopy', '0.98   ', 'alpha: Scattering coefficient for solar radiation', '0.5   ', 'alphal:   Scattering coefficient for long wave radiation', '0.0  ', 'g: leaf orientation with respect to zenith angle', '0.5   ', 'uc:  Unloading rate coefficient (Per hour) (Hedstrom and Pomeroy, 1998)', '0.004626286  ', 'as:  Fraction of extraterrestrial radiation on cloudy day, Shuttleworth (1993)  ', '0.25   ', 'Bs:     (as+bs):Fraction of extraterrestrial radiation on clear day, Shuttleworth ', '0.5      ', 'lambda: Ratio of direct atm radiation to diffuse, worked out from Dingman ', '0.857143 ', 'rimax:  Maximum value of Richardson number for stability correction', '0.16', 'wcoeff: Wind decay coefficient for the forest', '0.5     ', 'a: A in Bristow-Campbell formula for atmospheric transmittance', '0.8      ', 'c: C in Bristow-Campbell formula for atmospheric transmittance', '2.4 '],
}

site_initial_variable_codes = ['USic', 'WSic', 'Tic', 'WCic', 'df', 'apr', 'Aep', 'cc', 'hcan', 'lai', 'Sbar', 'ycage', 'slope', 'aspect', 'latitude', 'longitude', 'subalb', 'subtype', 'gsurf', 'Ts_last', 'b01', 'b02', 'b03', 'b04', 'b05', 'b06', 'b07', 'b08', 'b09', 'b10', 'b11', 'b12']


input_vairable_codes = ['Prec', 'Ta', 'Tmin', 'Tmax', 'v', 'RH', 'Vp', 'AP', 'Qsi', 'Qli', 'Qnet', 'Qg', 'Snowalb']


def create_model_parameter_files(output_control, output_inputcontrol,
                                 output_outputcontrol, output_siteinitial, output_param,
                                 startDateTime=None, endDateTime=None, topY=None, bottomY=None,
                                 rightX=None, leftX=None, usic=None, wsic=None, tic=None, wcic=None,
                                 ts_last=None, **kwargs):
    try:

        # update the control.dat content
        if len(startDateTime.split(' ')) == 1:
            start_obj = datetime.strptime(startDateTime, '%Y/%M/%d')
            end_obj = datetime.strptime(endDateTime, '%Y/%M/%d')
            start_str = datetime.strftime(start_obj, '%Y %M %d') + ' 0.0'
            end_str = datetime.strftime(end_obj, '%Y %M %d') + ' 0.0'
        else:
            start_obj = datetime.strptime(startDateTime, '%Y/%M/%d %H')
            end_obj = datetime.strptime(endDateTime, '%Y/%M/%d %H')
            start_str = datetime.strftime(start_obj, '%Y %M %d %H')
            end_str = datetime.strftime(end_obj, '%Y %M %d %H')


        file_contents_dict['control.dat'][8] = start_str
        file_contents_dict['control.dat'][9] = end_str

        # update the siteinitial.dat content
        lat = 0.5 * (topY + bottomY)
        lon = 0.5 * (rightX + leftX)
        file_contents_dict['siteinitial.dat'][45] = str(lat)
        file_contents_dict['siteinitial.dat'][96] = str(lon)

        site_variables_dict = {3: usic, 6: wsic, 9: tic, 12: wcic, 93: ts_last}
        for line, var_name in site_variables_dict.items():
            if var_name:
                file_contents_dict['siteinitial.dat'][line] = str(var_name)

        # write list in parameter files
        file_path_mapping = {
            'control.dat': output_control,
            'inputcontrol.dat': output_inputcontrol,
            'outputcontrol.dat': output_outputcontrol,
            'siteinitial.dat': output_siteinitial,
            'param.dat': output_param
        }

        for file_name, file_content in file_contents_dict.items():
            file_path = file_path_mapping[file_name]
            with open(file_path, 'w') as para_file:
                para_file.write('\r\n'.join(file_content))  # the line separator is \r\n

        response_dict = {'success': 'True'}

    except Exception as e:
        response_dict = {'success': 'False',
                         'message': 'failed to create the parameter files'}

    return response_dict