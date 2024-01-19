import unittest

from eisdashboard.model.config import Config, Data
from eisdashboard.model.config import Collections, Title
from eisdashboard.model.config import TimeBounds, CustomCollections


class TestConfig(unittest.TestCase):

    def test_default_values(self):
        config = Config()
        self.assertEqual(config.log_level, 'INFO')
        self.assertEqual(config.log_dir, '')
        self.assertEqual(config.data, Data())
        self.assertEqual(config.title, Title())
        self.assertEqual(config.nasa_earthdata_collections, Collections())
        self.assertEqual(config.custom_collections, CustomCollections())
        self.assertEqual(config.bounds, [])
        self.assertEqual(config.time_bounds, TimeBounds())

    def test_custom_values(self):
        data = Data(default=['value1'], datasets=['value2'])
        title = Title(title='Custom Title', subtitle='Custom Subtitle')
        nasa_earthdata_collections = Collections(ids=['id1', 'id2'])
        custom_collections = CustomCollections(ids={'id1': 'path1'})
        time_bounds = TimeBounds(start='2022-01-01', end='2023-01-01')
        config = Config(
            data=data,
            title=title,
            nasa_earthdata_collections=nasa_earthdata_collections,
            custom_collections=custom_collections,
            bounds=[[1, 2], [3, 4]],
            time_bounds=time_bounds,
            log_level='DEBUG',
            log_dir='/path/to/logs'
        )

        self.assertEqual(config.log_level, 'DEBUG')
        self.assertEqual(config.log_dir, '/path/to/logs')
        self.assertEqual(config.data, data)
        self.assertEqual(config.title, title)
        self.assertEqual(config.nasa_earthdata_collections,
                         nasa_earthdata_collections)
        self.assertEqual(config.custom_collections, custom_collections)
        self.assertEqual(config.bounds, [[1, 2], [3, 4]])
        self.assertEqual(config.time_bounds, time_bounds)


if __name__ == '__main__':
    unittest.main()
