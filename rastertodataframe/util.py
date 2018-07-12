# -*- coding: utf-8 -*-
import logging

import pyproj
import geopandas as gpd
from osgeo import gdal, ogr, osr

log = logging.getLogger(__name__)


def open_raster(path, read_only=True):
    """Open a raster using GDAL.

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


def open_vector(path, with_geopandas=False, read_only=True):
    """Open a vector dataset using OGR or GeoPandas.

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
        return gpd.read_file(path)

    update = False if read_only else True
    return ogr.OpenShared(path, update=update)


def _get_dataset_epsg(dataset):
    """Get the EPSG code from a GDAL Dataset.

    Parameters
    ----------
    dataset : gdal.Dataset

    Returns
    -------
    int
    """
    prj = dataset.GetProjection()
    return _epsg_from_projection(prj)


def _get_datasource_epsg(datasource):
    """Get the EPSG code from a OGR DataSource.

    Parameters
    ----------
    datasource : ogr.DataSource

    Returns
    -------
    int
    """
    layer = datasource.GetLayer(0)
    spatial_ref = layer.GetSpatialRef()
    spatial_ref.AutoIdentifyEPSG()
    return int(spatial_ref.GetAuthorityCode(None))


def _get_gpd_epsg(gdf):
    """Get the EPSG code from a GeoPandas DataFrame.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame

    Returns
    -------
    int
    """
    return _epsg_from_projection(pyproj.Proj(gdf.crs).srs)


def _epsg_from_projection(prj):
    """Return the EPSG code from a projection string.

    Parametres
    ----------
    prj : str

    Returns
    -------
    int
    """
    srs = osr.SpatialReference()

    if prj.startswith("PROJCS") or prj.startswith("GEOGCS"):
        # ESRI well know text strings,
        srs.ImportFromESRI([prj])
    else:
        # Proj4 strings.
        srs.ImportFromProj4(prj)

    srs.AutoIdentifyEPSG()
    return int(srs.GetAuthorityCode(None))


def get_epsg(data):
    """Get the EPSG code from an input.

    Parameters
    ----------
    data : gdal.Dataset or ogr.DataSource or gpd.GeoDataFrame

    Returns
    -------
    int
    """
    if isinstance(data, gdal.Dataset):
        return _get_dataset_epsg(data)
    elif isinstance(data, ogr.DataSource):
        return _get_datasource_epsg(data)
    elif isinstance(data, gpd.GeoDataFrame):
        return _get_gpd_epsg(data)
    else:
        raise ValueError('Unable to get EPSG from: {}'.format(data))


def same_epsg(data1, data2):
    """Check sets of data have the same EPSG.

    Parameters
    ----------
    data1 : gdal.DataSet or ogr.DataSource or gpd.GeoDataFrame
    data2 : gdal.DataSet or ogr.DataSource or gpd.GeoDataFrame

    Returns
    -------
    bool
    """
    return get_epsg(data1) == get_epsg(data2)


def _create_empty_raster(template, out_path, n_bands=1, no_data_value=None):
    """Create a new empty raster using GDAL. Inherits all but the data from the
        given template dataset.

    Parameters
    ----------
    template : gdal.Dataset
    out_path : str
    n_bands : int or None
        Number of bands to create in the output raster.
    no_data_value : float or None
        No data value, if None uses the same as ``template``.

    Returns
    -------
    gdal.DataSet
    """
    # Raster size.
    x_size = template.RasterXSize
    y_size = template.RasterYSize
    n_bands = int(n_bands) if n_bands is not None else template.RasterCount
    dtype = template.GetRasterBand(1).DataType

    # Create the driver.
    driver = template.GetDriver()
    out_dataset = driver.Create(out_path, x_size, y_size, n_bands, dtype)

    # Set the projection.
    out_dataset.SetGeoTransform(template.GetGeoTransform())
    out_dataset.SetProjection(template.GetProjectionRef())

    # Set the no data value.
    if no_data_value is not None:
        out_ndv = float(no_data_value)
        for i in range(1, out_dataset.RasterCount + 1):
            band = out_dataset.GetRasterBand(i)
            band.SetNoDataValue(out_ndv)

    return out_dataset


def burn_vector_mask_into_raster(raster_path, vector_path, out_path,
                                 vector_field=None):
    """Create a new raster based on the input raster with vector features
        burned into the raster. To be used as a mask for pixels in the vector.

    Parameters
    ----------
    raster_path : str
    vector_path : str
    out_path : str
        Path for output raster. Format and Datatype are the same as ``ras``.
    vector_field : str or None
        Name of a field in the vector to burn values from. If None, all vector
        features are burned with a constant value of 1.

    Returns
    -------
    gdal.Dataset
        Single band raster with vector geometries burned.
    """

    ras = open_raster(raster_path)
    vec = open_vector(vector_path)

    # Check EPSG are same, if not reproject vector.
    if not same_epsg(ras, vec):
        raise ValueError(
            'Raster and vector are not the same EPSG.\n'
            '{} != {}'.format(get_epsg(ras), get_epsg(vec))
        )

    # Create an empty for GDALRasterize to burn vector values to.
    out_ds = _create_empty_raster(ras, out_path, n_bands=1, no_data_value=0)

    if vector_field is None:
        # Use a constant value for all features.
        burn_values = [1]
        attribute = None
    else:
        # Use the values given in the vector field.
        burn_values = None
        attribute = vector_field

    # Options for Rasterize.
    # note: burnValues and attribute are exclusive.
    rasterize_opts = gdal.RasterizeOptions(
        bands=[1],
        burnValues=burn_values,
        attribute=attribute,
        allTouched=True)
    _ = gdal.Rasterize(out_ds, vector_path, options=rasterize_opts)

    # Explicitly close raster to ensure it is saved.
    out_ds.FlushCache()
    out_ds = None

    return open_raster(out_path)


def get_raster_band_names(raster):
    """Obtain the names of bands from a raster. The raster metadata is queried
    first, if no names a present, a 1-index list of band_N is returned.

    Parameters
    ----------
    raster : gdal.Dataset

    Returns
    -------
    list[str]
    """
    band_names = []
    for i in range(1, raster.RasterCount + 1):
        band = raster.GetRasterBand(i)

        if band.GetDescription():
            # Use the band description.
            band_names.append(band.GetDescription())
        else:
            # Check for metedata.
            this_band_name = 'Band_{}'.format(band.GetBand())
            metadata = band.GetDataset().GetMetadata_Dict()

            # If in metadata, return the metadata entry, else Band_N.
            if this_band_name in metadata and metadata[this_band_name]:
                band_names.append(metadata[this_band_name])
            else:
                band_names.append(this_band_name)

    return band_names


def get_pixels(ras, mask, mask_val=None):
    """Get pixels from a raster (with optional mask).

    Parameters
    ----------
    ras : np.ndarray
        Array of raster data in the form [bands][y][x].
    mask : np.ndarray
        Array (2D) of zeroes to mask data.
    mask_val : int
        Value of the data pixels in the mask. Default: non-zero.

    Returns
    -------
    np.ndarray
        Array of non-masked data.
    """
    if mask is None:
        return ras

    # Use the mask to get the indices of the non-zero pixels.
    if mask_val:
        (i, j) = (mask == mask_val).nonzero()
    else:
        (i, j) = mask.nonzero()

    return (ras[i, j] if ras.ndim == 2 else ras[:, i, j])
