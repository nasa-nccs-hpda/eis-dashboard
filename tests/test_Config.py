import unittest

from eisdashboard.model.config import Config, Data
from eisdashboard.model.config import Collections, Title, TimeBounds

class TestConfig(unittest.TestCase):

    def test_default_values(self):
        config = Config()
        self.assertEqual(config.log_level, 'INFO')
        self.assertEqual(config.log_dir, '')
        self.assertEqual(config.data, Data())
        self.assertEqual(config.title, Title())
        self.assertEqual(config.collections, Collections())
        self.assertEqual(config.bounds, [])
        self.assertEqual(config.time_bounds, TimeBounds())

    def test_custom_values(self):
        data = Data(default=['value1'], datasets=['value2'])
        title = Title(title='Custom Title', subtitle='Custom Subtitle')
        collections = Collections(ids=['id1', 'id2'])
        time_bounds = TimeBounds(start='2022-01-01', end='2023-01-01')

        config = Config(
            data=data,
            title=title,
            collections=collections,
            bounds=[[1, 2], [3, 4]],
            time_bounds=time_bounds,
            log_level='DEBUG',
            log_dir='/path/to/logs'
        )

        self.assertEqual(config.log_level, 'DEBUG')
        self.assertEqual(config.log_dir, '/path/to/logs')
        self.assertEqual(config.data, data)
        self.assertEqual(config.title, title)
        self.assertEqual(config.collections, collections)
        self.assertEqual(config.bounds, [[1, 2], [3, 4]])
        self.assertEqual(config.time_bounds, time_bounds)

if __name__ == '__main__':
    unittest.main()