#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rastertodataframe` package."""

import os
import unittest
import tempfile

from osgeo import gdal, ogr
import geopandas as gpd

from rastertodataframe import raster_to_dataframe


class TestRasterToDataFrame(unittest.TestCase):
    def setUp(self):
        test_data_path = os.path.join(os.path.dirname(__file__))
        self.raster_path = os.path.join(test_data_path, 'raster.tif')
        self.vector_path = os.path.join(test_data_path, 'vector.geojson')
        self.raster_wgs84_path = os.path.join(test_data_path,
                                              'raster_epsg4326.tif')

    def test_raster_to_dataframe(self):
        pass
