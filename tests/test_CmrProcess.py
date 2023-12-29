import unittest
from unittest.mock import MagicMock, patch
from eisdashboard.model.cmr_query import CmrProcess


class TestCmrProcess(unittest.TestCase):
    def setUp(self):
        # Create an instance of CmrProcess with required parameters
        self.cmr_process = CmrProcess(mission="your_mission",
                                      dateTime="2023-01-01")

    @patch("urllib3.PoolManager")
    def test_run_with_error(self, mock_pool_manager):
        # Mock the _cmrQuery method to return an error
        self.cmr_process._cmrQuery = MagicMock(return_value=(None, True))

        # Run the method under test
        result = self.cmr_process.run()

        # Assert the expected results
        self.assertEqual(result, [])

    def test_build_request(self):
        # Test the _buildRequest method
        result = self.cmr_process._buildRequest(pageNum=2)

        # Assert the expected results
        expected = {
            "page_num": 2,
            "page_size": 150,
            "short_name": "your_mission",
            "bounding_box": None,
            "day_night_flag": "",
            "temporal": "2023-01-01",
            "online_only": "true",
        }
        self.assertEqual(result, expected)

    @patch("urllib3.PoolManager")
    def test_send_request_success(self, mock_pool_manager):
        # Mock the request to return sample data
        mock_pool_manager.return_value.request.return_value.status = 200
        mock_pool_manager.return_value.request.return_value.data = (
            '{"items": []}'.encode("utf-8")
        )

        # Test the _sendRequest method
        result = self.cmr_process._sendRequest(
            requestDictionary={"param": "value"})

        # Assert the expected results
        self.assertEqual(result, (0, None))

    @patch("urllib3.PoolManager")
    def test_send_request_error(self, mock_pool_manager):
        # Mock the request to return an error status
        mock_pool_manager.return_value.request.return_value.status = 400

        # Test the _sendRequest method
        result = self.cmr_process._sendRequest(
            requestDictionary={"param": "value"})

        # Assert the expected results
        self.assertEqual(result, (0, None))

    def test_process_request(self):
        # Test the _processRequest method
        sample_data = {
            "items": [
                {
                    "meta": {"provider-id": "provider1"},
                    "umm": {
                        "RelatedUrls": [{"URL": "url1"}, {"URL": "url2"}],
                        "TemporalExtent": {"RangeDateTime": "temporal_range1"},
                        "DataGranule": {"DayNightFlag": "day_night1"},
                        "SpatialExtent": {"HorizontalSpatialDomain":
                                          "spatial_extent1"},
                    },
                }
            ]
        }
        result = self.cmr_process._processRequest(sample_data)
        # Assert the expected results
        expected = {
            "url1": {
                "file_name": "url1",
                "file_url": "url2",
                "provider_id": "provider1",
                "temporal_range": "temporal_range1",
                "spatial_extent": "spatial_extent1",
                "day_night_flag": "day_night1",
            }
        }
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
