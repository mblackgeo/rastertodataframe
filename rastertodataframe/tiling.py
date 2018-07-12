# -*- coding: utf-8 -*-
"""Utils for reading a GDAL Dataset in small tiles."""


def windows(ras, size=256):
    """Generator for raster window size/offsets.

    Parameters
    ----------
    ras : gdal.Dataset
        Input raster.
    size : int
        Size of window in pixels. One value required which is used for both the
        x and y size. E.g 256 means a 256x256 window.

    Yields
    ------
    tuple[int]
        4 element tuple containing the x size, y size, x offset and y offset
        of the window.
    """
    ras_x = ras.RasterXSize
    ras_y = ras.RasterYSize
    for xoff in range(0, ras_x, size):
        xsize = (size if size + xoff <= ras_x else ras_x - xoff)
        for yoff in range(0, ras_y, size):
            ysize = (size if size + yoff <= ras_y else ras_y - yoff)
            yield xsize, ysize, xoff, yoff


def tiles(ras, size=256):
    """Generator return a raster array in tiles.

    Parameters
    ----------
    ras : gdal.Dataset
        Input raster.
    size : int
        Size of window in pixels. One value required which is used for both the
        x and y size. E.g 256 means a 256x256 window.

    Yields
    ------
    np.ndarray
        Raster array in form [band][y][x].
    """
    for xsize, ysize, xoff, yoff in windows(ras, size=size):
        yield ras.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize)
