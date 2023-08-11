from swotdashboard.model.common import read_config
from swotdashboard.model.config import Config
from swotdashboard.model.interactivity import InteractivityManager

from ipyleaflet import Map, basemaps
import ipywidgets as widgets

import panel as pn
from ipyleaflet import Map, basemaps
from typing import Tuple

# ------------------------------------------------------------------------
# DashBoard
# Base class for SWOT EIS Dashboard
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

    # ------------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------------
    def __init__(self, config_file):

        self._conf = read_config(config_file)

        # Cols for dashboard
        self.timeSeriesColumn = pn.Column()

        self.mapColumn = pn.Column()

        self.gridBox = pn.GridBox()

        self._interactivityManager = InteractivityManager(self._conf)

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
            header_color=self.HEADER_COLOR,
            active_header_background_color=self.HEADER_ACTIVE_BG_COLOR)
        
        return layerAccordion

    # ------------------------------------------------------------------------
    # getMap
    # ------------------------------------------------------------------------
    def getBaseMap(self):

        base = Map(
            center=(37.6069, -120.8762),
            zoom=5,
            basemap=basemaps.Esri.WorldImagery,
            scroll_wheel_zoom=True,
            keyboard=True,
            layout=widgets.Layout(height='400px', width='800px'),
        )

        return base

    # ------------------------------------------------------------------------
    # updateTimeSeries
    # ------------------------------------------------------------------------
    def updateTimeSeries(self, event):
        timestepDisabledPreEvent = \
            self._interactivityManager.timeStepInputWidget.disabled
        self.timeSeriesColumn[0].loading = True
        self._interactivityManager.timeSeriesVariableWidget.disabled = True
        self._interactivityManager.timeStepInputWidget.disabled = True
        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled = True
        self.timeSeriesColumn[0] = self.generateTimeSeriesGrid(
            self._interactivityManager.timeSeriesVariableWidget.value,
            self._interactivityManager.timeAveragedSequentialRadioWidget.value,
            self._interactivityManager.timeStepInputWidget.value,
            self._interactivityManager.toggleCSVExportWidget.value,
            self.bufferInput.value)
        self._interactivityManager.timeSeriesVariableWidget.disabled = False
        self._interactivityManager.timeAveragedSequentialRadioWidget.disabled = False
        self._interactivityManager.timeStepInputWidget.disabled = timestepDisabledPreEvent
        self.timeSeriesColumn[0].loading = False

if __name__ == '__main__':
    dashboard = Dashboard(config_file='swot-dashboard/configs/test_config.yaml')
