from .dashboard import Dashboard
from .streams import ClickStream
from . import utils

import random

from ipyleaflet import Marker
import panel as pn


# -----------------------------------------------------------------------------
# PointDashBoard
# Point and click dashboard
# -----------------------------------------------------------------------------
class PointDashBoard(Dashboard):

    marker = Marker(location=(0, 0))
    clickStream = ClickStream()
    LAST_LOCATION = (0, 0)

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, config_file):

        super(PointDashBoard, self).__init__(config_file)

        self._boundTitle = self.updateTitle(*self._centerBounds)

        self._basemap = self.getBaseMap()

        PointDashBoard.marker = Marker(location=self._centerBounds)

        self._basemap.add_layer(PointDashBoard.marker)

    # -------------------------------------------------------------------------
    # preprocess
    # -------------------------------------------------------------------------
    @staticmethod
    def onMapInteractionCallback(*args, **kwargs):

        if kwargs['type'] == 'click':

            lat, lon = kwargs['coordinates']

            # Update the marker position
            PointDashBoard.marker.location = (lat, lon)

            PointDashBoard.clickStream.event(lat=lat, lon=lon)

            PointDashBoard.lastLocation = (lat, lon)

    # -------------------------------------------------------------------------
    # updateTitle
    # -------------------------------------------------------------------------
    def updateTitle(self, lat, lon):

        ret = '## Point Selected: ({}, {})'.format(
            round(lat, 4), round(lon, 4))

        self._logger.debug(f'Setting title to: {ret}')

        return pn.pane.Markdown(ret, width=400)

    # -------------------------------------------------------------------------
    # generateTimeSeriesGrid
    # -------------------------------------------------------------------------
    def generateTimeSeriesGrid(self, timeSeriesList, timeAveraged,
                               step, exportToCSV, dateRange):

        self._logger.debug('Generating new time series from options:')
        self._logger.debug(timeSeriesList)

        timeAve = True if timeAveraged == 'Time Averaged' else False

        ncols = self.NCOLS
        nrows = (len(timeSeriesList)//2)+1

        totalCol = pn.Column()

        gBox = pn.GridBox(ncols=ncols, nrows=nrows)

        for _, collectVariableOption in enumerate(timeSeriesList):

            collectionID, variable = self.parseVariableOption(
                collectVariableOption)

            if variable in self.BANNED_VARIABLES:
                continue

            color = PointDashBoard.COLORS[random.randint(
                0, len(PointDashBoard.COLORS)-1)]

            xarrayTS = self._datasetsData[collectionID][variable]

            rasterTS = xarrayTS.resample(time=step).mean(
                dim='time') if timeAve else xarrayTS

            ds = utils.plotTS(rasterTS,
                              PointDashBoard.clickStream.param.lat,
                              PointDashBoard.clickStream.param.lon)

            addTimeSeriesPlot = ds.hvplot('time',
                                          color=color,
                                          grid=True)

            gBox.append(addTimeSeriesPlot.dmap())

        totalCol.append(gBox)

        return totalCol

    # -------------------------------------------------------------------------
    # setStreamsAndBinds
    # -------------------------------------------------------------------------
    def setStreamsAndBinds(self):

        # Streaming definitions.
        self._basemap.on_interaction(PointDashBoard.onMapInteractionCallback)

        lat = PointDashBoard.clickStream.param.lat

        lon = PointDashBoard.clickStream.param.lon

        self._boundTitle = pn.bind(self.updateTitle, lat=lat, lon=lon)

    # -------------------------------------------------------------------------
    # view
    # -------------------------------------------------------------------------
    def view(self):
        """
        Main view for the dashboard. Returns a complete dashboard renderable
        in Jupyter Notebooks.
        Defines and initializes streams, panel compenents
        that need to be defined closest to user invocation.
        """
        self._logger.debug('Setting streams and binds')
        self.setStreamsAndBinds()

        # Partial dashboard initializations.
        title, subtitle = self.getTitles()
        titleRow = pn.Row(pn.Column(title, subtitle))

        errorRow = pn.Row(
            self._interactivityManager.exceptionCommWidget,
        )

        try:

            timeSeriesGrid = self.generateTimeSeriesGrid(
                self._interactivityManager.timeSeriesVariableWidget.value,
                self._interactivityManager.timeAveragedSequentialRadioWidget.
                value,
                self._interactivityManager.timeStepInputWidget.value,
                self._interactivityManager.toggleCSVExportWidget.value,
                self._interactivityManager.dateTimeRangeWidget.value)

        except Exception as exceptionCaptured:

            step = 'Initial generation of the time series grid'

            self.exeptionHandler(exceptionCaptured, step)

            # ---
            # Panel will accept a none-type object when put in a panel
            # organizational object such as column, row, etc.
            # ---
            timeSeriesGrid = None

        self.timeSeriesColumn = pn.Column(timeSeriesGrid)

        self.setWatchers()

        widgetBox = self.getWidgetBox()
        baseMapRow = pn.Row(self._basemap, min_height=400,)

        baseMapCard = baseMapRow
        timeSeriesCard = pn.Card(self.timeSeriesColumn)
        baseMapTimeSeries = pn.Column(baseMapCard,
                                      self._boundTitle,
                                      timeSeriesCard)

        lowerRow = pn.Row(widgetBox, baseMapTimeSeries)
        dashboard = pn.Column(titleRow,
                              errorRow,
                              lowerRow,
                              background='WhiteSmoke')

        return dashboard
