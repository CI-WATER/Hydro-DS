# Hydro-DS
Web based services for hydrological data processing.

NOTE: Detail description of available web services is coming soon.
## The following data/computing web services are supported:
- Subset DEM (based on bounding box)
- Subset raster to reference raster
- Subset NetCDF to reference raster
- Subset NetCDF by time dimension 
- Delineate watershed
- Generate outlet shape file
- Project shape file
- Project raster
- Project and clip raster
- Project and resample raster
- Project NetCDF
- Generate aspect raster
- Generate slope raster
- Convert raster to NetCDF
- Combine two rasters
- Resample raster
- Resampele NetCDF to reference NetCDF
- Reverse NetCDF Y-axis
- Project, subset and resample NetCDF
- Project, subset and resample raster
- Concatenate NetCDF files
- Generate canopy variable specific data in NetCDF format
- List available data sources

## Other supporting services:
- Upload a file
- Download a file
- Delete a file
- Zip a list of user files
- List user files

## Supported data:
- DEM for the western USA with spatial resolution of 1 arc –sec and NAD83 geographic coordinates system in Tiff Format
- National Land Cover Dataset 2011 (NLCD 2011) covering the whole USA with Projected coordinates of Albers_Conical_Equal_Area  and resolution of 30 m in Tiff format
- Daymet Climate Data for the whole USA for the following variables for years 2010 and 2011. 
  Data will be stored for more years (2005 to 2009) once the data service functions are completely implemented.
  The spatial resolution is 1 Km with spatial reference system of lambert_conformal_conic and daily temporal 
  resolution in netCDF format.
    - Precipitation (mm/day)
    - Daily maximum temperature (oC)
    - Daily minimum temperature (oC)
    - Vapor pressure (Pa)
    - Solar radiation (W/m^2)
- NLDAS climate data (accessed through web services not stored locally)