#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rastertodataframe` package."""

import os
import unittest

from rastertodataframe import raster_to_dataframe


class TestRasterToDataFrame(unittest.TestCase):
    def setUp(self):
        test_data_path = os.path.join(os.path.dirname(__file__), 'data')
        self.raster_path = os.path.join(test_data_path, 'raster.tif')
        self.vector_path = os.path.join(test_data_path, 'vector.geojson')
        self.raster_wgs84_path = os.path.join(test_data_path,
                                              'raster_epsg4326.tif')
        self.single_band_raster = os.path.join(test_data_path, 'oneband.tif')

    def test_raster_to_dataframe_with_vector(self):
        out_df = raster_to_dataframe(
            self.raster_wgs84_path, vector_path=self.vector_path)

        expected_cols = ['Band_1', 'Band_2', 'Band_3', 'Band_4',
                         'fid', 'value', 'value_string']

        self.assertEqual(out_df.shape, (267, 7))
        self.assertCountEqual(list(out_df.columns), expected_cols)

    def test_raster_to_dataframe_without_vector(self):
        out_df = raster_to_dataframe(self.raster_path)

        expected_cols = ['Band_1', 'Band_2', 'Band_3', 'Band_4']

        self.assertEqual(out_df.shape, (2204, 4))
        self.assertCountEqual(list(out_df.columns), expected_cols)

    def test_single_band_with_vector(self):
        out_df = raster_to_dataframe(
            self.single_band_raster, vector_path=self.vector_path)

        expected_cols = ['Band_1', 'fid', 'value', 'value_string']

        self.assertEqual(out_df.shape, (267, 4))
        self.assertCountEqual(list(out_df.columns), expected_cols)

    def test_single_band_without_vector(self):
        out_df = raster_to_dataframe(self.single_band_raster)

        expected_cols = ['Band_1']

        self.assertEqual(out_df.shape, (2262, 1))
        self.assertCountEqual(list(out_df.columns), expected_cols)
