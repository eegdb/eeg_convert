__version__ = "1.0.0"
__author__ = "eegdb@outlook.com"
__all__ = ['EEGReader', 'EEGWriter', 'detect_format', 'is_valid_enum_value','Supports']
from .eeg_reader import EEGReader
from .eeg_writer import EEGWriter
from .util import detect_format, is_valid_enum_value
from .supports import Supports