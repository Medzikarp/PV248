import sys
import wave
import numpy as np
import struct
import itertools
import math

tones = ['a', 'bes', 'b', 'c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis']

def sliding_window(seq, n, step, fill=None, keep=0):
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result
    while True:
        elem = tuple( next(it, fill) for _ in range(step))
        result = result[step:] + elem
        if elem[-1] is fill:
            if keep:
                yield result
            break
        yield result


def freq2tone(a_reference, frequency):
    steps = math.log((frequency / a_reference), math.pow(2, (1/12)))
    up = steps >= 0
    steps = np.abs(steps)
    octave = int(steps // 12)
    tone = int(steps % 12)
    cents = float((steps - tone) % 12)
    cents = int(cents * 100)
    if cents > 50:
        cents = cents - 100
        tone = tone + 1
        if tone > 11:
            tone = tone % 12
            octave += 1

    if up:
        if tone > 2:
            tone = tone - 12
            octave += 1
    else:
        if tone > 9:
            tone = tone - 12
            octave += 1
        cents = -cents
        tone = -tone
        octave = -octave
    tone_label = tones[tone]

    if octave < -1:
        tone_label = tone_label.capitalize()
    while octave < -2:
        tone_label = tone_label + ','
        octave += 1
    while octave > -1:
        tone_label = tone_label + '’'
        octave -= 1
    cents_string = str(cents)
    if cents >= 0:
        cents_string = '+' + cents_string
    return tone_label + cents_string


def equal_segments(segment1, segment2):
    if len(segment1) != len(segment2):
        return False
    segment1 = sorted(segment1)
    segment2 = sorted(segment2)
    for idx,val in enumerate(segment1):
        if segment1[idx] != segment2[idx]:
            return False
    return True


def print_segment(peaks, start, end, a1):
    if len(peaks) > 0:
        if start < 10.0:
            print(str(0), end='')
        print('%.2f' % start, '-', end='', sep='')
        if end < 10.0:
            print(str(0), end='')
        print('%.2f' % end, end=' ')
        for p in sorted(peaks):
            print(freq2tone(int(a1), p), end=' ')
        print()


a1_freq = sys.argv[1]
waveFile = wave.open(sys.argv[2], 'r')
frames_number = waveFile.getnframes()
channels_number = waveFile.getnchannels()
frame_rate = waveFile.getframerate()
cluster_difference = 0.1


frames = waveFile.readframes(frames_number)

window_time = 1
window_size = int(window_time * frame_rate)
window_shift_time = 0.1
window_shift = int(window_shift_time * frame_rate)

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

maxs_in_windows = []
for window in sliding_window(samples, window_size, window_shift):
    highest_peaks = []
    if len(window) < window_size:
        break
    amplitudes = np.abs(np.fft.rfft(window))
    mean = np.mean(amplitudes)
    sorted_by_amplitudes = np.argsort(amplitudes)[::-1]

    for max in sorted_by_amplitudes:
        add_peak = True
        if len(highest_peaks) == 3 or amplitudes[max] < 20*mean:
            break
        for peak in highest_peaks:
            if np.abs(max - peak) <= 1:
                add_peak = False
        if add_peak:
            highest_peaks.append(max)
    maxs_in_windows.append(highest_peaks)

    '''highest_peaks = np.argpartition(amplitudes, -3)[-3:].tolist()'''

i = 0
j = 1
while (i < len(maxs_in_windows) and j < len(maxs_in_windows)):
    while (j < len(maxs_in_windows) and equal_segments(maxs_in_windows[i], maxs_in_windows[j])):
        j = j + 1
    print_segment(maxs_in_windows[i], i*0.1, j*0.1, a1_freq)
    i = j
