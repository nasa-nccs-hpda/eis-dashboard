from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class CustomCollections:
    ids: Dict[str, str] = field(default_factory=lambda: {})


@dataclass
class Data:
    default: List[str] = field(default_factory=lambda: [])
    datasets: List[str] = field(default_factory=lambda: [])


@dataclass
class Collections:
    ids: List[str] = field(default_factory=lambda: [])


@dataclass
class Title:
    title: str = 'Base Dashboard'
    subtitle: str = 'A general EIS dashboard'


@dataclass
class TimeBounds:
    start: str = ''
    end: str = ''


@dataclass
class Config:
    """
    SWOT Dashboard data configuration class (embedded with OmegaConf).
    """

    data: Data = field(default_factory=Data)

    title: Title = field(default_factory=Title)

    nasa_earthdata_collections: Collections = \
        field(default_factory=Collections)

    custom_collections: CustomCollections = \
        field(default_factory=CustomCollections)

    bounds: List[list] = field(default_factory=lambda: [])

    time_bounds: TimeBounds = field(default_factory=TimeBounds)

    log_level: str = 'INFO'

    log_dir: str = ''


if __name__ == '__main__':

    from eisdashboard.model.common import read_config

    config_path: str = 'configs/dev_configs/test_no_nasaed.yaml'  # dev_configs/test_custom_config.yaml'

    config = read_config(config_path)

    print(config.custom_collections)

    print(config.nasa_earthdata_collections)
    print(bool(config.nasa_earthdata_collections['ids']))
