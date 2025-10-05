import eeg_convert
import argparse
def convert(source, target, low=None, high=None, notch=None):
    reader = eeg_convert.EEGReader(source)
    signals = reader.signals
    writer = eeg_convert.EEGWriter(target, signals)
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

def convert2(source, target, low=None, high=None, notch=None):
    reader = eeg_convert.EEGReader(source)
    signals = reader.signals
    writer = eeg_convert.EEGWriter(target, signals)
    signal_last_read = {}
    for channel in signals:
        signal_last_read[channel] = 0
    duration = reader.duration
    batch = 300
    for i in range(0, int(duration), batch):

        data = reader.read_by_time(i, batch)
        filtered = []
        ch_index = 0
        for channel in signals:
            ch_filtered = reader.filter2(data[ch_index], signals[channel], low, high, notch)
            filtered.append(ch_filtered)
            ch_index = ch_index + 1
        for j in range(batch + 1):
            write_data = []
            ch_index = 0
            for channel in signals:
                sample_rate = signals[channel]
                ch_data = filtered[ch_index]
                if j * sample_rate + sample_rate > len(ch_data):
                    break
                write_data.append(ch_data[j * sample_rate:j * sample_rate + sample_rate])
                ch_index = ch_index + 1
            if len(write_data) == 0:
                break
            writer.write_samples(write_data)
    writer.closed()

def main():
    p = argparse.ArgumentParser(description="EEG Convert")
    p.add_argument('-i', '--in', dest='infile', required=True,
                   help='Curry/EDF/BDF/SET/MAT')
    p.add_argument('-o', '--out', dest='outfile', required=True, help='EDF/BDF/SET/MAT')
    p.add_argument('-low_pass', help='low_pass_filter(butterworth)')
    p.add_argument('--high_pass', help='high_pass_filter(butterworth)')
    p.add_argument('--notch', help='notch')
    args = p.parse_args()

    infile = args.infile
    outfile = args.outfile
    low = args.low_pass
    high = args.high_pass
    notch = args.notch
    convert2(infile, outfile, low, high, notch)
    print("success")

if __name__ == '__main__':
    main()
