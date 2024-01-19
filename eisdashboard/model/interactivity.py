import panel as pn


# ------------------------------------------------------------------------
# Interactivity
# ------------------------------------------------------------------------
class InteractivityManager(object):

    RASTER_VAR_NAME: str = 'Variables'
    RASTER_TIME_NAME: str = 'Time'

    TIME_SERIES_NAME: str = 'Time Series Variables'
    TIME_AVE_SEQ_RADIO_NAME: str = 'Visualization Type'
    TIME_AVE_SEQ_RADIO_OPTS: list = ['Daily', 'Time Averaged']
    TIME_AVE_SEQ_RADIO_VAL: str = 'Daily'
    TIME_AVE_SEQ_RADIO_BUTTON_TYPE: str = 'success'

    TIME_STEP_INPUT_NAME: str = 'Time Step'
    TIME_STEP_INPUT_VALUE: str = '7D'

    TIME_AVE_CSV_TOGGLE_NAME: str = 'Export to time series to CSV'
    TIME_AVE_CSV_TOGGLE_BUTTON_TYPE: str = 'success'

    EXCEPTION_COMM_VAL: str = ''

    STATUS_INDICATOR_VAL: str = ''

    # ------------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------------
    def __init__(self, conf) -> None:

        self._conf = conf

        # Widgets
        self._rasterVariableSelectWidget = pn.widgets.Select(
            name=self.RASTER_VAR_NAME,
            value=[],
            options=[])

        self._rasterTimeSelectWidget = pn.widgets.Select(
            name=self.RASTER_TIME_NAME,
            value=[],
            options=[])

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

        self._exceptionCommWidget = pn.pane.Markdown(
            self.EXCEPTION_COMM_VAL,
            width=400)

        self._statusIndicatorWidget = pn.pane.Markdown(
            self.STATUS_INDICATOR_VAL,
            width=400)

        self._timeAveragedSequentialRadioWidget.link(
            self._timeStepInputWidget,
            callbacks={
                'value': self._timeAveragedCallBack})

    # ------------------------------------------------------------------------
    # rasterVariableSelectWidget
    # ------------------------------------------------------------------------
    @property
    def rasterVariableSelectWidget(self):
        return self._rasterVariableSelectWidget

    # ------------------------------------------------------------------------
    # rasterTimeSelectWidget
    # ------------------------------------------------------------------------
    @property
    def rasterTimeSelectWidget(self):
        return self._rasterTimeSelectWidget

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
    # exceptionCommWidget
    # ------------------------------------------------------------------------
    @property
    def exceptionCommWidget(self):
        return self._exceptionCommWidget

    # ------------------------------------------------------------------------
    # statusIndicatorWidget
    # ------------------------------------------------------------------------
    @property
    def statusIndicatorWidget(self):
        return self._statusIndicatorWidget

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
