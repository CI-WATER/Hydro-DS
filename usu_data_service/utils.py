__author__ = 'pkdash'

import os
from uuid import uuid4
import shutil
import glob
import zipfile
import logging

from django.core.files import File
from django.core.validators import URLValidator

from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as DRF_ValidationError

from ciwater import settings
from usu_data_service.models import UserFile

logger = logging.getLogger(__name__)

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

        source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
        if not os.path.isfile(source_file_path):
            raise NotFound(detail="No file was found at:%s" % file_url_path)

        destination_file_path = os.path.join(uuid_path, file_name)
        shutil.copyfile(source_file_path, destination_file_path)
        return destination_file_path


def zip_user_files(user, file_name_list, zip_file_name):

    if not zip_file_name.endswith('.zip'):
        raise DRF_ValidationError(detail={'zip_file_name': "{file_name} is not a valid zip "
                                                           "file name.".format(zip_file_name)})

    # create temp UUID directory and copy the selected files there for zipping
    uuid_file_path = generate_uuid_file_path()
    logger.debug("uuid_file_path for zip files function:" + uuid_file_path)

    user_folder = 'user_%s' % user.id

    # check the listed files to be zipped exists
    for file_name in file_name_list:
        source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
        if not os.path.isfile(source_file_path):
            raise DRF_ValidationError(detail={'file_name_list': "{file_name} was not found.".format(file_name=file_name)})

    logger.debug("copying file to working directory for zipping:{w_dir}".format(w_dir=uuid_file_path))
    for file_name in file_name_list:
        source_file_path = os.path.join(settings.MEDIA_ROOT, 'data', user_folder, file_name)
        destination_file_path = os.path.join(uuid_file_path, file_name)
        shutil.copyfile(source_file_path, destination_file_path)

    file_matching_pattern = '*.*'
    files_to_look_for = os.path.join(uuid_file_path, file_matching_pattern)
    zip_target_path = os.path.join(uuid_file_path, 'zip')
    os.makedirs(zip_target_path)
    zip_file = os.path.join(zip_target_path, zip_file_name)
    zf = zipfile.ZipFile(zip_file, 'w')
    logger.debug("starting to zip files")
    for each_file in glob.glob(files_to_look_for):
        zf.write(each_file, os.path.relpath(each_file, uuid_file_path))

    zf.close()

    # if the zip file already exists, delete it first
    delete_user_file(user, zip_file_name)
    logger.debug("saving the generated zip file to django as user file")

    # save zip file in django
    user_file = UserFile(file=File(open(zip_file, 'rb')))
    user_file.user = user
    user_file.save()

    # delete uuid temp working directory
    delete_working_uuid_directory(uuid_file_path)

    # return zip file url
    zip_file_url = current_site_url() + user_file.file.url.replace('/static/media/', '/files/')
    logger.debug("zip_file_url:" + zip_file_url)
    return zip_file_url


def unzip_shape_file(shape_zip_file):
    target_unzip_directory = os.path.dirname(shape_zip_file)
    logger.debug("unzipping shape zip file to:" + target_unzip_directory)
    with zipfile.ZipFile(shape_zip_file, "r") as z:
        z.extractall(target_unzip_directory)


def is_input_file_url_path(input_file):
    from django.core.exceptions import ValidationError
    url_validator = URLValidator()
    try:
        url_validator(input_file)
    except ValidationError:
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
            file_path = user_file.file.path
            user_file.file.delete()
            user_file.delete()
            # try:
            #     if os.path.isfile(file_path):
            #         os.remove(file_path)
            # except Exception:
            #     pass

            logger.debug("{file_name} file got deleted by system to save output file with the "
                         "same name".format(file_name=file_path))

            break


def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    #from django.contrib.sites.models import Site
    current_site = 'hydro-ds.uwrl.usu.edu'
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port = getattr(settings, 'MY_SITE_PORT', None)
    url = '%s://%s' % (protocol, current_site)
    if port:
        url += ':%s' % port
    return url


def validate_file_name(file_name):
        try:
            name_part, ext_part = os.path.splitext(file_name)
            if len(name_part) == 0 or len(ext_part) < 2:
                return False

            ext_part = ext_part[1:]
            for c in ext_part:
                if not c.isalpha():
                    return False
            if not name_part[0].isalpha():
                return False
            for c in name_part[1:]:
                if not c.isalnum() and c not in ['-', '_']:
                    return False
        except:
            return False
        return True


def delete_working_uuid_directory(dir_to_delete):
    import usu_data_service
    usu_data_service_root_path = os.path.dirname(usu_data_service.__file__)
    data_service_working_directory = os.path.join(usu_data_service_root_path, 'workspace')
    # make sure we are deleting the uid folder under the path "/...../workspace/"
    if dir_to_delete.startswith(data_service_working_directory):
        if not dir_to_delete.endswith(data_service_working_directory):
            shutil.rmtree(dir_to_delete)

    logger.debug('deleted working directory:' + dir_to_delete)
