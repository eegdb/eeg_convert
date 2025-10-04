import numpy as np

from eeg_reader import EEGReader
from eeg_writer import EEGWriter


def convert(source, target, low=None, high=None, notch=None):
    reader = EEGReader(source)
    signals = reader.signals
    writer = EEGWriter(target, signals)
    signal_last_read = {}
    for channel in signals:
        signal_last_read[channel] = 0
    duration = reader.duration
    batch = 300
    for i in range(0, int(duration), batch):

        batch_data = []
        for channel in signals:
            sample_rate = signals[channel]
            # read 5min
            length = sample_rate * batch
            data = reader.read(channel, signal_last_read[channel], length)
            data = reader.filter(channel, data, low, high, notch)
            # print(f"read{channel},{len(data)}")
            batch_data.append(data)
            signal_last_read[channel] = signal_last_read[channel] + length

        for j in range(batch + 1):
            write_data = []
            ch_index = 0
            for channel in signals:
                sample_rate = signals[channel]
                ch_data = batch_data[ch_index]
                if j * sample_rate + sample_rate > len(ch_data):
                    break
                write_data.append(ch_data[j * sample_rate:j * sample_rate + sample_rate])
                ch_index = ch_index + 1
            if len(write_data) == 0:
                break
            writer.write_samples(write_data)
    writer.closed()


if __name__ == '__main__':
    source_path = "C:\\Users\yimin\Downloads\MonkeySignalContrast\MonkeySignalContrast\data.edf"
    target_path = "C:\\Users\yimin\Downloads\MonkeySignalContrast\MonkeySignalContrast\data2.edf"
    convert(source_path, target_path, 45, 0.3, None)
