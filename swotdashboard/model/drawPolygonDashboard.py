import panel as pn
import random
import pathlib
import xarray as xr

import ipyleaflet

from .dashboard import Dashboard
from .streams import PolygonDrawStream
from . import utils


class PolygonDrawDashboard(Dashboard):

    polyStream = PolygonDrawStream()

    def __init__(self, config_file):

        super(PolygonDrawDashboard, self).__init__(config_file)

        self._titleStr = '## Polygon Draw Time Series'

        self._title = pn.pane.Markdown(self._titleStr, width=400)

        self._basemap = self.getBaseMap()

        self._drawControl = ipyleaflet.DrawControl(
            polygon={'shapeOptions': {'color': '#0000FF'}}, marker={})

        self._basemap.add_control(self._drawControl)

        # DEV ONLY

        # Add in dummy dataset
        merra_dir = pathlib.Path(
            '/explore/nobackup/people/cssprad1/' +
            'projects/swot-dashboard/data/merra')
        merra_files = merra_dir.glob('*.nc4')
        self._datasets = {'MERRA': xr.open_mfdataset(
            merra_files).resample(time='1D').mean()}

    # ------------------------------------------------------------------------
    # onMapInteractionCallback
    # ------------------------------------------------------------------------
    @staticmethod
    def onMapInteractionCallback(*args, **kwargs):

        if not kwargs['action'] == 'created':
            return

        print(kwargs)

        geometryDict = kwargs['geo_json']['geometry']

        print(geometryDict)

        PolygonDrawDashboard.polyStream.event(polygon=geometryDict)

    # ------------------------------------------------------------------------
    # generateTimeSeriesGrid
    # ------------------------------------------------------------------------
    def generateTimeSeriesGrid(self, timeSeriesList, timeAveraged,
                               step, exportToCSV):

        timeAve = True if timeAveraged == 'Time Averaged' else False

        ncols = self.NCOLS
        nrows = (len(timeSeriesList)//2)+1

        totalCol = pn.Column()

        gBox = pn.GridBox(ncols=ncols, nrows=nrows)

        for _, ts in enumerate(timeSeriesList):

            color = self.COLORS[random.randint(
                0, len(self.COLORS)-1)]

            # DEV TODO Add selecting
            xarrayTS = self._datasets['MERRA'][ts]

            rasterTS = xarrayTS.resample(time=step).mean(
                dim='time') if timeAve else xarrayTS

            gBox.append(pn.bind(
                utils.plotByPolygon,
                polygonDict=PolygonDrawDashboard.polyStream.param.polygon,
                datarray=rasterTS,
                color=color,
                # title=title,
                export=exportToCSV,
                # path='{}.csv'.format(varShortName),
                # ylabel=ylabel,
                collapse=False))

        totalCol.append(gBox)

        return totalCol

    # ------------------------------------------------------------------------
    # setStreamsAndBinds
    # ------------------------------------------------------------------------
    def setStreamsAndBinds(self):

        # Streaming definitions.
        self._drawControl.on_draw(self.onMapInteractionCallback)

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
            self._interactivityManager.toggleCSVExportWidget.value))

        self.setWatchers()

        widgetBox = self.getWidgetBox()
        baseMapRow = pn.Row(self._basemap, min_height=400,)

        baseMapCard = baseMapRow
        timeSeriesCard = pn.Card(self.timeSeriesColumn)
        baseMapTimeSeries = pn.Column(baseMapCard,
                                      self._title,
                                      timeSeriesCard)

        lowerRow = pn.Row(widgetBox, baseMapTimeSeries)
        dashboard = pn.Column(titleRow,
                              lowerRow,
                              background='WhiteSmoke')

        return dashboard
