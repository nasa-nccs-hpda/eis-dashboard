import holoviews as hv
from holoviews import opts, streams
import panel as pn
import random
import pathlib
import xarray as xr

from ipyleaflet import Marker
import ipywidgets as widgets

from .dashboard import Dashboard
from .clickStream import ClickStream
from . import utils


class PointDashBoard(Dashboard):

    marker = Marker(location=(0, 0))
    clickStream = ClickStream()
    lastLocation = (0, 0)

    def __init__(self, config_file):

        super(PointDashBoard, self).__init__(config_file)

        self._boundTitle = self.updateTitle(0, 0)

        self.bufferInput = pn.widgets.FloatInput(
            name='Buffer (degrees)', value=0.1)

        self._basemap = self.getBaseMap()

        PointDashBoard.marker = Marker(location=(37.6069, -120.8762))

        self._basemap.add_layer(PointDashBoard.marker)

        # DEV ONLY
        merra_dir = pathlib.Path(
            '/explore/nobackup/people/cssprad1/projects/swot-dashboard/data/merra')
        merra_files = merra_dir.glob('*.nc4')
        self._datasets = {'MERRA': xr.open_mfdataset(
            merra_files).resample(time='1D').mean()}
    # ------------------------------------------------------------------------
    # preprocess
    # ------------------------------------------------------------------------

    @staticmethod
    def onMapInteractionCallback(**kwargs):
        if kwargs['type'] == 'click':
            lat, lon = kwargs['coordinates']
            # Update the marker position
            PointDashBoard.marker.location = (lat, lon)
            PointDashBoard.clickStream.event(lat=lat, lon=lon)
            PointDashBoard.lastLocation = (lat, lon)

    # ------------------------------------------------------------------------
    # updateTitle
    # ------------------------------------------------------------------------
    def updateTitle(self, lat, lon):
        ret = '## Point Selected: ({}, {})'.format(
            round(lat, 4), round(lon, 4))
        return pn.pane.Markdown(ret, width=400)

    # ------------------------------------------------------------------------
    # generateTimeSeriesGrid
    # ------------------------------------------------------------------------
    def generateTimeSeriesGrid(self, timeSeriesList, timeAveraged,
                               step, exportToCSV, buffer):
        timeAve = True if timeAveraged == 'Time Averaged' else False
        ncols = 2
        nrows = (len(timeSeriesList)//2)+1
        totalCol = pn.Column()
        gBox = pn.GridBox(ncols=ncols, nrows=nrows)
        for i, ts in enumerate(timeSeriesList):

            color = PointDashBoard.COLORS[random.randint(
                0, len(PointDashBoard.COLORS)-1)]

            xarrayTS = self._datasets['MERRA'][ts]

            rasterTS = xarrayTS.resample(time=step).mean(
                dim='time') if timeAve else xarrayTS

            ds = utils.plotTS(rasterTS, PointDashBoard.clickStream.param.lat,
                              PointDashBoard.clickStream.param.lon)

            addTimeSeriesPlot = ds.hvplot('time', color=color,
                                          grid=True)

            gBox.append(addTimeSeriesPlot.dmap())

        totalCol.append(gBox)

        return totalCol

    # ------------------------------------------------------------------------
    # setStreamsAndBinds
    # ------------------------------------------------------------------------
    def setStreamsAndBinds(self):

        # Streaming definitions.
        self._basemap.on_interaction(PointDashBoard.onMapInteractionCallback)

        lat = PointDashBoard.clickStream.param.lat

        lon = PointDashBoard.clickStream.param.lon

        self._boundTitle = pn.bind(self.updateTitle, lat=lat, lon=lon)

    # --------------------------------------------------------------4----------
    # setWatchers
    # ------------------------------------------------------------------------
    def setWatchers(self):
        # Callback initializations.
        self._interactivityManager.timeSeriesVariableWidget.param.watch(
            self.updateTimeSeries, 'value')
        self._interactivityManager.timeAveragedSequentialRadioWidget.param.watch(
            self.updateTimeSeries, 'value')
        self._interactivityManager.timeStepInputWidget.param.watch(
            self.updateTimeSeries, 'value')
        self._interactivityManager.toggleCSVExportWidget.param.watch(
            self.updateTimeSeries, 'value')
        self.bufferInput.param.watch(self.updateTimeSeries, 'value')

    # ------------------------------------------------------------------------
    # view
    # ------------------------------------------------------------------------
    def view(self):
        """
        Main view for the dashboard. Returns a complete dashboard renderable
        in Jupyter Notebooks.
        Defines and initializes streams, panel compenents
        that need to be defined closest to user invocation.
        """
        self.setStreamsAndBinds()

        # Partial dashboard initializations.
        title, subtitle = self.getTitles()
        titleRow = pn.Row(pn.Column(title, subtitle))

        self.timeSeriesColumn = pn.Column(self.generateTimeSeriesGrid(
            self._interactivityManager.timeSeriesVariableWidget.value,
            self._interactivityManager.timeAveragedSequentialRadioWidget.value,
            self._interactivityManager.timeStepInputWidget.value,
            self._interactivityManager.toggleCSVExportWidget.value,
            self.bufferInput.value))

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
                              # baseMapCard,
                              lowerRow,
                              background='WhiteSmoke')

        return dashboard
