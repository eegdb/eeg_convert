import mne.io
import numpy as np
import pyedflib
import os
from scipy import signal
from scipy.signal import lfilter
import util
from supports import Supports





class EEGReader:
    # k: ch_name  v: sample_rate
    signals = {}
    # k: ch_name  v:total_sample_count
    signal_total_samples = {}
    duration =None
    start_time = None
    source = None
    ext = None

    def __init__(self, path):
        if os.path.exists(path) is False:
            raise ValueError(f"{path} is not exist")
        self.ext = util.detect_format(path)
        valid = util.is_valid_enum_value(Supports, self.ext)
        if valid is False:
            raise ValueError(f"{self.ext} is not support")
        if self.ext == Supports.EDF.value or self.ext == Supports.BDF.value:
            self.source = pyedflib.EdfReader(path)
            self.duration = self.source.getFileDuration()
            signals_labels = self.source.getSignalLabels()
            for i in range(len(signals_labels)):
                self.signals[signals_labels[i]] = int(self.source.getSampleFrequency(i))
                self.signal_total_samples[signals_labels[i]] = self.source.samples_in_file(i)
            print(self.signals)
            self.start_time = self.source.getStartdatetime

    def read(self, ch_name, start_samples_index, length):
        if self.ext == Supports.EDF.value or self.ext == Supports.BDF.value:
            ch_index = self._get_ch_index(ch_name)
            if ch_index < 0:
                raise ValueError(f"chname:{ch_name} is not exist")
            total_samples = self.signal_total_samples[ch_name]
            if start_samples_index + length > total_samples:
                length = total_samples - start_samples_index
            return self.source.readSignal(ch_index, start=start_samples_index, n=length)

    def filter(self,ch_name, data, low=None, high=None, notch=None):
        sample_rate = self.signals[ch_name]
        if low is not None:
            if low < sample_rate / 2:
                data = np.tile(data, 2)
                low_b,low_a = self._butter(low, sample_rate, 'low')
                filtered = lfilter(low_b, low_a, data)
                half = filtered.size / 2
                data = filtered[int(half):]
        if high is not None:
            if high < sample_rate / 2:
                data = np.tile(data, 2)
                high_b, high_a = self._butter(high, sample_rate, 'high')
                filtered = lfilter(high_b, high_a, data)
                half = filtered.size / 2
                data = filtered[int(half):]
        if notch is not None:
            data = self._notch_filter(data, notch, sample_rate)
        # if isinstance(data, np.ndarray):  # 判断是否为 NumPy 数组
        #     return data.tolist()
        return data

    @staticmethod
    def _butter(cutoff, fs, btyte, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype=btyte, analog=False)
        return b, a

    @staticmethod
    def _notch_filter(exg_data, removed_notch_hz, freq):
        if removed_notch_hz < freq / 2:
            q_notch = 10  # Quality factor
            w0 = removed_notch_hz / (freq / 2)  # Normalized Frequency
            c, d = signal.iirnotch(w0, q_notch)
            filtered = signal.filtfilt(c, d, exg_data)  # the eeg data we want
            return filtered
        return exg_data

    def _get_ch_index(self, ch_name):
        try:
            keys_list = list(self.signals.keys())
            return keys_list.index(ch_name)
        except ValueError:
            return -1
