import eeg_convert.eeg_reader

path = 'C:\\Users\yimin\Downloads\MonkeySignalContrast\MonkeySignalContrast\data.edf'
# path = 'C:\\Users\yimin\Downloads\MonkeySignalContrast\MonkeySignalContrast\diff_freq_hz_2.cdt'
reader = eeg_convert.eeg_reader.EEGReader(path)
# data = reader.read('M1',0, 756)
data = reader.read_by_time(0,3)
data = reader.filter2(data, 45, low=None, high=None, notch=None)