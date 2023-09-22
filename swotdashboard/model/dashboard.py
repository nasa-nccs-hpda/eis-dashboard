import swotdashboard.model.utils as dashboard_utils
from swotdashboard.model.data.ingest import Ingest
from swotdashboard.model.interactivity import InteractivityManager
from swotdashboard.model.common import read_config

from typing import Tuple

from ipyleaflet import Map, basemaps
import ipywidgets as widgets
import panel as pn


# ------------------------------------------------------------------------
# DashBoard
# Base class for EIS General Dashboard
# ------------------------------------------------------------------------
class Dashboard(object):

    COLORS = ['red', 'blue', 'green', 'black', 'indianred', 'grey',
              'maroon', 'orange', 'gold', 'darkgreen', 'darkslategrey',
              'steelblue', 'purple', 'crimson']

    HEADER_BG_COLOR: str = '#0059b3'
    HEADER_COLOR: str = 'white'
    HEADER_ACTIVE_BG_COLOR: str = '#339966'

    WIDGET_BOX_HEIGHT: int = 800
    TITLE_WIDTH: int = 600

    NCOLS: int = 2

    BANNED_VARIABLES: list = ['lat', 'lon', 'time']

    # ------------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------------
    def __init__(self, config_file):

        self._conf = read_config(config_file)

        self._start_date = self._conf['time_bounds']['start']
        self._end_date = self._conf['time_bounds']['end']

        self._bounds = list(self._conf['bounds'][0])

        self._centerBounds = self.getCenterOfBoundingBox()

        self._start_date = dashboard_utils.parseDate(self._start_date)
        self._end_date = dashboard_utils.parseDate(self._end_date)

        # Cols for dashboard
        self.timeSeriesColumn = pn.Column()

        self.mapColumn = pn.Column()

        self.gridBox = pn.GridBox()

        self._interactivityManager = InteractivityManager(self._conf)

        self._ingest = Ingest(self._conf)

        self._datasetsData = {}

        self._datasetsVariables = {}

        self.initializeData()

        self._variableOptions = self.initializeVariableOptions()

        # Now that we have all of the variable options, populate the widget
        # with these options
        self._interactivityManager._timeSeriesVariablesWidget.options = \
            self._variableOptions

    # ------------------------------------------------------------------------
    # initializeData
    # ------------------------------------------------------------------------
    def initializeData(self):

        boundingBox: list = self._bounds
        collectionIDs = list(self._conf['collections']['ids'])
        dateRange = (self._start_date, self._end_date)

        print(type(boundingBox[0]))
        print(collectionIDs)

        queryPackages = dashboard_utils.makeAllQueryPackages(collectionIDs,
                                                             dateRange,
                                                             boundingBox)

        print(queryPackages)

        for queryPackage in queryPackages:

            dataPackage = self._ingest.get_data_from_bounds(queryPackage)

            self._datasetsData[dataPackage['key']] = dataPackage['data']

            self._datasetsVariables[dataPackage['key']] = \
                dataPackage['variables']

        print(self._datasetsVariables)

    # ------------------------------------------------------------------------
    # initializeVariableOptions
    # ------------------------------------------------------------------------
    def initializeVariableOptions(self):
        # TODO: map this later, this is not the most efficient
        allOptions: list = []

        for key in self._datasetsVariables.keys():

            variablesForThisCollection: list = self._datasetsVariables[key]

            for variable in variablesForThisCollection:

                variableOptionStr: str = f'{key}:{variable}'

                allOptions.append(variableOptionStr)

        print(allOptions)
        return allOptions

    # ------------------------------------------------------------------------
    # parseVariableOption
    # ------------------------------------------------------------------------
    def parseVariableOption(self, variableOption: str):
        # Called by the updateTimeSeries Function

        collectionID, variableName = variableOption.split(':')

        return (collectionID, variableName)

    # ------------------------------------------------------------------------
    # getTitles
    # ------------------------------------------------------------------------
    def getTitles(self) -> Tuple[pn.pane.Markdown, pn.pane.Markdown]:

        title = pn.pane.Markdown(self._conf.title.title,
                                 width=self.TITLE_WIDTH)

        subtitle = pn.pane.Markdown(self._conf.title.subtitle)

        return title, subtitle

    # ------------------------------------------------------------------------
    # getWidgetBox
    # ------------------------------------------------------------------------
    def getWidgetBox(self):

        layerAccordion = self.getLayerAccordion(
            self._interactivityManager.layerSelection)

        widgetBox = pn.WidgetBox(
            self._interactivityManager.timeAveragedSequentialRadioWidget,
            layerAccordion,
            self._interactivityManager.timeStepInputWidget,
            self._interactivityManager.timeSeriesVariableWidget,
            self._interactivityManager.dateTimeRangeWidget,
            self._interactivityManager.toggleCSVExportWidget,
            height=self.WIDGET_BOX_HEIGHT)

        return widgetBox

    # ------------------------------------------------------------------------
    # getWidgetBox
    # ------------------------------------------------------------------------
    def getLayerAccordion(self, layerSelectionWidget):

        layerAccordion = pn.Accordion(
            ('Basemap Type', layerSelectionWidget),
            header_background=self.HEADER_BG_COLOR,
            header_color=self.HEADER_COLOR)

        return layerAccordion

    # ------------------------------------------------------------------------
    # getWidgetBox
    # ------------------------------------------------------------------------
    def getCenterOfBoundingBox(self):
        lons = self._bounds[::2]
        lats = self._bounds[1::2]

        lons_min = min(lons)
        lats_min = min(lats)

        lons_max = max(lons)
        lats_max = max(lats)

        center_lons = (lons_min + lons_max) / 2
        center_lats = (lats_min + lats_max) / 2

        center_lons = round(center_lons, 5)
        center_lats = round(center_lats, 5)

        center = (center_lats, center_lons)

        print(center)

        return center

    # ------------------------------------------------------------------------
    # getMap
    # ------------------------------------------------------------------------
    def getBaseMap(self):

        base = Map(
            center=self._centerBounds,
            zoom=5,
            basemap=basemaps.Esri.WorldImagery,
            scroll_wheel_zoom=True,
            keyboard=True,
            layout=widgets.Layout(height='400px', width='800px'),
        )

        return base

    # ------------------------------------------------------------------------
    # onMapInteractionCallback
    # ------------------------------------------------------------------------
    @staticmethod
    def onMapInteractionCallback(**kwargs):
        """
        Base function for map interaction callbacks. This should be overridden
        by the inheriting class. Each dashboard handles the interaction
        differently.
        """
        pass

    # ------------------------------------------------------------------------
    # generateTimeSeriesGrid
    # ------------------------------------------------------------------------
    def generateTimeSeriesGrid(self):
        """
        This function should be over-written by the inheriting class. This
        function handles resampling and ploting the time series. Each
        dashboard does this differently depending on the selection criteria.
        """

        pass

    # -------------------------------------------------------------------------
    # setWatchers
    # -------------------------------------------------------------------------
    def setWatchers(self):

        # Callback initializations.
        self._interactivityManager.timeSeriesVariableWidget.param.watch(
            self.updateTimeSeries, 'value')

        self._interactivityManager.timeAveragedSequentialRadioWidget.\
            param.watch(self.updateTimeSeries, 'value')

        self._interactivityManager.timeStepInputWidget.param.watch(
            self.updateTimeSeries, 'value')

        self._interactivityManager.toggleCSVExportWidget.param.watch(
            self.updateTimeSeries, 'value')

        self._interactivityManager.dateTimeRangeWidget.param.watch(
            self.updateTimeSeries, 'value')

    # ------------------------------------------------------------------------
    # updateTimeSeries
    # ------------------------------------------------------------------------
    def updateTimeSeries(self, event):

        timestepDisabledPreEvent = \
            self._interactivityManager.timeStepInputWidget.disabled

        self.timeSeriesColumn[0].loading = True

        # self._interactivityManager.dateTimeRangeWidget.disabled = True

        self._interactivityManager.timeSeriesVariableWidget.disabled = True

        self._interactivityManager.timeStepInputWidget.disabled = True

        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled \
            = True

        self._interactivityManager.dateTimeRangeWidget.disabled \
            = True

        self.timeSeriesColumn[0] = self.generateTimeSeriesGrid(
            self._interactivityManager.timeSeriesVariableWidget.value,
            self._interactivityManager.timeAveragedSequentialRadioWidget.value,
            self._interactivityManager.timeStepInputWidget.value,
            self._interactivityManager.toggleCSVExportWidget.value,
            self._interactivityManager.dateTimeRangeWidget.value)

        # self._interactivityManager.dateTimeRangeWidget.disabled = False

        self._interactivityManager.timeSeriesVariableWidget.disabled = False

        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled \
            = False

        self._interactivityManager.timeStepInputWidget.disabled = \
            timestepDisabledPreEvent

        self.timeSeriesColumn[0].loading = False


if __name__ == '__main__':
    dashboard = Dashboard(config_file='swot-dashboard/configs' +
                          '/test_config.yaml')

    print(dashboard._start_date)
    print(dashboard._end_date)
