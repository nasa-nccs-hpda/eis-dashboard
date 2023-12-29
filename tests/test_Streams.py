import unittest

from eisdashboard.model.streams import PolygonDrawStream, ClickStream


class TestPolygonDrawStream(unittest.TestCase):

    def test_default_polygon_value(self):
        stream = PolygonDrawStream()
        self.assertEqual(
            stream.polygon,
            {
                "coordinates": [
                    [
                        [-110.390625, 39.878267],
                        [-88.242187, 40.682859],
                        [-85.078125, -7.403143],
                        [-119.179688, 2.06791],
                        [-110.390625, 39.878267],
                    ]
                ]
            },
        )

    def test_custom_polygon_value(self):
        custom_polygon = {"coordinates": [[[0, 0], [1, 1], [2, 2], [0, 0]]]}
        stream = PolygonDrawStream(polygon=custom_polygon)
        self.assertEqual(stream.polygon, custom_polygon)


class TestClickStream(unittest.TestCase):

    def test_default_lat_value(self):
        stream = ClickStream()
        self.assertEqual(stream.lat, 0)

    def test_default_lon_value(self):
        stream = ClickStream()
        self.assertEqual(stream.lon, 0)

    def test_custom_lat_lon_values(self):
        custom_lat = 45
        custom_lon = -90
        stream = ClickStream(lat=custom_lat, lon=custom_lon)
        self.assertEqual(stream.lat, custom_lat)
        self.assertEqual(stream.lon, custom_lon)


if __name__ == "__main__":
    unittest.main()
