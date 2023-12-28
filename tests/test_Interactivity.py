import unittest
from unittest.mock import MagicMock

import panel as pn

from eisdashboard.model.interactivity import InteractivityManager
from eisdashboard.model.common import read_config


class TestInteractivityManager(unittest.TestCase):

    def setUp(self):
        # Mocking the Dashboard class for testing purposes
        self.dashboard_mock = MagicMock()
        self.dashboard_mock._conf = {'your_config_key': 'your_config_value'}
        self._conf = read_config('configs/example_config.yaml')

    def test_init(self):
        # Test if the initialization of InteractivityManager
        # works without errors
        im = InteractivityManager(conf=self._conf)
        self.assertIsInstance(im, InteractivityManager)

    def test_properties(self):
        # Test the getter methods for various properties

        im = InteractivityManager(conf=self._conf)

        self.assertIsInstance(
            im.timeSeriesVariableWidget, pn.widgets.MultiChoice)
        self.assertIsInstance(
            im.timeAveragedSequentialRadioWidget, pn.widgets.RadioButtonGroup)
        self.assertIsInstance(
            im.timeStepInputWidget, pn.widgets.TextInput)
        self.assertIsInstance(
            im.toggleCSVExportWidget, pn.widgets.Button)
        self.assertIsInstance(
            im.exceptionCommWidget, pn.pane.Markdown)
        self.assertIsInstance(
            im.statusIndicatorWidget, pn.pane.Markdown)

    def test_timeAveragedCallBack(self):
        # Test the timeAveragedCallBack method

        im = InteractivityManager(conf=self._conf)

        # Mock the target and event for the callback
        target = im._timeStepInputWidget
        event_mock = MagicMock(new='Time Averaged')

        # Call the callback method
        InteractivityManager._timeAveragedCallBack(target, event_mock)

        # Check if the target's disabled property is set correctly
        self.assertFalse(target.disabled)

    def test_sequentialDisable(self):
        # Test the _sequentialDisable method

        im = InteractivityManager(conf=self._conf)

        # Mock the target and event for the callback
        target = im._toggleCSVExportWidget
        event_mock = MagicMock(new='Time Averaged')

        # Call the callback method
        InteractivityManager._sequentialDisable(target, event_mock)

        # Check if the target's disabled property is set correctly
        self.assertTrue(target.disabled)


if __name__ == '__main__':
    unittest.main()
