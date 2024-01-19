import ipyleaflet
import panel as pn
import random

from eisdashboard.model.dashboard import Dashboard
from eisdashboard.model.streams import PolygonDrawStream
import eisdashboard.model.utils as utils


# -----------------------------------------------------------------------------
# PolygonDrawDashboard
# Polygon draw dashboard
# -----------------------------------------------------------------------------
class PolygonDrawDashboard(Dashboard):
    polyStream = PolygonDrawStream()

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, config_file):
        super(PolygonDrawDashboard, self).__init__(config_file)

        self._basemap = self.getBaseMap()

        self._drawControl = ipyleaflet.DrawControl(
            polygon={"shapeOptions": {"color": "#0000FF"}},
            circlemarker={}, polyline={}
        )
        # ---
        # In order for these to not show up they need to be
        # empty dicts
        # ---

        self._basemap.add_control(self._drawControl)

    # ------------------------------------------------------------------------
    # onMapInteractionCallback
    # ------------------------------------------------------------------------
    @staticmethod
    def onMapInteractionCallback(*args, **kwargs):
        if not kwargs["action"] == "created":
            return

        geometryDict = kwargs["geo_json"]["geometry"]

        # Need to make sure we only accept polygons
        if geometryDict["type"] != "Polygon":
            return

        PolygonDrawDashboard.polyStream.event(polygon=geometryDict)

    # ------------------------------------------------------------------------
    # generateTimeSeriesGrid
    # ------------------------------------------------------------------------
    def generateTimeSeriesGrid(self, timeSeriesList, timeAveraged, step,
                               exportToCSV):
        # Logging and status reporting
        self._logger.debug("Generating new time series from options:")
        self._logger.debug(timeSeriesList)
        self.indicateStatus("Updating time-series")

        timeAve = True if timeAveraged == "Time Averaged" else False

        ncols = self.NCOLS
        nrows = (len(timeSeriesList) // 2) + 1

        numTimeSeries = len(timeSeriesList)

        totalCol = pn.Column()

        gBox = pn.GridBox(ncols=ncols, nrows=nrows)

        for i, collectVariableOption in enumerate(timeSeriesList):
            self.indicateStatus(f"Adding time-series {i+1}/{numTimeSeries}")

            collectionID, variable = \
                self.parseVariableOption(collectVariableOption)

            if variable in self.BANNED_VARIABLES:
                continue

            color = self.COLORS[random.randint(0, len(self.COLORS) - 1)]

            xarrayTS = self._datasetsData[collectionID][variable]

            rasterTS = (
                xarrayTS.resample(time=step).mean(dim="time") if timeAve
                else xarrayTS
            )

            if exportToCSV:
                self._logger.debug(f"Writing {collectVariableOption} to csv")
                # Actual exporting is handled in the plotByPolygon function
                # this is done because it handles clipping, etc.

            gBox.append(
                pn.bind(
                    utils.plotByPolygon,
                    polygonDict=PolygonDrawDashboard.polyStream.param.polygon,
                    datarray=rasterTS,
                    color=color,
                    title=f"{collectionID} {variable}",
                    export=exportToCSV,
                    path=f"{collectionID}_{variable}.csv",
                    collapse=False,
                )
            )

        totalCol.append(gBox)

        self.indicateStatus("Finished adding time-series")

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
        self._logger.debug("Setting streams and binds")
        self.setStreamsAndBinds()

        # Partial dashboard initializations.
        title, subtitle = self.getTitles()
        titleRow = pn.Row(pn.Column(title, subtitle))

        errorRow = pn.Row(
            self._interactivityManager.exceptionCommWidget,
        )

        statusRow = pn.Row(
            self._interactivityManager.statusIndicatorWidget,
        )

        try:
            timeSeriesGrid = self.generateTimeSeriesGrid(
                self._interactivityManager.timeSeriesVariableWidget.value,
                self._interactivityManager.
                timeAveragedSequentialRadioWidget.value,
                self._interactivityManager.timeStepInputWidget.value,
                self._interactivityManager.toggleCSVExportWidget.value,
            )

        except Exception as exceptionCaptured:
            step = "Initial generation of the time series grid"

            self.exeptionHandler(exceptionCaptured, step)

            # ---
            # Panel will accept a none-type object when put in a panel
            # organizational object such as column, row, etc.
            # ---
            timeSeriesGrid = None

        self.timeSeriesColumn = pn.Column(timeSeriesGrid)

        self.setWatchers()

        widgetBox = self.getWidgetBox()
        baseMapRow = pn.Row(
            self._basemap,
            min_height=400,
            min_width=800,
        )

        baseMapCard = baseMapRow
        timeSeriesCard = pn.Card(self.timeSeriesColumn)
        baseMapTimeSeries = pn.Column(baseMapCard, timeSeriesCard)

        lowerRow = pn.Row(widgetBox, baseMapTimeSeries)
        dashboard = pn.Column(
            titleRow, errorRow, statusRow, lowerRow, background="WhiteSmoke"
        )

        return dashboard
