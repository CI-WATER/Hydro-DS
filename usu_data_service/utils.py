__author__ = 'pkdash'

import os
from uuid import uuid4
import shutil
import glob
import zipfile

from django.core.validators import URLValidator

from rest_framework.exceptions import NotFound

from ciwater import settings
from usu_data_service.models import UserFile


def generate_uuid_file_path(file_name=None):
    import usu_data_service
    usu_data_service_root_path = os.path.dirname(usu_data_service.__file__)
    uuid_path = os.path.join(usu_data_service_root_path, 'workspace', uuid4().hex)
    os.makedirs(uuid_path)
    file_path = uuid_path
    if file_name:
        file_path = os.path.join(uuid_path, file_name)
    return file_path


def copy_input_file_to_uuid_working_directory(uuid_path, file_url_path):
        path_parts = file_url_path.split('/')
        file_name = path_parts[-1]
        if 'user_' in path_parts[-2]:
            user_folder = path_parts[-2]
        else:
            user_folder = ''
        print('user_folder:' + user_folder)

        source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
        if not os.path.isfile(source_file_path):
            raise NotFound(detail="No file was found at:%s" % file_url_path)

        destination_file_path = os.path.join(uuid_path, file_name)
        shutil.copyfile(source_file_path, destination_file_path)
        return destination_file_path


def unzip_shape_file(shape_zip_file):
    target_unzip_directory = os.path.dirname(shape_zip_file)
    print(">>>> unzipping to:" + target_unzip_directory)
    with zipfile.ZipFile(shape_zip_file, "r") as z:
        z.extractall(target_unzip_directory)


def is_input_file_url_path(input_file):
    from django.core.exceptions import ValidationError
    url_validator = URLValidator()
    try:
        url_validator(input_file)
    except ValidationError as e:
        return False
    return True


def validate_url_file_path(file_url_path):
    from django.core.exceptions import ValidationError
    url_validator = URLValidator()
    try:
        url_validator(file_url_path)
    except ValidationError as e:
        raise e

    path_parts = file_url_path.split('/')
    file_name = path_parts[-1]
    if 'user_' in path_parts[-2]:
        user_folder = path_parts[-2]
    else:
        user_folder = ''
    print('user_folder:' + user_folder)

    source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
    if not os.path.isfile(source_file_path):
        raise NotFound(detail="No file was found at:%s" % file_url_path)
    return source_file_path


def create_shape_zip_file(shape_file_path):
    shape_file_name = os.path.basename(shape_file_path)
    shape_file_name_wo_ext = shape_file_name[:-4]
    base_dir = os.path.dirname(shape_file_path)
    # check if there is a folder in base_dir with same name as the shape file name
    if os.path.exists(os.path.join(base_dir, shape_file_name_wo_ext)):
        base_dir = os.path.join(base_dir, shape_file_name_wo_ext)

    file_matching_pattern = shape_file_name_wo_ext + '.*'
    files_to_look_for = os.path.join(base_dir, file_matching_pattern)
    zip_file = os.path.join(base_dir, shape_file_name_wo_ext + '_zip.zip')
    zf = zipfile.ZipFile(zip_file, 'w')
    for each_file in glob.glob(files_to_look_for):
        zf.write(each_file, os.path.relpath(each_file, base_dir))

    zf.close()
    renamed_zip_file = zip_file.replace('_zip', '')
    os.rename(zip_file, renamed_zip_file)
    return renamed_zip_file


def delete_user_file(user, filename):
    for user_file in UserFile.objects.filter(user__id=user.id):
        if os.path.basename(user_file.file.name) == filename:
            user_file.file.delete()
            user_file.delete()
            print('>>> file_deleted:' + filename)
            break