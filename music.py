# copied from http://stackoverflow.com/questions/2648151/python-frequency-detection

from datetime import datetime, timedelta
from Queue import Queue
import time
import wave

import numpy as np
import pyaudio

import lights

WIDTH = 2
RATE = 44100
CHUNK = 1024
window = np.blackman(CHUNK)

MIN_FREQUENCY = 60
MAX_FREQUENCY = 1800

last_change_time = datetime.now()
frequencies_queue = Queue()

def main():
    p = pyaudio.PyAudio()

    device_info = p.get_device_info_by_index(2)
    channels = int(device_info['maxInputChannels'])

    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=channels,
                    rate=RATE,
                    input_device_index=2,
                    input=True,
                    stream_callback=callback)

    stream.start_stream()

    while stream.is_active():
        pass

    stream.stop_stream()
    stream.close()

    p.terminate()

def callback(in_data, frame_count, time_info, status):
    global last_change_time
    global frequencies_queue

    # unpack the data and times by the hamming window
    indata = np.array(wave.struct.unpack("%dh"%(len(in_data)/WIDTH), in_data))*window

    # Take the fft and square each value
    fftData = abs(np.fft.rfft(indata))**2

    # find the maximum
    which = fftData[1:].argmax() + 1

    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        frequency = (which+x1)*RATE/CHUNK
    else:
        frequency = which*RATE/CHUNK

    if frequency > MIN_FREQUENCY and frequency < MAX_FREQUENCY:
        frequencies_queue.put(frequency)
        bri = 235
        sat = 254
        time_now = datetime.now()
        if time_now >= last_change_time + timedelta(seconds=0.3):
            frequencies = []
            while not frequencies_queue.empty():
                frequencies.append(frequencies_queue.get())

            current_min = min(frequencies)
            current_max = max(frequencies)
            try:
                frequencies.remove(current_min)
                frequencies.remove(current_max)
            except ValueError:
                pass

            if frequencies:
                current_avg = sum(frequencies) / float(len(frequencies))

                hue = int((current_avg - MIN_FREQUENCY) / float(MAX_FREQUENCY) * 65535)
                print 'Frequency:', current_avg, 'Hue:', hue

                lights.change_hue_single(hue)
            last_change_time = time_now

    return (in_data, pyaudio.paContinue)

if __name__ == '__main__':
    main()
