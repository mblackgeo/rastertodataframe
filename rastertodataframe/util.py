# -*- coding: utf-8 -*-
import logging

import geopandas as gpd
from osgeo import gdal, ogr

log = logging.getLogger(__name__)


def _open_raster(path, read_only=True):
    """Open a raster in read-only mode.

    Parameters
    ----------
    path : str
        Path of file to open.
    read_only : bool
        File mode, set to False to open in "update" mode.

    Returns
    -------
    GDAL dataset
    """
    access = gdal.GA_ReadOnly if read_only else gdal.GA_Update
    return gdal.OpenShared(path, access)


def _open_vector(path, with_geopandas=False, read_only=True):
    """Import a vector dataset to OGR or GeoDataFrame.

    Parameters
    ----------
    path : str
        Path to vector file.
    with_geopandas : bool
        Set to True to open with geopandas, else use OGR.
    read_only : bool
        If opening with OGR, set to False to open in "update" mode.

    Returns
    -------
    GeoDataFrame if ``with_geopandas`` else OGR datsource.
    """
    if with_geopandas:
        gpd.read_file(path)

    update = False if read_only else True
    return ogr.OpenShared(path, update=update)


def _burn_vector_mask_into_raster(raster, vector):
    """Create a new raster based on the input raster with vector features
        burned into the raster. To be used as a mask for pixels in the vector.

    Parameters
    ----------
    raster : rasterio.DataSetReader
    vector : geopandas.geodataframe.GeoDataFrame

    Returns
    -------
    str
        Path to created raster with vector geometries burned.
    """
    # Check EPSG are same, if not reproject vector.
    # Create an output raster from the input raster.
    # Use GDAL rasterize to burn the vector into the raster.
    # Open and return the burned raster.
    pass
