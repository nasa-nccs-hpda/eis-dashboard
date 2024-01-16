from eisdashboard.model.dashboard import Dashboard
import panel as pn


# -----------------------------------------------------------------------------
# rasterDashboard
# Raster dashboard
# -----------------------------------------------------------------------------

class RasterDashboard(Dashboard):

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------

    def __init__(self, config_file):
        super(RasterDashboard, self).__init__(config_file)

        self._basemap = self.getBaseMap()

        # Populating Variable Select Options
        self._interactivityManager._rasterVariableSelectWidget.options = \
            self._validStarterVariables
        self._interactivityManager._rasterVariableSelectWidget.value = \
            [self._validStarterVariables[0]]

        # Popultating Time Select Options
        self._tstampsOptions = self.initializeTimeStampsOptions()
        self._interactivityManager._rasterTimeSelectWidget.options = \
            self._tstampsOptions
        self._interactivityManager._rasterTimeSelectWidget.value = \
            [self._tstampsOptions[0]]

    # ------------------------------------------------------------------------
    # initializeTimeStampsOptions
    # As "initializeVariableOptions" in dashboard.py
    # ------------------------------------------------------------------------
    def initializeTimeStampsOptions(self):

        allOptions: list = []
        for key in self._datasetsVariables.keys():
            tstampsForThisCollection = self._datasetsData[key].time.values
            tstampsStr = [f'{e}' for e in tstampsForThisCollection]

            allOptions.extend(tstampsStr)

        return allOptions

    # ------------------------------------------------------------------------
    # Generate raster plot
    # ------------------------------------------------------------------------

    # TODO
    # Add option for colormap (cmap)
    def generateRasterLayer(self, varOpt, timeOpt):

        collectionID, variable = self.parseVariableOption(varOpt)
        time = timeOpt

        ds = self._datasetsData[collectionID][variable].sel(time=time).load()

        rasterLayer = ds.hvplot.quadmesh(
            x='lon', y='lat',
            geo=True,
            cmap='jet',
            rasterize=True,
            frame_width=1200,
            title=f'{collectionID}; {variable}; {time}',
            tiles='EsriImagery',
        )

        return rasterLayer

    # ------------------------------------------------------------------------
    # Override getWidgetBox
    # ------------------------------------------------------------------------
    def getWidgetBox(self):
        self._logger.info('Getting widget box in RasterDashboard')

        widgetBox = pn.WidgetBox(
            self._interactivityManager.rasterVariableSelectWidget,
            self._interactivityManager.rasterTimeSelectWidget,
            height=self.WIDGET_BOX_HEIGHT
        )

        return widgetBox

    # ------------------------------------------------------------------------
    # View
    # ------------------------------------------------------------------------

    def view(self):
        """
        Main view for the dashboard. Returns a complete dashboard renderable
        in Jupyter Notebooks.
        Defines and initializes streams, panel compenents
        that need to be defined closest to user invocation.
        """

        # Title initializing
        title, subtitle = self.getTitles()
        titleRow = pn.Row(pn.Column(title, subtitle))

        # Error and status indicators initialization
        errorRow = pn.Row(
            self._interactivityManager.exceptionCommWidget,
        )

        statusRow = pn.Row(
            self._interactivityManager.statusIndicatorWidget,
        )

        widgetBox = self.getWidgetBox()

        try:

            rasterPlot = pn.bind(
                self.generateRasterLayer,
                varOpt=self._interactivityManager.rasterVariableSelectWidget,
                timeOpt=self._interactivityManager.rasterTimeSelectWidget
            )

        except Exception as exceptionCaptured:
            step = 'Initial Generation of the raster plot'

            self.excptionHandler(exceptionCaptured, step)
            # show empty map
            rasterPlot = self.getBaseMap()

        self.setWatchers()

        rasterRow = pn.Row(rasterPlot, min_height=400,)

        lowerRow = pn.Row(widgetBox, rasterRow)
        dashboard = pn.Column(titleRow,
                              errorRow,
                              statusRow,
                              lowerRow,
                              background='WhiteSmoke'
                              )

        return dashboard
