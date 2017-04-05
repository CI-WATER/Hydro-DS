"""
This is the data service to run the ueb model.
"""
import os
import json
import zipfile
import shutil
import subprocess
import datetime
import functools

from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic
from usu_data_service.models import Job
from usu_data_service.servicefunctions.run_job import run_service, run_service_done
from usu_data_service.utils import generate_uuid_file_path, delete_working_uuid_directory
from usu_data_service.servicefunctions.model_parameter_list import site_initial_variable_codes, input_vairable_codes


def run_ueb_simulation_job(request, **kwargs):
    job = None
    try:

        job = Job.objects.create(user=request.user,
                                 job_description="run ueb model for resource " + kwargs.get('resource_id'),
                                 status="Started",
                                 is_success=False,
                                 message='Job has been submitted for processing and not completed yet.',
                                 extra_data='HydroShare: ' + kwargs.get('hs_username') if kwargs.get('hs_username') else None)

        future = run_service(run_ueb_model, **kwargs)
        partial_run_service_done = functools.partial(run_service_done, job=job)
        future.add_done_callback(partial_run_service_done)

        return {'success': 'True',
                'message': 'The job has been submitted with job ID as {}'.format(job.id)
                }

    except Exception as e:
        if isinstance(job, Job):
            job.delete()

        return {'success': 'False',
                'message': ['The job submission is failed. Please try to submit the job again.']}


def run_ueb_model(resource_id, hs_username=None, hs_password=None,
                  hs_client_id=None, hs_client_secret=None, token=None, **kwargs):
    """
    This function will download the resource from HydroShare, run model in HydroDS and then save the results in HydroShare.

    :param resource_id: string
    :param hs_username: hydroshare account user name
    :param hs_password: hydroshare account user password
    :param hs_client_id: hydroshare application client id
    :param hs_client_secret: hydroshare application client secrete
    :param token: tokent dictionary as json string from hydroshare oauth authentication
    :return: notification of the url link for the model outputs
    """

    # authentication
    if hs_username and hs_password:
        auth = HydroShareAuthBasic(hs_username, hs_password)
    elif hs_client_id and hs_client_secret and token:
        token = json.loads(token)
        auth = HydroShareAuthOAuth2(hs_client_id, hs_client_secret, token=token)
    else:
        response_dict = {'success': "False",
                         'message': "Authentication to HydroShare is failed. Please provide HydroShare User information"}
        return response_dict

    # download resource to tmp dir in HydroDS
    uuid_file_path = generate_uuid_file_path()
    input_bag_path = os.path.join(uuid_file_path, resource_id + '.zip')
    try:
        hs = HydroShare(auth=auth, hostname='www.hydroshare.org')
        obj = hs.getResource(resource_id)
        # import types
        # resource = str(isinstance(obj, types.GeneratorType))
        with open(input_bag_path, 'wb') as fd:
            for chunk in obj:
                fd.write(chunk)

        subprocess.Popen(['unzip', input_bag_path], stdout=subprocess.PIPE, cwd=uuid_file_path).wait()
        os.remove(input_bag_path)

    except Exception as e:
        delete_working_uuid_directory(uuid_file_path)
        return {'success': "False", 'message': 'Failed to download the HydroShare resource.'}

    # validate files and run model service
    model_input_folder = os.path.join(uuid_file_path, resource_id, 'data', 'contents')

    if not os.path.isdir(model_input_folder):
        delete_working_uuid_directory(uuid_file_path)
        return {'success': "False", 'message': 'Failed to download the HydroShare resource.'}

    else:
        # validate the model input file
        validation = validate_model_input_files(model_input_folder)

        # run model
        if not validation['is_valid']:
            delete_working_uuid_directory(uuid_file_path)
            return {'success': 'False', 'message': validation['result'] }
        else:
            # run ueb model
            try:

                # copy ueb executable
                ueb_bash_path = r'/home/ahmet/hydosbin/ueb/UEBGrid_Parallel_Linuxp/runueb.sh'
                ueb_exe_path = r'/home/ahmet/hydosbin/ueb/UEBGrid_Parallel_Linuxp/ueb'  # TODO find out the ueb file path
                shutil.copy(ueb_exe_path, model_input_folder)
                shutil.copy(ueb_bash_path, model_input_folder)

                process = subprocess.Popen(['./runueb.sh'], stdout=subprocess.PIPE,
                                       cwd=model_input_folder).wait()

                # process = subprocess.Popen(['echo', 'jamy'], cwd=model_input_folder).wait()

                # check simulation result
                if process != 0:
                    # delete_working_uuid_directory(uuid_file_path)
                    return {'success': 'False', 'message': 'failed to execute ueb model process fail'+str(process)+' '+uuid_file_path}
                else:
                    # get point output file
                    output_file_name_list = []
                    model_param_files_dict = validation['result']
                    point_index = 1
                    output_control_contents = model_param_files_dict['output_file']['file_contents']
                    point_num = int(output_control_contents[point_index].split(' ')[0])

                    if point_num != 0:
                        for i in range(point_index + 1, point_index + 1 + point_num):
                            output_file_name_list.append(output_control_contents[i].split(' ')[2])

                    # get netcdf output file
                    netcdf_index = point_index + 1 + point_num
                    netcdf_num = int(output_control_contents[netcdf_index].split(' ')[0])

                    if netcdf_num != 0:
                        for i in range(netcdf_index + 1, netcdf_index + 1 + netcdf_num):
                            output_file_name_list.append(output_control_contents[i].split(' ')[1])

                    # get aggregation file
                    output_file_name_list.append(
                        model_param_files_dict['control_file']['file_contents'][5].split(' ')[0])

                    # zip all the output files
                    zip_file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + 'output_package.zip'
                    zip_file_path = os.path.join(model_input_folder, zip_file_name)
                    zf = zipfile.ZipFile(zip_file_path, 'w')
                    for file_path in [os.path.join(model_input_folder, file_name) for file_name in
                                      output_file_name_list]:
                        if os.path.isfile(file_path):
                            zf.write(file_path, os.path.basename(file_path))
                    zf.close()

            except Exception as e:
                delete_working_uuid_directory(uuid_file_path)
                return {'success': "False", 'message': 'Failed to execute ueb model'}

            # Share the output in HydroShare
            os.chdir(model_input_folder)
            try:
                resource_id = hs.addResourceFile(resource_id, zip_file_name)
                res_creation = True
            except Exception:
                res_creation = False

            if not res_creation:
                try:
                    rtype = 'ModelInstanceResource'
                    title = 'UEB model simulation output'
                    abstract = 'This resource includes the UEB model simulation output files derived from the model' \
                               'instance package http://www.hydroshare.org/resource/{}. The model simulation was conducted ' \
                               'using the UEB web application http://localhost:8000/apps/ueb-app'.format(resource_id)
                    keywords = ('UEB', 'Snowmelt simulation')
                    metadata = [
                        {"source": {'derived_from': 'http://www.hydroshare.org/resource/{}'.format(resource_id)}}]

                    resource_id = hs.createResource(rtype, title, resource_file=zip_file_name, keywords=keywords,
                                                    abstract=abstract, metadata=json.dumps(metadata))

                except Exception:
                    delete_working_uuid_directory(uuid_file_path)
                    return {'success': "False", 'message': 'Failed to share the model outputs in HydroShare.'}

            delete_working_uuid_directory(uuid_file_path)

    return {'success': 'True',
            'message': 'Please check the model outputs in the HydroShare http://www.hydroshare.org/resource/{}'.format(resource_id)}


def validate_model_input_files(model_input_folder):
    try:
        # move all files from zip and folders in the same model_input_folder level
        model_files_path_list = move_files_to_folder(model_input_folder)

        if model_files_path_list:

            # check model parameter files:
            validation = validate_param_files(model_input_folder)

            # check the data input files:
            if validation['is_valid']:
                validation = validate_data_files(model_input_folder, validation['result'])
        else:
            validation = {
                'is_valid': False,
                'result': 'Failed to unpack the model instance resource for file validation.'
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model input files. ' + e.message
        }

    return validation


def move_files_to_folder(model_input_folder):
    """
    move all the files in sub-folder or zip file to the given folder level and remove the zip and sub-folders
    Return the new file path list in the folder
    """
    try:
        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

        while model_files_path_list:
            added_files_list = []

            for model_file_path in model_files_path_list:

                if os.path.isfile(model_file_path) and os.path.splitext(model_file_path)[1] == '.zip':
                    zf = zipfile.ZipFile(model_file_path, 'r')
                    zf.extractall(model_input_folder)
                    extract_file_names = zf.namelist()
                    added_files_list += [os.path.join(model_input_folder, name) for name in extract_file_names]
                    zf.close()
                    os.remove(model_file_path)

                elif os.path.isdir(model_file_path):
                    for dirpath, _, filenames in os.walk(model_file_path):
                        for name in filenames:
                            sub_file_path = os.path.abspath(os.path.join(dirpath, name))
                            new_file_path = os.path.join(model_input_folder, name)
                            shutil.move(sub_file_path, new_file_path)
                            added_files_list.append(new_file_path)
                    shutil.rmtree(model_file_path)

            model_files_path_list = added_files_list

        model_files_path_list = [os.path.join(model_input_folder, name) for name in os.listdir(model_input_folder)]

    except Exception as e:
        model_files_path_list = []

    return model_files_path_list


def validate_param_files(model_input_folder):
    try:

        if 'control.dat' in os.listdir(model_input_folder):

            # get the control file path and contents
            file_path = os.path.join(model_input_folder, 'control.dat')
            with open(file_path) as para_file:
                file_contents = [line.replace('\r\n', '').replace('\n', '').replace('\t', ' ') for line in para_file.readlines()]  # remember the repalce symble is '\r\n'. otherwise, it fails to recoganize the parameter file names

            param_files_dict = {
                'control_file': {'file_path': file_path,
                                 'file_contents': file_contents
                                 }
            }

            # get the other model parameter files path and contents
            file_types = ['param_file', 'site_file', 'input_file', 'output_file']
            missing_file_names = []

            for index in range(0, len(file_types)):
                content_index = index + 1
                file_name = param_files_dict['control_file']['file_contents'][content_index]
                file_path = os.path.join(model_input_folder, file_name)

                if file_name in os.listdir(model_input_folder):
                    param_files_dict[file_types[index]] = {'file_path': file_path}

                    with open(file_path) as para_file:
                        file_contents = [line.replace('\r\n', '').replace('\n', '') for line in para_file.readlines()]

                    param_files_dict[file_types[index]]['file_contents'] = file_contents
                else:
                    missing_file_names.append(file_name)

            if missing_file_names:
                validation = {
                    'is_valid': False,
                    'result': 'Please provide the missing model parameter files: {}.'.format(','.join(missing_file_names))
                }
            else:
                validation = {
                    'is_valid': True,
                    'result': param_files_dict
                }
        else:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model parameter file: control.dat.'
            }

    except Exception as e:
        validation = {
            'is_valid': False,
            'result': 'Failed to validate the model parameter files. ' + e.message
        }

    return validation


def validate_data_files(model_input_folder, model_param_files_dict):
    missing_file_names = []

    try:
        # check the control.dat watershed.nc
        watershed_name = model_param_files_dict['control_file']['file_contents'][6]
        if watershed_name not in os.listdir(model_input_folder):
            missing_file_names.append(watershed_name)

        # check the missing files in siteinitial.dat
        site_file_names = []

        for var_name in site_initial_variable_codes:
            for index, content in enumerate(model_param_files_dict['site_file']['file_contents']):
                if var_name in content and model_param_files_dict['site_file']['file_contents'][index+1][0] == '1':
                    site_file_names.append(model_param_files_dict['site_file']['file_contents'][index+2].split(' ')[0])
                    break

        if site_file_names:
            for name in site_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        # check the missing files in inputcontrol.dat
        input_file_names = []
        for var_name in input_vairable_codes:
            for index, content in enumerate(model_param_files_dict['input_file']['file_contents']):
                if var_name in content:
                    if model_param_files_dict['input_file']['file_contents'][index+1][0] == '1':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index+2].split(' ')[0]+'0.nc')
                    elif model_param_files_dict['input_file']['file_contents'][index+1][0] == '0':
                        input_file_names.append(model_param_files_dict['input_file']['file_contents'][index + 2].split(' ')[0])
                    break

        if input_file_names:
            for name in input_file_names:
                if name not in os.listdir(model_input_folder):
                    missing_file_names.append(name)

        if missing_file_names:
            validation = {
                'is_valid': False,
                'result': 'Please provide the missing model input data files: {}'.format(',\n'.join(missing_file_names))
            }
        else:
            validation = {
                'is_valid': True,
                'result': model_param_files_dict
            }

    except Exception as e:

        validation = {
            'is_valid': False,
            'result':  'Failed to validate the model input data files.' + e.message
        }

    return validation