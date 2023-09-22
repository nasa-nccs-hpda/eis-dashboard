import datetime
from typing import Tuple

import panel as pn


# ------------------------------------------------------------------------
# Interactivity
# ------------------------------------------------------------------------
class InteractivityManager(object):

    BASEMAP_NAME: str = 'Base map layer'
    BASEMAP_OPTS: list = ['OSM', 'ESRI']
    BASEMAP_DEFAULT: str = 'ESRI'
    BASEMAP_BUTTON_TYPE: str = 'success'

    TIME_SERIES_NAME: str = 'Time Series Variables'
    TIME_AVE_SEQ_RADIO_NAME: str = 'Visualization Type'
    TIME_AVE_SEQ_RADIO_OPTS: list = ['Daily', 'Time Averaged']
    TIME_AVE_SEQ_RADIO_VAL: str = 'Daily'
    TIME_AVE_SEQ_RADIO_BUTTON_TYPE: str = 'success'

    TIME_STEP_INPUT_NAME: str = 'Time Step'
    TIME_STEP_INPUT_VALUE: str = '7D'

    TIME_AVE_CSV_TOGGLE_NAME: str = 'Export to time series to CSV'
    TIME_AVE_CSV_TOGGLE_BUTTON_TYPE: str = 'success'

    EXCEPTION_COMM_NAME: str = ''
    EXCEPTION_COMM_VAL: str = ''

    DATE_TIME_RANGE_PICKER_NAME: str = 'Date-Time Range'
    DATE_TIME_RANGE_PICKER_DEF_VALUE: \
        Tuple[datetime.datetime, datetime.datetime] = (
            datetime.datetime(2023, 3, 1, 0, 0),
            datetime.datetime(2023, 3, 31, 12, 59)
        )

    # ------------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------------
    def __init__(self, conf) -> None:

        self._conf = conf

        # Widgets
        self._layerSelectionWidget = pn.widgets.RadioButtonGroup(
            name=self.BASEMAP_NAME,
            options=self.BASEMAP_OPTS,
            value=self.BASEMAP_DEFAULT,
            button_type=self.BASEMAP_BUTTON_TYPE)

        self._timeSeriesVariablesWidget = pn.widgets.MultiChoice(
            name=self.TIME_SERIES_NAME,
            value=[],
            options=[])

        self._timeAveragedSequentialRadioWidget = \
            pn.widgets.RadioButtonGroup(
                name=self.TIME_AVE_SEQ_RADIO_NAME,
                options=self.TIME_AVE_SEQ_RADIO_OPTS,
                value=self.TIME_AVE_SEQ_RADIO_VAL,
                button_type=self.TIME_AVE_SEQ_RADIO_BUTTON_TYPE)

        self._timeStepInputWidget = pn.widgets.TextInput(
            name=self.TIME_STEP_INPUT_NAME,
            value=self.TIME_STEP_INPUT_VALUE,
            disabled=False)

        self._timeStepInputWidget = pn.widgets.TextInput(
            name=self.TIME_STEP_INPUT_NAME,
            value=self.TIME_STEP_INPUT_VALUE,
            disabled=True)

        self._toggleCSVExportWidget = pn.widgets.Button(
            name=self.TIME_AVE_CSV_TOGGLE_NAME,
            button_type=self.TIME_AVE_CSV_TOGGLE_BUTTON_TYPE)

        self._dateTimeRangeWidget = pn.widgets.DatetimeRangePicker(
            name=self.DATE_TIME_RANGE_PICKER_NAME,
            value=self.DATE_TIME_RANGE_PICKER_DEF_VALUE,
        )

        self._exceptionCommWidget = pn.pane.Markdown(
            self.EXCEPTION_COMM_VAL,
            width=400)

        self._timeAveragedSequentialRadioWidget.link(
            self._timeStepInputWidget,
            callbacks={
                'value': self._timeAveragedCallBack})

    # ------------------------------------------------------------------------
    # layerSelection
    # ------------------------------------------------------------------------
    @property
    def layerSelection(self):
        return self._layerSelectionWidget

    # ------------------------------------------------------------------------
    # timeSeriesVariableWidget
    # ------------------------------------------------------------------------
    @property
    def timeSeriesVariableWidget(self):
        return self._timeSeriesVariablesWidget

    # ------------------------------------------------------------------------
    # timeAveragedSequentialRadioWidget
    # ------------------------------------------------------------------------
    @property
    def timeAveragedSequentialRadioWidget(self):
        return self._timeAveragedSequentialRadioWidget

    # ------------------------------------------------------------------------
    # timeStepInputWidget
    # ------------------------------------------------------------------------
    @property
    def timeStepInputWidget(self):
        return self._timeStepInputWidget

    # ------------------------------------------------------------------------
    # toggleCSVExportWidget
    # ------------------------------------------------------------------------
    @property
    def toggleCSVExportWidget(self):
        return self._toggleCSVExportWidget

    # ------------------------------------------------------------------------
    # dateTimeRangeWidget
    # ------------------------------------------------------------------------
    @property
    def dateTimeRangeWidget(self):
        return self._dateTimeRangeWidget

    # ------------------------------------------------------------------------
    # dateTimeRangeWidget
    # ------------------------------------------------------------------------
    @property
    def exceptionCommWidget(self):
        return self._exceptionCommWidget

    # ------------------------------------------------------------------------
    # timeAveragedCallBack
    # ------------------------------------------------------------------------
    @staticmethod
    def _timeAveragedCallBack(target, event):
        """Callback to enable time-averaged related widgets"""
        target.disabled = False if event.new == 'Time Averaged' else True

    # ------------------------------------------------------------------------
    # sequentialDisable
    # ------------------------------------------------------------------------
    @staticmethod
    def _sequentialDisable(target, event):
        """Callback to disable time-averaged related widgets"""
        target.disabled = True if event.new == 'Time Averaged' else False


if __name__ == '__main__':

    from swotdashboard.model.dashboard import Dashboard

    dashboard = Dashboard(
        config_file='swot-dashboard/configs/test_config.yaml')
    conf = dashboard._conf
    im = InteractivityManager(conf=conf)
