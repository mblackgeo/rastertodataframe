===================
Raster To DataFrame
===================


.. image:: https://img.shields.io/pypi/v/rastertodataframe.svg
        :target: https://pypi.python.org/pypi/rastertodataframe
        :alt: PyPI Status

.. image:: https://img.shields.io/travis/mblack20/rastertodataframe.svg
        :target: https://travis-ci.org/mblack20/rastertodataframe
        :alt: Build Status

.. image:: https://readthedocs.org/projects/rastertodataframe/badge/?version=latest
        :target: https://rastertodataframe.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/mblack20/rastertodataframe/badge.svg?branch=master
        :target: https://coveralls.io/github/mblack20/rastertodataframe?branch=master
        :alt: Coverage Status



A simple python module that converts a raster to a Pandas DataFrame.

.. code-block:: python

   from rastertodataframe import raster_to_dataframe

   raster_path = '/some/gdal/compatible/file.tif'
   vector_path = '/some/ogr/compatible/file.geojson'

   # Extract all image pixels (no vector).
   df = raster_to_dataframe(raster_path)

   # Extract only pixels the vector touches and include the vector metadata.
   df = raster_to_dataframe(raster_path, vector_path=vector_path)


* Free software: MIT license
* Documentation: https://rastertodataframe.readthedocs.io.


Features
--------

* Convert any GDAL compatible raster to a Pandas DataFrame.
* Optionally, if any OGR compatible vector file is given, only pixels touched by the vector are extracted from the raster. The output DataFrame includes these pixels as well as any attributed from the vector file.


Installation
------------

* A working GDAL/OGR installation is required. This is best accomplished with ``conda``.
* Clone this repository and install with ``pip install -e /path/to/rastertodataframe``.
* Coming soon: ``pip install rastertodataframe``.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
