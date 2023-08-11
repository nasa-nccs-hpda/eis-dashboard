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

    def __init__(self, conf) -> None:

        self._conf = conf

        default_datasets = list(self._conf.data.default)
        additional_datasets = list(self._conf.data.datasets)

        # Widgets
        self._layerSelectionWidget = pn.widgets.RadioButtonGroup(
            name=self.BASEMAP_NAME,
            options=self.BASEMAP_OPTS,
            value=self.BASEMAP_DEFAULT,
            button_type=self.BASEMAP_BUTTON_TYPE)

        self._timeSeriesVariablesWidget = pn.widgets.MultiChoice(
            name=self.TIME_SERIES_NAME,
            value=default_datasets,
            options=additional_datasets)

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

        self._timeAveragedSequentialRadioWidget.link(
            self._timeStepInputWidget,
            callbacks={
                'value': self._timeAveragedCallBack})

    @property
    def layerSelection(self):
        return self._layerSelectionWidget

    @property
    def timeSeriesVariableWidget(self):
        return self._timeSeriesVariablesWidget

    @property
    def timeAveragedSequentialRadioWidget(self):
        return self._timeAveragedSequentialRadioWidget

    @property
    def timeStepInputWidget(self):
        return self._timeStepInputWidget

    @property
    def toggleCSVExportWidget(self):
        return self._toggleCSVExportWidget

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
