import unittest
from unittest.mock import patch, MagicMock
import requests

import xarray as xr
import numpy as np
import pandas as pd

from eisdashboard.model.data.ingest import Ingest


class TestIngest(unittest.TestCase):

    def setUp(self):
        # Initialize the Ingest object with a mock config
        self.config = MagicMock()
        self.ingest = Ingest(self.config)

    @patch('requests.get')
    def test_get_temp_credentials_success(self, mock_requests_get):
        # Mock the successful response from the S3 credentials endpoint
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'accessKeyId': 'mock_access_key',
            'secretAccessKey': 'mock_secret_key',
            'sessionToken': 'mock_session_token'
        }
        mock_requests_get.return_value = mock_response

        # Call the _get_temp_credentials method
        credentials = self.ingest._get_temp_credentials('GES_DISC')

        # Assert that the method returns the expected credentials
        self.assertEqual(credentials['accessKeyId'], 'mock_access_key')
        self.assertEqual(credentials['secretAccessKey'], 'mock_secret_key')
        self.assertEqual(credentials['sessionToken'], 'mock_session_token')

    @patch('requests.get',
           side_effect=requests.exceptions.RequestException('Mock error'))
    def test_get_temp_credentials_failure(self, mock_requests_get):
        # Mock an exception when making a request to the S3 credentials
        # endpoint
        result = self.ingest._get_temp_credentials('GES_DISC')

        self.assertEqual(result, (0, None))

    @patch('s3fs.S3FileSystem')
    @patch('xarray.open_mfdataset')
    def test_ingest_success(self, mock_open_mfdataset, mock_s3fs):
        # Mock the successful retrieval of S3 credentials and opening of files
        mock_temp_creds = {
            'accessKeyId': 'mock_access_key',
            'secretAccessKey': 'mock_secret_key',
            'sessionToken': 'mock_session_token'
        }
        self.ingest._get_temp_credentials = \
            MagicMock(return_value=mock_temp_creds)

        # Mock the successful opening of S3 files
        mock_open_mfdataset.return_value = MagicMock()

        # Call the ingest method
        result = self.ingest.ingest('GES_DISC', ('s3://file1.nc',
                                                 's3://file2.nc'))

        # Assert that the method returns a valid result
        self.assertIsNotNone(result)

    @patch('s3fs.S3FileSystem')
    def test_ingest_failure(self, mock_s3fs):
        # Mock an exception when opening S3 files

        with self.assertRaises(ValueError):
            self.ingest.ingest('GES_DISC', ('s3://file1.nc',
                                            's3://file2.nc'))

    @patch('eisdashboard.model.cmr_query.CmrProcess')
    @patch('eisdashboard.model.data.ingest.Ingest.ingest')
    def test_get_data_from_bounds(self, mock_ingest, mock_cmr_process):
        # Mocking necessary objects
        mock_cmr_process.return_value.run.return_value = ([],
                                                          'mock_provider_id')
        mock_ingest.return_value = MagicMock()

        # Creating a mock configuration
        mock_config = MagicMock()

        # Creating an instance of Ingest
        ingest_instance = Ingest(mock_config)

        # Creating a mock query package
        mock_query_package = {
            'collection_id': 'mock_collection_id',
            'datetime': 'mock_datetime',
            'coords': [1.0, 2.0],
            'spatialParameter': 'mock_spatial_parameter'
        }

        # Calling the method to be tested
        result = ingest_instance.get_data_from_bounds(mock_query_package)

        self.assertEqual(result['key'], 'mock_collection_id')
        self.assertIsInstance(result['data'], MagicMock)
        self.assertIsInstance(result['variables'], list)

    def test_rename_dims(self):
        # dummy instance
        ingest = Ingest(self.config)

        # Create dummy data
        latitude = np.linspace(-90, 90, 3)
        longitude = np.linspace(-180, 180, 4)
        time = pd.date_range("2024-01-01", periods=5, freq="D")

        data = np.random.rand(len(time), len(latitude), len(longitude))

        dataset = xr.Dataset(
            {
                "temperature": (["Time", "Latitude", "Longitude"], data),
            },
            coords={
                "Latitude": latitude,
                "Longitude": longitude,
                "Time": time,
            },
        )

        result_dataset = ingest.rename_dims(dataset)

        expected_coords = ['time', 'lat', 'lon']
        expected_dims = ['time', 'lat', 'lon']

        self.assertTrue(list(result_dataset.coords.keys()) == expected_coords)
        self.assertTrue(list(result_dataset.dims.keys()) == expected_dims)

    def test_refine_urls(self):
        ingest = Ingest(self.config)

        # Test case 1: URLs with proper suffixes and prefixes
        urls_case1 = ['s3://example1.nc', 'http://archive.gov/example2.nc4',
                      's3://example3.hdf']
        expected_result_case1 = ('s3://example1.nc', 's3://example2.nc4',
                                 's3://example3.hdf')
        self.assertEqual(ingest._refine_urls(urls_case1),
                         expected_result_case1)

        # Test case 2: URLs with incorrect suffixes or prefixes
        urls_case2 = ['s3://example4.txt', 'ftp://example5.nc',
                      'http://archive.gov/example6.hdf.md5']
        expected_result_case2 = ()
        self.assertEqual(ingest._refine_urls(urls_case2),
                         expected_result_case2)

        # Test case 3: Empty list
        urls_case3 = []
        expected_result_case3 = ()
        self.assertEqual(ingest._refine_urls(urls_case3),
                         expected_result_case3)


if __name__ == '__main__':
    unittest.main()
