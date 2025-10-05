import os
import pyedflib
import eeg_convert as convert

class EEGWriter:

    # k: ch_name  v: sample_rate
    signals = {}
    ext = None
    target = None

    def __init__(self, path, ch_dict):
        if os.path.exists(path):
            raise ValueError(f"{path} is exist")
        self.ext = convert.detect_format(path)
        valid = convert.is_valid_enum_value(convert.Supports, self.ext)
        if valid is False:
            raise ValueError(f"{self.ext} is not support")
        if self.ext == convert.Supports.CDT:
            raise ValueError(f"{self.ext} is not support export")
        self.signals = ch_dict
        ch_length = len(ch_dict)
        if self.ext == convert.Supports.BDF.value:
            self.target = pyedflib.EdfWriter(path, ch_length,
                               file_type=pyedflib.FILETYPE_BDFPLUS)
            self._write_edf_header()
        elif self.ext == convert.Supports.EDF.value:
            self.target = pyedflib.EdfWriter(path, ch_length,
                                   file_type=pyedflib.FILETYPE_EDFPLUS)
            self._write_edf_header()



    def _write_edf_header(self):
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            channel_infos = []
            for channel in self.signals:
                ch_info = {'label': channel, 'dimension': 'uV', 'sample_frequency': self.signals[channel], 'physical_max': 32767, 'physical_min': -32767, 'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
                channel_infos.append(ch_info)
            self.target.setSignalHeaders(channel_infos)



    def write_samples(self, data):
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            if len(data) != len(self.signals):
                raise ValueError(f"{len(data)} is not signal len")
            self.target.writeSamples(data)

    def closed(self):
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            self.target.close()
            del self.target