import wave
import sys
import numpy as np
import struct

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


waveFile = wave.open(sys.argv[1], 'r')
frames_number = waveFile.getnframes()
channels_number = waveFile.getnchannels()
frame_rate = waveFile.getframerate()


frames = waveFile.readframes(frames_number)

window_time = 1
window_size = int(window_time * frame_rate)

samples = []
samples_iterator = struct.iter_unpack('h', frames)
if channels_number == 2:
    for number in samples_iterator:
        sample_ch1 = number[0]
        sample_ch2 = next(samples_iterator)[0]
        samples.append((sample_ch1 + sample_ch2) / 2)
if channels_number == 1:
    for number in samples_iterator:
        samples.append(number[0])

lowest = np.inf
highest = -np.inf

for window in chunker(samples, window_size):
    if len(window) < window_size:
        break
    amplitude = np.abs(np.fft.rfft(window))
    mean = np.mean(amplitude)
    peaks = np.argwhere(amplitude >= 20*mean)
    if len(peaks) > 0:
        if peaks.min() < lowest:
            lowest = peaks.min()
        if peaks.max() > highest:
            highest = peaks.max()

if np.isfinite(lowest) and np.isfinite(highest):
    print("low: " + str(lowest) + " high: " + str(highest))
else:
    print("no peaks")
