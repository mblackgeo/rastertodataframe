#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rastertodataframe.tiling` package."""

import os
import unittest

import numpy as np
from osgeo import gdal

from rastertodataframe import tiling


class TestRasterToDataFrameTiling(unittest.TestCase):
    def setUp(self):
        test_data_path = os.path.join(os.path.dirname(__file__), 'data')
        raster_path = os.path.join(test_data_path, 'raster.tif')
        self.ras = gdal.OpenShared(raster_path)

    @staticmethod
    def count_generator(generator):
        """Counter for a generator."""
        return sum(1 for _ in generator)

    def test_windows(self):
        # Test the expected number of windows are returned.
        num_windows = self.count_generator(tiling.windows(self.ras, size=1))
        self.assertEqual(num_windows, 38 * 58)

        num_windows = self.count_generator(tiling.windows(self.ras, size=5))
        self.assertEqual(num_windows, 96)

        num_windows = self.count_generator(tiling.windows(self.ras, size=25))
        self.assertEqual(num_windows, 6)

        num_windows = self.count_generator(tiling.windows(self.ras, size=256))
        self.assertEqual(num_windows, 1)

    def test_tiles(self):
        # Check the correct size array is being returned.
        arr = next(tiling.tiles(self.ras, size=5))
        self.assertEqual(arr.shape, (self.ras.RasterCount, 5, 5))

        # Returns the whole raster (window size > raster).
        arr = next(tiling.tiles(self.ras, size=256))
        self.assertEqual(arr.shape, (self.ras.RasterCount, 38, 58))

        # Return first pixel.
        arr = np.squeeze(next(tiling.tiles(self.ras, size=1)))
        self.assertEqual(arr.shape, (self.ras.RasterCount, ))
        self.assertListEqual(list(arr), [8778, 7731, 6943, 6267])
