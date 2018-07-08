# -*- coding: utf-8 -*-
import os
import logging
import tempfile

import numpy as np
import pandas as pd

from rastertodataframe import util

log = logging.getLogger(__name__)


def raster_to_dataframe(raster_path, vector_path=None):
    """Convert a raster to a Pandas DataFrame.

    .. note:: This requires enough memory to load the entire raster.

    Parameters
    ----------
    raster_path : str
        Path to raster file.
    vector_path : str
        Optional path to vector file. If given, raster pixels will be extracted
        from features in the vector. If None, all raster pixels are converted
        to a DataFrame.

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    # Placeholders for possible temporary files.
    fid1 = fid2 = tmp_fname = vector_mask_fname = None

    # Get raster band names.
    ras = util.open_raster(raster_path)
    raster_band_names = util.get_raster_band_names(ras)

    # Create a mask from the pixels touched by the vector.
    if vector_path is not None:
        fid1, tmp_fname = tempfile.mkstemp(suffix='.geojson')

        # Add a dummy feature ID column to the vector.
        # This is not always present in OGR features.
        vec_gdf = util.open_vector(vector_path, with_geopandas=True)
        mask_values = list(range(1, len(vec_gdf) + 1))
        vec_gdf['__fid__'] = pd.Series(mask_values)
        vec_gdf.to_file(tmp_fname, driver='GeoJSON')

        # Mask the vector using the feature ID column.
        fid2, vector_mask_fname = tempfile.mkstemp()
        vector_mask = util.burn_vector_mask_into_raster(
            raster_path, tmp_fname, vector_mask_fname,
            vector_field='__fid__')

        # Loop over mask values to extract pixels.
        mask_arr = vector_mask.GetRasterBand(1).ReadAsArray()
        ras_arr = ras.ReadAsArray()  # TODO this is not memory efficient.

        out_dfs = []
        for mask_val in mask_values:
            pixels = util.extract_masked_px(ras_arr, mask_arr, mask_val=mask_val)\
                .transpose()
            fid_px = np.ones(pixels.shape[0]) * mask_val

            mask_df = pd.DataFrame(pixels, columns=raster_band_names)
            mask_df['__fid__'] = fid_px
            out_dfs.append(mask_df)

        # Fill DataFrame with pixels.
        out_df = pd.concat(out_dfs)

        # Join with vector attributes.
        out_df = out_df.merge(vec_gdf, how='left', on='__fid__')

    else:
        # No vector given, simply load the raster.
        ras_arr = ras.ReadAsArray()  # TODO not memory efficient.
        mask_arr = np.ones((ras_arr.shape[1], ras_arr.shape[2]))
        pixels = util.extract_masked_px(ras_arr, mask_arr).transpose()
        out_df = pd.DataFrame(pixels, columns=raster_band_names)

    # TODO screen no data values.

    # Remove temporary files.
    if fid1 is not None and tmp_fname is not None:
        os.close(fid1)
        os.remove(tmp_fname)
    if fid2 is not None and vector_mask_fname is not None:
        os.close(fid2)
        os.remove(vector_mask_fname)

    # Return dropping any extra cols.
    return out_df.drop(columns=['__fid__', 'geometry'], errors='ignore')
