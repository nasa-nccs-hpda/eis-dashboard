import unittest
import argparse
from datetime import datetime
import omegaconf

from eisdashboard.model.common import read_config, valid_date


class TestCommon(unittest.TestCase):

    def setUp(self):
        # Create a temporary config file for testing
        self.temp_config_file = 'configs/dev_configs/test_config_both.yaml'

    def test_read_config(self):
        # Test read_config function
        config = read_config(self.temp_config_file)
        self.assertIsInstance(config, omegaconf.dictconfig.DictConfig)
        self.assertEqual(config.bounds, [[-76.6, 38.8, -76.5, 38.9]])

    def test_valid_date(self):
        # Test valid_date function with a valid date string
        date_str = "2023-12-28"
        valid_date_obj = valid_date(date_str)
        self.assertIsInstance(valid_date_obj, datetime)

        # Test valid_date function with an invalid date string
        invalid_date_str = "invalid_date"
        with self.assertRaises(argparse.ArgumentTypeError):
            valid_date(invalid_date_str)


if __name__ == '__main__':
    unittest.main()
