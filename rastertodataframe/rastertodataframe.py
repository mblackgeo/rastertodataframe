# -*- coding: utf-8 -*-
import logging

import pandas as pd
import geopandas as gpd

from . import util

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
    raster = util.open_raster(raster_path)
    vector = util.open_vector(vector_path) if vector_path is not None else None

    # If vector:
    #    Get vector mask (either all features or by a specific vector field).
    #    Loop over mask values to extract pixels.

    # Assemble dataframe from raster pixels.
    pass
