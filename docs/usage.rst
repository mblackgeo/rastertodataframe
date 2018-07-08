=====
Usage
=====

To use Raster To DataFrame in a project::

    from rastertodataframe import raster_to_dataframe

    raster_path = '/some/gdal/compatible/file.tif'
    vector_path = '/some/ogr/compatible/file.geojson'

    # Extract all image pixels (no vector).
    df = raster_to_dataframe(raster_path)

    # Extract only pixels the vector touches and include the vector metadata.
    df = raster_to_dataframe(raster_path, vector_path=vector_path)
