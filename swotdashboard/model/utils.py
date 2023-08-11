import numpy as np
import pandas
import os
# import s3fs
import xarray as xr

import geopandas as gpd
import pandas as pd
import hvplot.pandas
import hvplot.xarray
import panel as pn
import rioxarray as rio
from shapely.geometry import mapping, Point


def clip_to_shape(raster, shape_file):
    """Given a raster and geometry, clip raster to the given geometry."""
    raster.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    raster.rio.write_crs("epsg:4326", inplace=True)
    raster_clipped = raster.rio.clip(
        shape_file.geometry.apply(mapping), shape_file.crs, drop=False)
    return raster_clipped


def collapseTo1D(datarray):
    """Collapse lat/lon via sum given an xarray."""
    dataCollapsed = datarray.sum(axis=1).compute()
    dataCollapsed = dataCollapsed.sum(axis=1).compute()
    return dataCollapsed


def collapseMean(datarray):
    """Load dat and collapse to averaged lat/lon"""
    datarray = datarray.load()
    dataCollapsed = datarray.mean(['lat']).compute()
    dataCollapsed = dataCollapsed.mean(['lon']).compute()
    return dataCollapsed


def plotTS(datarray, lat, lon):
    """Plot time-series given a xarray dataarray and lat/lon"""
    datarray = datarray.load()
    dataSelected = datarray.interactive.sel(lon=lon,
                                            lat=lat,
                                            method='nearest')
    return dataSelected


def plotByIndex(shape, index, datarray, collapse, color='red', title='test',
                export=False, path='.', ylabel='test'):
    """Given an index for a shape, clip raster data to shape geometry"""
    if not index:
        return '### Nothing selected'
    shape = gpd.GeoDataFrame(shape.loc[[index[0]], 'geometry'])
    daLoaded = datarray  # .load()
    daLoaded = clip_to_shape(daLoaded, shape)
    daLoaded = collapseTo1D(daLoaded) if collapse else collapseMean(daLoaded)
    if export:
        daLoaded.to_pandas().to_csv(path)

    timeSeriesPlot = daLoaded.hvplot('time', title=title, color=color,
                                     ylabel=ylabel, grid=True)
    return timeSeriesPlot


def spatiallyAverageByIndex(shape, index, datarray, collapse):
    """Given an index for a shape, clip raster data to shape geometry"""
    if not index:
        return '### Nothing selected'
    print(type(index))
    shape = gpd.GeoDataFrame(shape.loc[[index[0]], 'geometry'])
    daLoaded = datarray.load()
    daLoaded = clip_to_shape(daLoaded, shape)
    daLoaded = collapseTo1D(daLoaded) if collapse else collapseMean(daLoaded)
    return daLoaded
