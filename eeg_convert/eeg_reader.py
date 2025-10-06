from mne import io
import numpy as np
import pyedflib
import os
from scipy import signal
from scipy.signal import lfilter
import eeg_convert as convert

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
        self.ext = convert.detect_format(path)
        valid = convert.is_valid_enum_value(convert.Supports, self.ext)
        if valid is False:
            raise ValueError(f"{self.ext} is not support")
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            self.source = pyedflib.EdfReader(path)
            self.duration = self.source.getFileDuration()
            signals_labels = self.source.getSignalLabels()
            for i in range(len(signals_labels)):
                self.signals[signals_labels[i]] = int(self.source.getSampleFrequency(i))
                self.signal_total_samples[signals_labels[i]] = self.source.samples_in_file(i)
            print(self.signals)
            self.start_time = self.source.getStartdatetime
        elif self.ext == convert.Supports.CDT.value:
            self.source = io.read_raw_curry(path)
            raw_info = self.source.info
            sfreq = raw_info['sfreq']
            for channel in raw_info.ch_names:
                self.signals[channel] = int(sfreq)
                self.signal_total_samples[channel] = self.source.n_times
            self.start_time = raw_info['meas_date']

    def read_by_time(self, start_time_second, duration_second):
        data = []
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            ch_names = self.signals.keys()
            for ch_name in ch_names:
                start_samples_index = start_time_second * self.signals[ch_name]
                length = duration_second * self.signals[ch_name]
                ch_data = self.read(ch_name, start_samples_index, length)
                data.append(ch_data)
        elif self.ext == convert.Supports.CDT.value:
            # sample_rate in CDT is all same
            chs = list(self.signals.keys())
            sample_rate = self.signals[chs[0]]
            start_samples_index = start_time_second * sample_rate
            end = start_samples_index + duration_second * sample_rate
            unit = {'eeg':'uV'}
            data = self.source.get_data(start=start_samples_index, stop=end, units=unit)
        return data

    def read(self, ch_name, start_samples_index, length):
        total_samples = self.signal_total_samples[ch_name]
        if start_samples_index + length > total_samples:
            length = total_samples - start_samples_index
        if self.ext == convert.Supports.EDF.value or self.ext == convert.Supports.BDF.value:
            ch_index = self._get_ch_index(ch_name)
            if ch_index < 0:
                raise ValueError(f"chname:{ch_name} is not exist")

            return self.source.readSignal(ch_index, start=start_samples_index, n=length).flatten(order='C')
        elif self.ext == convert.Supports.CDT.value:
            end = start_samples_index + length
            return self.source.get_data([ch_name], start_samples_index, end, units='uV').flatten(order='C')

    def filter2(self, data, sample_rate, low=None, high=None, notch=None):
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
        return data

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
            data = self._notch_filter(data, notch, sample_rate).flatten(order='C')
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
    def _notch_filter(data, removed_notch_hz, freq):
        if removed_notch_hz < freq / 2:
            q_notch = 10
            w0 = removed_notch_hz / (freq / 2)
            c, d = signal.iirnotch(w0, q_notch)
            filtered = signal.filtfilt(c, d, data)
            filtered = np.ascontiguousarray(filtered)
            return filtered
        return data

    def _get_ch_index(self, ch_name):
        try:
            keys_list = list(self.signals.keys())
            return keys_list.index(ch_name)
        except ValueError:
            return -1
