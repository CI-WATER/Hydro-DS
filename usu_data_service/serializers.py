__author__ = 'pkdash'

from django.core.exceptions import ValidationError

from rest_framework import serializers
from usu_data_service.utils import *
from usu_data_service.servicefunctions.static_data import get_static_data_file_path

class InputRasterURLorStaticRequestValidator(serializers.Serializer):
    input_raster = serializers.CharField(required=True)

    def validate_input_raster(self, value):
        # check first if it is a valid url file path
        try:
            print('1>>>value')
            validate_url_file_path(value)
        except ValidationError:
            # assume this a static file name
            print('2>>>value')
            static_file_path = get_static_data_file_path(value)
            if static_file_path is None:
                raise serializers.ValidationError("Invalid static data file name:%s" % value)

        return value


class SubsetDEMRequestValidator(InputRasterURLorStaticRequestValidator):
    xmin = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    xmax = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    ymin = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    ymax = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    output_raster = serializers.CharField(required=False)

class InputRasterRequestValidator(serializers.Serializer):
    input_raster = serializers.URLField(required=True)


class InputNetCDFURLRequestValidator(serializers.Serializer):
    input_netcdf = serializers.URLField(required=True)


class InputNetCDFURLorStaticRequestValidator(serializers.Serializer):
    input_netcdf = serializers.CharField(required=True)

    def validate_input_netcdf(self, value):
        # check first if it is a valid url file path
        try:
            validate_url_file_path(value)
        except ValidationError:
            # assume this a static file name
            static_file_path = get_static_data_file_path(value)
            if static_file_path is None:
                raise serializers.ValidationError("Invalid static data file name:%s" % value)

        return value


class DelineateWatershedRequestValidator(serializers.Serializer):
    outletPointX = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    outletPointY = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    utmZone = serializers.IntegerField(required=True)
    streamThreshold = serializers.IntegerField(required=True)
    input_DEM_raster = serializers.URLField(required=True)
    output_raster = serializers.CharField(required=True)
    output_outlet_shapefile = serializers.CharField(required=True)


class DelineateWatershedAtShapeFileRequestValidator(serializers.Serializer):
    epsgCode = serializers.IntegerField(required=True)
    streamThreshold = serializers.IntegerField(required=True)
    input_DEM_raster = serializers.URLField(required=True)
    input_outlet_shapefile = serializers.URLField(required=True)
    output_raster = serializers.CharField(required=True)
    output_outlet_shapefile = serializers.CharField(required=True)

    def validate_input_outlet_shapefile(self, value):
        try:
            validate_url_file_path(value)
        except NotFound:
            raise serializers.ValidationError("Invalid input outlet shapefile:%s" % value)

        if not value.endswith('.zip'):
            raise serializers.ValidationError("Invalid input outlet shapefile. Shapefile needs to be a zip file:%s" % value)

        return value

    def validate_output_outlet_shapefile(self, value):
        if not value.endswith('.shp'):
            raise serializers.ValidationError("Invalid output outlet shapefile. Shapefile needs to be a .shp file:%s" % value)

        return value

class CreateOutletShapeRequestValidator(serializers.Serializer):
    outletPointX = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    outletPointY = serializers.DecimalField(required=True, max_digits=12, decimal_places=8)
    output_shape_file_name = serializers.CharField(required=False)


class RasterToNetCDFRequestValidator(InputRasterRequestValidator):
    output_netcdf = serializers.CharField(required=False)


class ComputeRasterAspectRequestValidator(InputRasterRequestValidator):
    output_raster = serializers.CharField(required=False)


class ComputeRasterSlopeRequestValidator(InputRasterRequestValidator):
    output_raster = serializers.CharField(required=False)


class ReverseNetCDFYaxisRequestValidator(InputNetCDFURLRequestValidator):
    output_netcdf = serializers.CharField(required=False)


class ProjectRasterRequestValidator(InputRasterRequestValidator):
    utmZone = serializers.IntegerField(required=True)
    output_raster = serializers.CharField(required=False)


class CombineRastersRequestValidator(serializers.Serializer):
    input_raster1 = serializers.URLField(required=True)
    input_raster2 = serializers.URLField(required=True)
    output_raster = serializers.CharField(required=False)


class ResampleRasterRequestValidator(InputRasterRequestValidator):
    dx = serializers.IntegerField(required=True)
    dy = serializers.IntegerField(required=True)
    # TODO: may be this should be a choice type field
    resample = serializers.CharField(min_length=1, default='near')
    output_raster = serializers.CharField(required=False)


class SubsetRasterToReferenceRequestValidator(InputRasterRequestValidator):
    reference_raster = serializers.URLField(required=True)
    output_raster = serializers.CharField(required=False)


class SubsetNetCDFToReferenceRequestValidator(InputNetCDFURLorStaticRequestValidator):
    reference_raster = serializers.URLField(required=True)
    output_netcdf = serializers.CharField(required=False)


class ProjectNetCDFRequestValidator(InputNetCDFURLRequestValidator):
    utm_zone = serializers.IntegerField(required=True)
    output_netcdf = serializers.CharField(required=False)
    variable_name = serializers.CharField(required=True)


class SubsetNetCDFByTimeDimensionRequestValidator(InputNetCDFURLorStaticRequestValidator):
    time_dim_name = serializers.CharField(required=True)
    start_time_index = serializers.IntegerField(required=True)
    end_time_index = serializers.IntegerField(required=True)
    output_netcdf = serializers.CharField(required=False)

    def validate_start_time_index(self, value):
        if value < 0:
            raise serializers.ValidationError("Invalid start_time_index value:%s. It must be a positive integer." % value)
        return value

    def validate_end_time_index(self, value):
        if value < 0:
            raise serializers.ValidationError("Invalid end_time_index value:%s. It must be a positive integer." % value)
        return value

    def validate(self, data):
        """
        Check that the start_time_index is before the end_time_index.
        """
        if data['start_time_index'] > data['end_time_index']:
            raise serializers.ValidationError("start time index must be a value less than the end time index")

        return data


class ResampleNetCDFRequestValidator(InputNetCDFURLRequestValidator):
    reference_netcdf = serializers.URLField(required=True)
    output_netcdf = serializers.CharField(required=False)
    variable_name = serializers.CharField(required=True)


class ConcatenateNetCDFRequestValidator(serializers.Serializer):
    input_netcdf1 = serializers.URLField(required=True)
    input_netcdf2 = serializers.URLField(required=True)
    output_netcdf = serializers.CharField(required=False)


class ProjectSubsetResampleNetCDFRequestValidator(ResampleNetCDFRequestValidator):
    pass


class ProjectClipRasterRequestValidator(InputRasterURLorStaticRequestValidator):
    output_raster = serializers.CharField(required=False)
    reference_raster = serializers.CharField(required=True)


class GetCanopyVariablesRequestValidator(serializers.Serializer):
    in_NLCDraster = serializers.URLField(required=True)
    out_ccNetCDF = serializers.CharField(required=False)
    out_hcanNetCDF = serializers.CharField(required=False)
    out_laiNetCDF = serializers.CharField(required=False)


class GetCanopyVariableRequestValidator(serializers.Serializer):
    in_NLCDraster = serializers.URLField(required=True)
    output_netcdf = serializers.CharField(required=True)
    variable_name = serializers.CharField(required=True)

    def validate_variable_name(self, value):
        if value not in ('cc', 'hcan', 'lai'):
            raise serializers.ValidationError("Invalid canopy variable name:%s. " % value)
        return value

class ProjectShapeFileUTMRequestValidator(serializers.Serializer):
    input_shape_file = serializers.URLField(required=True)
    output_shape_file = serializers.CharField(required=False)
    utm_zone = serializers.IntegerField(required=True)


class ProjectShapeFileEPSGRequestValidator(serializers.Serializer):
    input_shape_file = serializers.URLField(required=True)
    output_shape_file = serializers.CharField(required=False)
    epsg_code = serializers.IntegerField(required=True)

class ZipMyFilesRequestValidator(serializers.Serializer):
    file_names = serializers.CharField(min_length=5, required=True)
    zip_file_name = serializers.CharField(min_length=5, required=True)

    def validate_file_names(self, value):
        file_names = value.split(',')
        if len(file_names) == 0:
            raise serializers.ValidationError("No file name provided to be zipped")

        for file_name in file_names:
            if not validate_file_name(file_name):
                raise serializers.ValidationError("%s is not a valid file name" % file_name)

        return file_names

    def validate_zip_file_name(self, value):
        if not value.endswith('.zip'):
            raise serializers.ValidationError("%s is not a valid zip file name" % value)

        if not validate_file_name(value):
                raise serializers.ValidationError("%s is not a valid file name" % value)

        return value