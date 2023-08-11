from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class Data:
    default: List[str] = field(default_factory=lambda: [])
    datasets: List[str] = field(default_factory=lambda: [])


#@dataclass
#class Datasets:
#    datasets: List[Dict[str, str, List[str]]] = field(
#        default_factory=lambda: [{'name': 'merra',
#                                  'path': '/path/to/merra',
#                                  'subdatasets': ['subdataset1', 'subdataset2']}])


@dataclass
class Title:
    title: str = 'Base Dashboard'
    subtitle: str = 'A general EIS dashboard'


@dataclass
class Config:
    """
    SWOT Dashboard data configuration class (embedded with OmegaConf).
    """

    data: Data = field(default_factory=Data)

    title: Title = field(default_factory=Title)
