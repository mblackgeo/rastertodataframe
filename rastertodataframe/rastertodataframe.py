# -*- coding: utf-8 -*-
import os
import logging
import tempfile
import uuid
import shutil

import numpy as np
import pandas as pd

from rastertodataframe import util, tiling

log = logging.getLogger(__name__)


def raster_to_dataframe(raster_path, vector_path=None):
    """Convert a raster to a Pandas DataFrame.

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
    temp_dir = vector_mask_fname = None

    # Get raster band names.
    ras = util.open_raster(raster_path)
    raster_band_names = util.get_raster_band_names(ras)

    # Create a mask from the pixels touched by the vector.
    if vector_path is not None:

        # Create a temporary directory for files.
        temp_dir = tempfile.mkdtemp()
        vec_with_fid = os.path.join(temp_dir, '{}'.format(uuid.uuid1()))

        # Add a dummy feature ID column to the vector.
        # This is not always present in OGR features.
        vec_gdf = util.open_vector(vector_path, with_geopandas=True)
        mask_values = list(range(1, len(vec_gdf) + 1))
        vec_gdf['__fid__'] = pd.Series(mask_values)
        vec_gdf.to_file(vec_with_fid, driver='GeoJSON')

        # Mask the vector using the feature ID column.
        vector_mask_fname = os.path.join(temp_dir, '{}'.format(uuid.uuid1()))
        vector_mask = util.burn_vector_mask_into_raster(
            raster_path, vec_with_fid, vector_mask_fname,
            vector_field='__fid__')

        # Loop over mask values to extract pixels.
        tile_dfs = []  # DataFrames of each tile.
        mask_arr = vector_mask.GetRasterBand(1).ReadAsArray()

        for ras_arr in tiling.tiles(ras):

            mask_dfs = []  # DataFrames of each mask.
            for mask_val in mask_values:

                # Extract only masked pixels.
                pixels = util.get_pixels(
                    ras_arr, mask_arr, mask_val=mask_val)\
                    .transpose()
                fid_px = np.ones(pixels.shape[0]) * mask_val

                # Create a DataFrame of masked pixels and their FID.
                mask_df = pd.DataFrame(pixels, columns=raster_band_names)
                mask_df['__fid__'] = fid_px
                mask_dfs.append(mask_df)

            # Concat the mask DataFrames.
            mask_df = pd.concat(mask_dfs)

            # Join with pixels with vector attributes using the FID.
            tile_dfs.append(mask_df.merge(vec_gdf, how='left', on='__fid__'))

        # Merge all the tiles.
        out_df = pd.concat(tile_dfs)

    else:
        # No vector given, simply load the raster.
        tile_dfs = []  # DataFrames of each tile.
        for ras_arr in tiling.tiles(ras):

            idx = (1, 2)  # Assume multiband
            if ras_arr.ndim == 2:
                idx = (0, 1)  # Handle single band rasters

            mask_arr = np.ones((ras_arr.shape[idx[0]], ras_arr.shape[idx[1]]))
            pixels = util.get_pixels(ras_arr, mask_arr).transpose()
            tile_dfs.append(pd.DataFrame(pixels, columns=raster_band_names))

        # Merge all the tiles.
        out_df = pd.concat(tile_dfs)

    # TODO mask no data values.

    # Remove temporary files.
    if temp_dir is not None:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Return dropping any extra cols.
    return out_df.drop(columns=['__fid__', 'geometry'], errors='ignore')
