import geopandas as gpd
from shapely.geometry import Polygon
from datetime import datetime
import rioxarray
import logging


# -----------------------------------------------------------------------------
# clip_to_shape
# -----------------------------------------------------------------------------
def clip_to_shape(raster, geometry):
    """Given a raster and geometry, clip raster to the given geometry."""
    raster.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    raster.rio.write_crs("epsg:4326", inplace=True)
    raster_clipped = raster.rio.clip([geometry], crs=4326, drop=True)
    return raster_clipped


# -----------------------------------------------------------------------------
# collapseTo1D
# -----------------------------------------------------------------------------
def collapseTo1D(datarray):
    """Collapse lat/lon via sum given an xarray."""
    dataCollapsed = datarray.sum(axis=1)
    dataCollapsed = dataCollapsed.sum(axis=1)
    return dataCollapsed


# -----------------------------------------------------------------------------
# collapseMean
# -----------------------------------------------------------------------------
def collapseMean(datarray):
    """Load dat and collapse to averaged lat/lon"""
    # datarray = datarray.load()
    dataCollapsed = datarray.mean(['lat']).compute()
    dataCollapsed = dataCollapsed.mean(['lon']).compute()
    return dataCollapsed


# -----------------------------------------------------------------------------
# plotTS
# -----------------------------------------------------------------------------
def plotTS(datarray, lat, lon):
    """Plot time-series given a xarray dataarray and lat/lon"""
    datarray = datarray.load()
    dataSelected = datarray.interactive.sel(lon=lon,
                                            lat=lat,
                                            method='nearest')
    return dataSelected


# -----------------------------------------------------------------------------
# plotByIndex
# -----------------------------------------------------------------------------
def plotByIndex(shape,
                index,
                datarray,
                collapse=False,
                color='red',
                title='test',
                export=False,
                path='.',
                ylabel='test'):
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


# -----------------------------------------------------------------------------
# plotByPolygon
# -----------------------------------------------------------------------------
def plotByPolygon(polygonDict,
                  datarray,
                  collapse=True,
                  color='red',
                  title='test',
                  export=False,
                  path='.',
                  ylabel='test'):
    """Given an a polygon shape, clip raster data to shape geometry"""

    coordinates = polygonDict['coordinates']

    polygon = Polygon(coordinates[0])

    logging.debug(f'Polygon from coordinates: {polygon}')

    try:
        datarrayClipped = clip_to_shape(datarray, polygon)

        datarrayReadyToPlot = collapseTo1D(datarrayClipped) if collapse \
            else collapseMean(datarrayClipped)

    # ---
    # Catch the no-data in bounds exception explicitly.
    # This covers the edge-case where the user draws a polygon smaller than
    # the geographic extent of a single pixel. We just select the entire
    # pixel and return the time-series of that instead.
    # ---
    except rioxarray.exceptions.NoDataInBounds as noDataException:

        warning_msg = 'Polygon smaller than pixel extent.' + \
            f' Defaulting to entire pixel: {noDataException}'

        logging.warning(warning_msg)

        centerPoint = polygon.centroid  # return order lon, lat

        lon, lat = centerPoint.x, centerPoint.y

        logging.debug(f'Selecting lon ({lon}), lat ({lat})')

        datarrayReadyToPlot = plotTS(datarray, lat, lon)

        logging.info(f'Setting point selection to ({lon}, {lat}')

    # ---
    # Any other exceptions we gracefully handle through returning
    # text that will be rendered where the time-series plots should
    # be.
    # ---
    except Exception as e:

        logging.error(f'Encountered unknown exception {e}. Try again.')

        return str(e)

    if export:
        datarrayReadyToPlot.to_pandas().to_csv(path)

    timeSeriesPlot = datarrayReadyToPlot.hvplot('time',
                                                title=title,
                                                color=color,
                                                ylabel=ylabel,
                                                grid=True)

    return timeSeriesPlot


# -----------------------------------------------------------------------------
# spatiallyAverageByIndex
# -----------------------------------------------------------------------------
def spatiallyAverageByIndex(shape, index, datarray, collapse):
    """Given an index for a shape, clip raster data to shape geometry"""
    if not index:
        return '### Nothing selected'

    shape = gpd.GeoDataFrame(shape.loc[[index[0]], 'geometry'])
    daLoaded = datarray.load()
    daLoaded = clip_to_shape(daLoaded, shape)
    daLoaded = collapseTo1D(daLoaded) if collapse else collapseMean(daLoaded)
    return daLoaded


# -----------------------------------------------------------------------------
# ParseDate
# -----------------------------------------------------------------------------
def parseDate(dateString):
    """_summary_

    Args:
        dateString (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    try:
        # Attempt to parse the input string using the specified format
        dateObj = datetime.strptime(dateString, "%Y-%m-%d")
        return dateObj
    except ValueError:
        # Handle the case where the input string is not in the expected format
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")


# -------------------------------------------------------------------------
# updateTitle
# -------------------------------------------------------------------------
def makeAllQueryPackages(collectionIDs: list, dateRange: tuple, coords: list):

    queryPackageForEachCollection = []

    for collection in collectionIDs:

        queryPackage = makeQueryPackage(dateRange, coords, collection)

        queryPackageForEachCollection.append(queryPackage)

    return queryPackageForEachCollection


# -------------------------------------------------------------------------
# updateTitle
# -------------------------------------------------------------------------
def makeQueryPackage(dateRange: tuple, coords: list, collectionID: str):

    dateBegin, dateEnd = dateRange

    datetimeStr = f"{dateBegin.isoformat()}Z," + \
        f"{dateEnd.isoformat()}Z"

    queryPackage = {'spatialParameter': 'bounding_box',
                    'coords': coords,
                    'datetime': datetimeStr,
                    'collection_id': collectionID}
    return queryPackage
