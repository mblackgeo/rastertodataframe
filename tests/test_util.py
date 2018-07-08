#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rastertodataframe.util` package."""

import os
import unittest
import tempfile

from osgeo import gdal, ogr
import geopandas as gpd

from rastertodataframe import util


class TestRasterToDataFrameUtil(unittest.TestCase):
    def setUp(self):
        test_data_path = os.path.join(os.path.dirname(__file__))
        self.raster_path = os.path.join(test_data_path, 'raster.tif')
        self.vector_path = os.path.join(test_data_path, 'vector.geojson')
        self.raster_wgs84_path = os.path.join(test_data_path,
                                              'raster_epsg4326.tif')

    def test_open_raster(self):
        ras = util.open_raster(self.raster_path)
        self.assertIsInstance(ras, gdal.Dataset)

    def test_open_vector_ogr(self):
        # As OGR DataSource.
        vec = util.open_vector(
            self.vector_path,
            with_geopandas=False)
        self.assertIsInstance(vec, ogr.DataSource)

    def test_open_vector_gdf(self):
        # As GeoPandasDataFrame.
        vec_gdf = util.open_vector(
            self.vector_path,
            with_geopandas=True)
        self.assertIsInstance(vec_gdf, gpd.GeoDataFrame)

    def test__epsg_from_projection_proj4(self):
        # Proj4 string.
        prj = '+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs'
        self.assertEqual(
            util._epsg_from_projection(prj),
            32632)

    def test__epsg_from_projection_esri(self):
        # ESRI PROJCS (WKT).
        prj = ('PROJCS["WGS_1984_UTM_Zone_30N", '
               'GEOGCS["GCS_WGS_1984", '
               'DATUM["D_WGS_1984", '
               'SPHEROID["WGS_1984", 6378137.0, 298.257223563]], '
               'PRIMEM["Greenwich", 0.0], '
               'UNIT["Degree", 0.0174532925199433]], '
               'PROJECTION["Transverse_Mercator"], '
               'PARAMETER["False_Easting", 500000.0], '
               'PARAMETER["False_Northing", 0.0], '
               'PARAMETER["Central_Meridian", -3.0], '
               'PARAMETER["Scale_Factor", 0.9996], '
               'PARAMETER["Latitude_Of_Origin", 0.0], '
               'UNIT["Meter", 1.0]]')

        self.assertEqual(
            util._epsg_from_projection(prj),
            32630)

    def test_get_ogr_epsg(self):
        vec = ogr.OpenShared(self.vector_path)
        self.assertEqual(util.get_epsg(vec), 4326)

    def test_get_gdal_epsg(self):
        ras = gdal.OpenShared(self.raster_path)
        self.assertEqual(util.get_epsg(ras), 32632)

    def test_get_gpd_epsg(self):
        gdf = gpd.read_file(self.vector_path)
        self.assertEqual(util.get_epsg(gdf), 4326)

    def test_same_epsg(self):
        ras = gdal.OpenShared(self.raster_path)
        gdf = gpd.read_file(self.vector_path)
        self.assertFalse(util.same_epsg(ras, gdf))
        self.assertTrue(util.same_epsg(ras, ras))

    def test__create_empty_raster(self):
        fid, tmp_fname = tempfile.mkstemp()
        ras = gdal.OpenShared(self.raster_path)
        out = util._create_empty_raster(
            ras, tmp_fname, n_bands=1, no_data_value=0)

        self.assertIsInstance(out, gdal.Dataset)
        self.assertEqual(out.RasterCount, 1)
        self.assertEqual(ras.RasterXSize, out.RasterXSize)
        self.assertEqual(ras.RasterYSize, out.RasterYSize)

        os.close(fid)
        os.remove(tmp_fname)

    def test__brun_vector_mask_into_raster_wrong_epsg(self):
        # Error for differing projections.
        with self.assertRaises(ValueError):
            out = util._burn_vector_mask_into_raster(
                self.raster_path, self.vector_path, '')

    def test__burn_vector_mask_into_raster_vector_mask(self):
        # Burn in a specified vector field.
        fid, tmp_fname = tempfile.mkstemp()
        out = util._burn_vector_mask_into_raster(
            self.raster_wgs84_path, self.vector_path, tmp_fname)

        arr = out.GetRasterBand(1).ReadAsArray()
        self.assertEqual(arr.shape, (39, 58))
        self.assertEqual(arr.ndim, 2)
        self.assertEqual(arr.max(), 1)

        os.close(fid)
        os.remove(tmp_fname)

    def test__burn_vector_mask_into_raster_vector_field(self):
        # Burn in a specified vector field.
        fid, tmp_fname = tempfile.mkstemp()
        out = util._burn_vector_mask_into_raster(
            self.raster_wgs84_path, self.vector_path, tmp_fname,
            vector_field='value')

        arr = out.GetRasterBand(1).ReadAsArray()
        self.assertEqual(arr.shape, (39, 58))
        self.assertEqual(arr.ndim, 2)
        self.assertEqual(arr.max(), 2000)

        os.close(fid)
        os.remove(tmp_fname)
