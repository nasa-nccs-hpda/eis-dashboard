import eisdashboard.model.utils as dashboard_utils
from eisdashboard.model.data.ingest import Ingest
from eisdashboard.model.interactivity import InteractivityManager
from eisdashboard.model.common import read_config

import datetime
from typing import Tuple
import logging
import os

from ipyleaflet import Map, basemaps, ScaleControl
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

    BANNED_VARIABLES: list = ['lat', 'lon', 'time', 'time_bnds',
                              'time_bounds', 'lat_bounds', 'lon_bounds']

    # ------------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------------
    def __init__(self, config_file):

        self._conf = read_config(config_file)

        self._logger = self.initializeLogging()

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

        self._validStarterVariables = [
            var for var in self._variableOptions
            if self.parseVariableOption(var)[1].lower() not
            in self.BANNED_VARIABLES]

        self._logger.debug(self._validStarterVariables)

        self._interactivityManager._timeSeriesVariablesWidget.value = \
            [self._validStarterVariables[0]]

    # ------------------------------------------------------------------------
    # initializeLogging
    # ------------------------------------------------------------------------
    def initializeLogging(self):

        log_dir = self._conf['log_dir']
        os.makedirs(log_dir, exist_ok=True)

        formatter = logging.Formatter(
            '%(asctime)s-%(levelname)s-%(module)s:%(lineno)d-%(message)s')

        # Create a logger with default DEBUG log level
        logger = logging.getLogger()
        logger.setLevel('DEBUG')

        # ---
        # Create a console handler which overrides logging level
        # according to user-sprecified level in config.
        # ---
        log_level = getattr(logging, self._conf['log_level'].upper())
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)

        log_dt_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(
            log_dir,
            f'eis-dashboard-log-{log_dt_str}.log')
        fh = logging.FileHandler(log_filename)
        fh.setLevel('DEBUG')
        fh.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(ch)
        logger.addHandler(fh)

        return logger

    # ------------------------------------------------------------------------
    # initializeData
    # ------------------------------------------------------------------------
    def initializeData(self):
        self._logger.debug('Initializing data')

        collectionIDs = list(self._conf['nasa_earthdata_collections']['ids'])
        if collectionIDs:
            self.initializeNasaEarthdata(collectionIDs)

        customCollectionIDs = self._conf['custom_collections']['ids']

        if customCollectionIDs:
            self.initializeCustomData(customCollectionIDs)

    # ------------------------------------------------------------------------
    # initializeNasaEarthData
    # ------------------------------------------------------------------------
    def initializeNasaEarthdata(self, collectionIDs):
        self._logger.debug('Initializing nasa earthdata')

        boundingBox: list = self._bounds
        dateRange = (self._start_date, self._end_date)

        self._logger.debug(collectionIDs)

        queryPackages = dashboard_utils.makeAllQueryPackages(collectionIDs,
                                                             dateRange,
                                                             boundingBox)

        self._logger.debug(queryPackages)

        for queryPackage in queryPackages:

            dataPackage = self._ingest.get_nasa_earthdata(queryPackage)

            self._datasetsData[dataPackage['key']] = dataPackage['data']

            self._datasetsVariables[dataPackage['key']] = \
                dataPackage['variables']

        self._logger.debug(self._datasetsVariables)

    # ------------------------------------------------------------------------
    # initializeCustomData
    # ------------------------------------------------------------------------
    def initializeCustomData(self, customCollectionIDs):
        self._logger.debug('Initializing custom data')

        self._logger.debug(customCollectionIDs)

        for collectionID, s3Path in customCollectionIDs.items():

            self._logger.debug(f'collection ID: {collectionID}')
            self._logger.debug(f's3 path: {s3Path}')

            dataPackage = self._ingest.get_custom_s3_data(collectionID, s3Path)

            self._datasetsData[dataPackage['key']] = dataPackage['data']

            self._datasetsVariables[dataPackage['key']] = \
                dataPackage['variables']

        self._logger.debug(self._datasetsVariables)

    # ------------------------------------------------------------------------
    # initializeVariableOptions
    # ------------------------------------------------------------------------
    def initializeVariableOptions(self):
        # TODO: map this later, this is not the most efficient

        self._logger.debug('Initializing variable options')
        allOptions: list = []

        for key in self._datasetsVariables.keys():

            variablesForThisCollection: list = self._datasetsVariables[key]

            for variable in variablesForThisCollection:

                variableOptionStr: str = f'{key}:{variable}'

                allOptions.append(variableOptionStr)

        self._logger.debug(allOptions)
        return allOptions

    # ------------------------------------------------------------------------
    # parseVariableOption
    # ------------------------------------------------------------------------
    def parseVariableOption(self, variableOption: str):
        # Called by the updateTimeSeries Function
        self._logger.debug('Parsing variables and collectionID')

        collectionID, variableName = variableOption.split(':')

        return (collectionID, variableName)

    # ------------------------------------------------------------------------
    # getTitles
    # ------------------------------------------------------------------------
    def getTitles(self) -> Tuple[pn.pane.Markdown, pn.pane.Markdown]:
        self._logger.debug('Getting titles')

        title = pn.pane.Markdown(self._conf.title.title,
                                 width=self.TITLE_WIDTH)

        subtitle = pn.pane.Markdown(self._conf.title.subtitle)

        return title, subtitle

    # ------------------------------------------------------------------------
    # getWidgetBox
    # ------------------------------------------------------------------------
    def getWidgetBox(self):
        self._logger.debug('Getting widget box')

        widgetBox = pn.WidgetBox(
            self._interactivityManager.timeAveragedSequentialRadioWidget,
            self._interactivityManager.timeStepInputWidget,
            self._interactivityManager.timeSeriesVariableWidget,
            self._interactivityManager.toggleCSVExportWidget,
            height=self.WIDGET_BOX_HEIGHT)

        return widgetBox

    # ------------------------------------------------------------------------
    # getWidgetBox
    # ------------------------------------------------------------------------
    def getLayerAccordion(self, layerSelectionWidget):

        self._logger.debug('Getting layer accordion')

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

        self._logger.debug(f'Computing center bounds given lons: {lons}, ' +
                           f'lats: {lats}')

        lons_min = min(lons)
        lats_min = min(lats)

        lons_max = max(lons)
        lats_max = max(lats)

        center_lons = (lons_min + lons_max) / 2
        center_lats = (lats_min + lats_max) / 2

        center_lons = round(center_lons, 5)
        center_lats = round(center_lats, 5)

        center = (center_lats, center_lons)

        self._logger.debug(center)

        return center

    # ------------------------------------------------------------------------
    # getMap
    # ------------------------------------------------------------------------
    def getBaseMap(self):
        self._logger.debug('Instantiating basemap, with center of ' +
                           f'{self._centerBounds}, size: 400x400px')

        base = Map(
            center=self._centerBounds,
            zoom=5,
            basemap=basemaps.Esri.WorldImagery,
            scroll_wheel_zoom=True,
            keyboard=True,
            layout=widgets.Layout(height='400px', width='800px'),
        )

        base.add(ScaleControl(position='topright'))

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

    # ------------------------------------------------------------------------
    # exceptionHandler
    # ------------------------------------------------------------------------
    def exceptionHandler(self, exception: Exception, step: str) -> None:
        """Method that communicates to the user what exception was thrown
        and what step it occured at. This should update a warning message
        box in the dashboard view and return. The use case is that we don't
        want to error out because there will be no way for the user to know.

        Args:
            exception (Exception): exception that was thrown
            step (str): what step (e.g. updating time series)
        """
        msg = f'An error was encountered at step: {step}' + \
            ' of this dashboard. Error was: ' + \
            f' {exception}'

        self._interactivityManager.exceptionCommWidget.object = \
            f'<B>ERROR</b> {msg}'

        self._logger.error(msg)

    # ------------------------------------------------------------------------
    # resetExeptionCommWidget
    # ------------------------------------------------------------------------
    def resetExeptionCommWidget(self) -> None:
        """Resets the interactivity manager back to normal"""

        msg = ''

        self._interactivityManager.exceptionCommWidget.object = msg

    # ------------------------------------------------------------------------
    # indicateStatus
    # ------------------------------------------------------------------------
    def indicateStatus(self, step: str) -> None:
        """Method that communicates to the user current status of the
        dashboard.

        Args:
            step (str): what step (e.g. updating time series)
        """

        self._interactivityManager.statusIndicatorWidget.object = \
            f'<B>Status:</b> {step}'

        self._logger.debug(f'Updated status to :{step}')

    # -------------------------------------------------------------------------
    # setWatchers
    # -------------------------------------------------------------------------
    def setWatchers(self):
        self._logger.debug('Setting watchers; update time-series when changed')

        # Callback initializations.
        self._interactivityManager.timeSeriesVariableWidget.param.watch(
            self.updateTimeSeries, 'value')

        self._interactivityManager.timeAveragedSequentialRadioWidget.\
            param.watch(self.updateTimeSeries, 'value')

        self._interactivityManager.timeStepInputWidget.param.watch(
            self.updateTimeSeries, 'value')

        self._interactivityManager.toggleCSVExportWidget.param.watch(
            self.updateTimeSeries, 'value')

    # ------------------------------------------------------------------------
    # updateTimeSeries
    # ------------------------------------------------------------------------
    def updateTimeSeries(self, event):

        self.resetExeptionCommWidget()
        statusMsg = 'Updating time-series with selected options, ' + \
            'freezing all widgets'
        self._logger.debug(statusMsg)
        self.indicateStatus(statusMsg)

        timestepDisabledPreEvent = \
            self._interactivityManager.timeStepInputWidget.disabled

        self.timeSeriesColumn[0].loading = True

        self._interactivityManager.timeSeriesVariableWidget.disabled = True

        self._interactivityManager.timeStepInputWidget.disabled = True

        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled \
            = True

        try:
            self.timeSeriesColumn[0] = self.generateTimeSeriesGrid(
                self._interactivityManager.timeSeriesVariableWidget.value,
                self._interactivityManager.timeAveragedSequentialRadioWidget.
                value,
                self._interactivityManager.timeStepInputWidget.value,
                self._interactivityManager.toggleCSVExportWidget.value)

        # ---
        # This handles any error encountered from generateTimeSeriesGrid.
        # we assume that the previous return of time series was fine
        # so we will fall back to that. The user is not expected to move
        # be able to fix it at the dashboard view.
        # ---
        except Exception as exceptionCaptured:
            step = 'Updating the time series grid'
            self.exceptionHandler(exceptionCaptured, step)

        statusMsg = 'Completed update, unfreezing widgets'

        self._logger.debug(statusMsg)

        self.indicateStatus(statusMsg)

        self._interactivityManager.timeSeriesVariableWidget.disabled = False

        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled \
            = False

        self._interactivityManager.timeStepInputWidget.disabled = \
            timestepDisabledPreEvent

        self.timeSeriesColumn[0].loading = False

        self.indicateStatus('Idle')


if __name__ == '__main__':
    dashboard = Dashboard(config_file='configs/dev_configs' +
                          '/test_config.yaml')

    print(dashboard._start_date)
    print(dashboard._end_date)
